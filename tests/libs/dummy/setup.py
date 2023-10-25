from setuptools import setup

setup(
    name="dummy",
    version="0.1.0",
    description="Setting up a python package",
    entry_points={"etl_entities.plugins": ["dummy=dummy"]},
)
