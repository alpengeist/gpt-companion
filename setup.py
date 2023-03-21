from setuptools import setup

APP = ['main.py']
DATA_FILES = ['profile-default.toml']
OPTIONS = {
    'packages': ['pynput', 'openai', 'toml', 'ttkbootstrap', 'charset_normalizer'],
    'emulate_shell_environment': True
}

setup(
    name="GPT Companion",
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
