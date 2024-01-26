# setup.py
from setuptools import setup

setup(
    name='terraform-version-manager',
    version='1.0.0',
    description='Terraform Version Manager',
    author='Peter Mullenmaster',
    author_email='mullenmaster@outlook.com',
    url='https://github.com/mullenmaster/terraform-version-manager',
    py_modules=['tvm'],
    install_requires=[
        'requests',
        'argparse',
    ],
    entry_points={
        'console_scripts': [
            'tvm = tvm:main',
        ],
    },
)
