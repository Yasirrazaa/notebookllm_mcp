from setuptools import setup, find_packages
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='notebookllm',
    version='1.0',
    packages=find_packages(),
    py_modules=['cli'],
    install_requires=[
       'nbformat',
       'jupyter_client',
    ],
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    entry_points={
        "console_scripts": [
            "notebookllm = cli:main",
        ],
    },
)