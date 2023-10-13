import warnings


def pytest_runtest_setup(item):
    if "deprecated" in item.keywords:
        warnings.warn(UserWarning(f"{item.name} is deprecated."))  # noqa: B028
