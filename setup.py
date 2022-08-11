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
    url="https://gitlab.services.mts.ru/bigdata/platform/onetools/etl-entities",
    packages=find_packages(exclude=["docs", "docs.*", "tests", "tests.*"]),
    classifiers=[
        "Intended Audience :: Data engineers",
        "Topic :: Software Development :: ETL tools",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Documentation": "https://docs.bd.msk.mts.ru/etl-entities/",
        "Source": "https://git.bd.msk.mts.ru/bigdata/platform/onetools/etl-entities",
        "CI/CD": "https://gitlab.services.mts.ru/bigdata/platform/onetools/etl-entities/-/pipelines",
        "Tracker": "https://jira.bd.msk.mts.ru/projects/ONE/issues",
    },
    python_requires=">=3.7",
    install_requires=requirements,
    test_suite="tests",
    include_package_data=True,
    zip_safe=False,
)
