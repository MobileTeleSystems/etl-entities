import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
source_dir = 'src'

with open(os.path.join(here, 'requirements-test.txt'), 'r') as f:
    test_requirements = f.readlines()

with open(os.path.join(here, 'README.rst'), 'r') as f:
    long_description = f.read()

setup(
    name='hwmlib',
    version='0.0.1',
    author='Volkov Dmitrii',
    description='HWM lib',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://gitlab.services.mts.ru/bigdata/platform/onetools/hwmlib',
    package_dir={'': source_dir},
    packages=find_packages(where=source_dir),
    classifiers=[
        'Topic :: Software Development :: HWM lib',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
    ],
    tests_require=test_requirements,
    extras_require={'test': test_requirements},
    setup_requires=['setuptools-git-versioning'],
    test_suite='tests',
    zip_safe=False,
)
