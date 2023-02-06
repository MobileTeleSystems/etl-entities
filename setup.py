from os.path import abspath, dirname, join

from setuptools import find_packages, setup

from version import get_version

__version__ = get_version()
SELF_PATH = abspath(dirname(__file__))

with open(join(SELF_PATH, "requirements.txt")) as f:
    requirements = [line.rstrip() for line in f if line and not line.startswith("#")]

with open(join(SELF_PATH, "README.rst")) as f:
    long_description = f.read()

setup(
    name="etl-entities",
    version=__version__,
    author="ONEtools Team",
    author_email="onetools@mts.ru",
    description="ETL Entities lib",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    license="Apache License 2.0",
    license_files=("LICENSE.txt",),
    url="https://github.com/MobileTeleSystems/etl-entities",
    packages=find_packages(exclude=["docs", "docs.*", "tests", "tests.*"]),
    classifiers=[
        "Intended Audience :: Data engineers",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Software Development :: ETL tools",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Documentation": "https://etl-entities.readthedocs.io/en/stable/",
        "Source": "https://github.com/MobileTeleSystems/etl-entities",
        "CI/CD": "https://github.com/MobileTeleSystems/etl-entities/actions",
        "Tracker": "https://github.com/MobileTeleSystems/etl-entities/issues",
    },
    python_requires=">=3.7",
    install_requires=requirements,
    test_suite="tests",
    include_package_data=True,
    zip_safe=False,
)
