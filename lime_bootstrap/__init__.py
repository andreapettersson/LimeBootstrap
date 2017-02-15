from os.path import abspath, dirname, join
from flask import Blueprint

DEFAULT_CONFIG = {
}


def get_static_filepaths(is_source_install=False):
    file_path = abspath(dirname(__file__))
    static_path = join(file_path, 'static')
    source_path = join(file_path, '..', 'frontend')
    return static_path if not is_source_install else source_path


blueprint = Blueprint('lime_bootstrap', __name__)
