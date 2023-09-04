from __future__ import annotations

import os
from pathlib import Path

from setuptools import find_packages, setup


def get_version():
    if os.getenv("GITHUB_REF_TYPE", "branch") == "tag":
        return os.environ["GITHUB_REF_NAME"]

    version_file = here / "etl_entities" / "VERSION"
    version = version_file.read_text().strip()  # noqa: WPS410

    build_num = os.environ.get("GITHUB_RUN_ID", "0")
    branch_name = os.environ.get("GITHUB_REF_NAME", "")

    if not branch_name:
        return version

    return f"{version}.dev{build_num}"


def parse_requirements(file: Path) -> list[str]:
    lines = file.read_text().splitlines()
    return [line.rstrip() for line in lines if line and not line.startswith("#")]


here = Path(__file__).parent.resolve()
requirements = parse_requirements(here / "requirements.txt")
long_description = here.joinpath("README.rst").read_text()


setup(
    name="etl-entities",
    version=get_version(),
    author="DataOps.ETL",
    author_email="onetools@mts.ru",
    description="ETL Entities lib for onETL",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    license="Apache License 2.0",
    license_files=("LICENSE.txt",),
    url="https://github.com/MobileTeleSystems/etl-entities",
    packages=find_packages(exclude=["docs", "docs.*", "tests", "tests.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Pydantic",
        "Framework :: Pydantic :: 1",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
    ],
    project_urls={
        "Documentation": "https://etl-entities.readthedocs.io/",
        "Source": "https://github.com/MobileTeleSystems/etl-entities",
        "CI/CD": "https://github.com/MobileTeleSystems/etl-entities/actions",
        "Tracker": "https://github.com/MobileTeleSystems/etl-entities/issues",
    },
    python_requires=">=3.7",
    install_requires=requirements,
    include_package_data=True,
    zip_safe=False,
)
