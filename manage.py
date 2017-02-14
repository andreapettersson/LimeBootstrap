#!/usr/bin/env python
from contextlib import contextmanager
import os.path
import shutil
import sys
import os
from os.path import join, dirname, abspath, normpath, exists
import subprocess as sp
import tempfile
from tempfile import gettempdir
import glob
from wheel.install import WheelFile
import getpass
import logging
import click


logger = logging.getLogger(__name__)
ROOT = os.path.abspath(os.path.dirname(__file__))


@click.group(context_settings={'help_option_names': ['--help', '-h']})
@click.option(
    '--loglevel', default='INFO',
    type=click.Choice(['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']))
def cli(loglevel):
    _setup_logger(loglevel)


@cli.command(help='Build package')
def build():
    activate_local_node()
    rm_rf('build')
    rm_rf('dist')
    sp.check_call(['python', 'setup.py', '-q', 'bdist_wheel'])


def script_dir():
    return dirname(abspath(__file__))


frontend_dir = join(script_dir(), 'frontend')
vendor_dir = join(frontend_dir, 'tools', 'vendor')
node_dir = join(vendor_dir, 'nodejs')


@cli.group(help='Run tests', invoke_without_command=True)
@click.option('--reporter', help='How the result should be reported')
@click.option('--ci/--no-ci', default=False, help='Run as CI, more browsers')
@click.pass_context
def test(ctx, reporter=None, ci=None):
    if ctx.invoked_subcommand is None:
        ctx.invoke(test_python)
        ctx.invoke(test_js, reporter=reporter, ci=ci)


@test.group(name='python', help='Run python tests',
            invoke_without_command=True)
@click.pass_context
def test_python(ctx):
    if ctx.invoked_subcommand is None:
        ctx.invoke(flake)
        ctx.invoke(test_python_unit)


@test_python.command(name='unit', help="Run python unit tests")
def test_python_unit():
    retval1 = sp.call('nosetests')
    retval2 = sp.call('py.test', shell=True)
    # return value 5 is "not tests run" in pytest. This is not a error.
    retval2 = 0 if retval2 == 5 else retval2
    if sum([retval1, retval2]) != 0:
        raise RuntimeError('tests failed')


@test.command(name='js', help='Run js tests')
@click.option('--reporter', help='How the result should be reported')
@click.option('--ci/--no-ci', default=False, help='Run as CI, more browsers')
def test_js(reporter=None, ci=None):
    activate_local_node()
    with cd(frontend_dir):
        cmd = ['gulp.cmd', 'test']
        if reporter:
            cmd.append('--reporter={}'.format(reporter))
        if ci:
            cmd.append('--ci')

        call(cmd)


@test_python.command(name='coverage',
                     help="Run unit tests and get a coverage report")
def test_coverage():
    rm('.coverage')
    rm_rf('.htmlcov')
    sp.check_call(['coverage', 'run', '--branch',
                   'setup.py', '-q', 'nosetests'])
    sp.call(['py.test', '--cov-append',  '--branch',  '--cov=.coverage'],
            shell=True)
    sp.check_call('coverage report -m'.split())
    sp.check_call('coverage html -d .htmlcov -i'.split())
    browse_to('.htmlcov/index.html')


@test_python.command(help="Check for PEP8 violations")
def flake():
    sp.check_call(['flake8', abspath(dirname(__file__))])


@cli.group(help='Documentation helpers')
def docs():
    pass


@docs.command(name='generate', help="Generate documentation")
def docs_generate():
    rm('docs/lime_webclient.rst')
    rm('docs/modules.rst')
    sp.call(['sphinx-apidoc', '-o', 'docs', 'lime_webclient'])
    sp.check_call(['sphinx-build', '-q', '-b', 'html', 'docs',
                   'docs/_build/html'])


@docs.command(name='view', help="View generated documentation")
def viewdocs():
    filepath = os.path.abspath('./docs/_build/html/index.html')
    if not os.path.isfile(filepath):
        print('No documentation found. Run docs command')
        return

    browse_to(filepath)


@cli.command(help="Build wheel and upload to internal pypi server")
@click.option('--force', '-f', default=False, is_flag=True, help="Force")
@click.option('--username', '-u', help='Username for uploading to internal '
              'pypi server')
@click.option('--password', '-p', help='Password')
@click.pass_context
def upload(ctx, username=None, password=None, force=False):
    ctx.invoke(build)

    def package_exists(path):
        parsed_filename = WheelFile(path).parsed_filename
        package, version = parsed_filename.group(2), parsed_filename.group(4)
        p = sp.check_output(
            'devpi list {}=={}'.format(package, version).split())
        exists = True if p else False
        if exists:
            print('Package {}={} already exists.'.format(package, version))
        return exists

    def get_wheel_path():
        dist_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'dist'))
        return next(iter(glob.glob('{}/*.whl'.format(dist_dir))))

    wheel_path = get_wheel_path()
    if not package_exists(wheel_path) or force:
        if username:
            if not password:
                password = getpass.getpass()
            sp.check_call(['devpi', 'login', username, '--password', password])

        sp.check_call(['devpi', 'upload', wheel_path])


@cli.command(help="Initial setup of frontend stuff")
def init():
    init_npm_submodule()
    activate_local_node()
    setup_npm()
    set_registry()
    install_tools()
    install_packages()


def activate_local_node():
    os.environ['PATH'] = node_dir + os.pathsep + os.environ['PATH']
    os.environ['NODE_PATH'] = join(node_dir, 'node_modules')


def init_npm_submodule():
    print('Init git submodules...')
    git_init_cmd = ['git', 'submodule', 'update', '--init']
    call(git_init_cmd)


def setup_npm():
    print('Setting up npm...')
    npm_dir = join(vendor_dir, 'npm')
    clijs = join(npm_dir, 'cli.js')
    call(['node', clijs, 'install', 'npm@3.9.5', '-g'])


def set_registry():
    print('Setting npm registry')
    call(['npm.cmd', 'set', 'registry', 'https://npm.lundalogik.com:4873'])


def install_packages():
    cwd = os.getcwd()
    os.chdir(frontend_dir)
    rm_nodemodules()
    print('Installing webclient development dependencies...')
    call(['npm.cmd', 'install'])
    os.chdir(cwd)
    print('Cleaning up temp...')
    cleanup_temp()


def cleanup_temp():
    folders = glob.glob(join(gettempdir(), 'npm-*'))

    for folder in folders:
        shutil.rmtree(folder)


def rm_nodemodules():
    message = 'Removing any currently installed npm packages...'
    rm_dir(node_modules_dir(), message)


def rm_dir(dir, message):
    if not exists(dir):
        return

    print(message)
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.devnull, 'w') as devnull:
            sp.call(['robocopy', temp_dir, dir, '/MIR'],
                    stdout=devnull, stderr=devnull)

    shutil.rmtree(dir)


def install_tools():
    """
    Install global command lines tools. These are there as a convenience
    only, and should be safe to install directly from npm.org.
    """
    print('Installing webclient command line development tools...')

    for package in ['gulp']:
        if not package_exists(package):
            install_global_package(package)


def package_exists(package):
    try:
        call(['npm.cmd', 'ls', '-g', package], stdout=sp.DEVNULL)
        print("{} already installed".format(package))
        return True
    except sp.CalledProcessError:
        print("{} not installed".format(package))
        return False


def install_global_package(package):
    print('Installing package {}...'.format(package))
    if not call(['npm.cmd', 'install', '-g', package]):
        print('Failed to install global package {}'.format(package))
        print('This is not essential for a successful build')


def script_path():
    return normpath(abspath(dirname(__file__)))


def node_modules_dir():
    return normpath(abspath(join(frontend_dir, 'node_modules')))


def call(cmd, cwd=None, stdout=None):
    logger.debug(cmd if isinstance(cmd, str) else sp.list2cmdline(cmd))
    sp.check_call(cmd, env=os.environ, cwd=cwd, stdout=stdout)


def rm(path):
    if os.path.isfile(path):
        os.remove(path)


def rm_rf(path):
    if os.path.isdir(path):
        shutil.rmtree(path)


def cp(src, dest):
    if os.path.isdir(src):
        shutil.copytree(src, dest)
        return
    shutil.copy(src, dest)


@contextmanager
def cd(path):
    cwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(cwd)


def browse_to(filepath):
    filepath = os.path.abspath(filepath)

    if sys.platform.startswith('darwin'):
        sp.call('open', filepath)
    elif os.name == 'nt':
        os.startfile(filepath)
    elif os.name == 'posix':
        sp.call('xgd-open', filepath)


def _setup_logger(level):
    global_log = logging.getLogger()
    global_log.setLevel(getattr(logging, level))
    global_log.addHandler(logging.StreamHandler(sys.stdout))


def run_cli():
    try:
        sys.exit(cli())
    except sp.CalledProcessError as e:
        sys.exit(e.returncode)


if __name__ == '__main__':
    with cd(ROOT):
        run_cli()
