import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "requirements.txt")) as f:
    requirements = f.readlines()

with open(os.path.join(here, "requirements-test.txt")) as f:
    test_requirements = f.readlines()

with open(os.path.join(here, "README.rst")) as f:
    long_description = f.read()

setup(
    name="hwmlib",
    version="1.0.0",
    author="Volkov Dmitrii",
    description="HWM lib",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://gitlab.services.mts.ru/bigdata/platform/onetools/hwmlib",
    packages=find_packages(exclude=["docs", "docs.*", "tests", "tests.*"]),
    classifiers=[
        "Topic :: Software Development :: HWM lib",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    install_require=requirements,
    tests_require=test_requirements,
    extras_require={"test": test_requirements},
    setup_requires=["setuptools-git-versioning"],
    test_suite="tests",
    zip_safe=False,
)
