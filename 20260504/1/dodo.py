import os
from pathlib import Path
import shutil
import subprocess
import glob
from doit.tools import run_once, create_folder
from doit.task import clean_targets

DOIT_CONFIG = {
    'default_tasks': ['html'],
    'verbosity': 2,
}

LOCALE_DIR = 'mood/server/locale'
POT_FILE = os.path.join(LOCALE_DIR, 'messages.pot')
PO_FILE = os.path.join(LOCALE_DIR, 'ru_RU', 'LC_MESSAGES', 'messages.po')
MO_FILE = os.path.join(LOCALE_DIR, 'ru_RU', 'LC_MESSAGES', 'messages.mo')

def find_files(pattern, root='.'):
    return [str(p) for p in Path(root).glob(pattern) if p.is_file()]

def task_extract():
    py_files = find_files('*.py', 'mood')
    return {
        'actions': [
            f'pybabel extract -F babel.cfg -o {POT_FILE} .' if os.path.exists('babel.cfg') 
            else f'pybabel extract -o {POT_FILE} mood/'
        ],
        'file_dep': py_files,
        'targets': [POT_FILE],
        'clean': [clean_targets],
        'verbosity': 2,
    }

def task_update():
    return {
        'actions': [
            f'pybabel update -i {POT_FILE} -o {PO_FILE} -l ru_RU'
        ],
        'file_dep': [POT_FILE],
        'targets': [PO_FILE],
        'clean': [],
        'verbosity': 2,
    }

def task_compile():
    return {
        'actions': [
            f'pybabel compile -d {LOCALE_DIR} -l ru_RU'
        ],
        'file_dep': [PO_FILE],
        'targets': [MO_FILE],
        'clean': [clean_targets],
        'verbosity': 2,
    }

def task_i18n():
    return {
        'actions': [],
        'task_dep': ['extract', 'update', 'compile'],
        'verbosity': 2,
    }

def task_html():
    def clean_docs():
        shutil.rmtree('docs/_build', ignore_errors=True)
    src_dir = 'docs'
    build_dir = 'docs/_build/html'
    rst_files = find_files('*.rst', src_dir)
    py_files = find_files('*.py', 'mood')
    return {
        'actions': [f'sphinx-build -b html {src_dir} {build_dir}'],
        'file_dep': rst_files + py_files + [f'{src_dir}/conf.py'],
        'targets': [f'{build_dir}/index.html'],
        'clean': [clean_docs],
        'verbosity': 2,
    }

def task_test():
    def clean_pytest_cache():
        shutil.rmtree('.pytest_cache', ignore_errors=True)
    test_files = find_files('test_*.py', 'mood/tests')
    code_files = find_files('*.py', 'mood')
    return {
        'actions': ['pytest mood/tests -v'],
        'file_dep': [MO_FILE] + test_files + code_files,
        'task_dep': ['i18n'],
        'clean': [clean_pytest_cache],
        'verbosity': 2,
    }
