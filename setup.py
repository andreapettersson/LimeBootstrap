#!/usr/bin/env python
from setuptools import setup, find_packages
from distutils.command.build import build
import os
import shutil
from contextlib import contextmanager
from subprocess import check_call

VERSION = '1.12.0'

ROOT = os.path.abspath(os.path.dirname(__file__))


class PackageBuilder(build):
    def run(self):
        build_static_files()
        build.run(self)
        cleanup_temp_files()


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


def _get_static_temp_path():
    return os.path.join(ROOT, 'lime_webclient', 'static')


def build_static_files():
    static_dest_path = _get_static_temp_path()
    static_build_path = os.path.join(ROOT, 'frontend', 'dist')
    frontend_dir_path = os.path.join(ROOT, 'frontend')

    cleanup_temp_files()
    with cd(frontend_dir_path):
        check_call('gulp build --production', shell=True)
    cp(static_build_path, static_dest_path)


def cleanup_temp_files():
    rm_rf(_get_static_temp_path())


setup(
    name='lime-bootstrap',
    version=VERSION,

    packages=find_packages(),

    install_requires=[
        'Flask>=0.10.1',
        'lime-endpoints>=2.4.0,<3.0.0',
        'lime-config>=4.0.0,<5.0.0',
        'lime-core>=15.10.3,<16.0.0',
    ],
    include_package_data=True,
    entry_points={
        'lime_blueprints':
            'lime_bootstrap = lime_bootstrap.endpoints:register_blueprint',
        'lime_static_paths': 'static = lime_bootstrap:get_static_filepaths',
        'lime.config': 'lime_bootstrap = lime_bootstrap:DEFAULT_CONFIG',
    },
    cmdclass={
        'build': PackageBuilder,
    }
)
