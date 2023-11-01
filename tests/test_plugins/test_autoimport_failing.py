import textwrap

import pytest

import etl_entities


def test_autoimport_failing(monkeypatch):
    monkeypatch.delenv("ETL_ENTITIES_PLUGINS_BLACKLIST", raising=False)

    error_msg = textwrap.dedent(
        r"""
        Error while importing plugin 'failing-plugin' from package 'failing' v0.1.0.

        Statement:
            import failing

        Check if plugin is compatible with current etl_entities version \d+.\d+.\d+.

        You can disable loading this plugin by setting environment variable:
            ETL_ENTITIES_PLUGINS_BLACKLIST='failing-plugin,failing-plugin'

        You can also define a whitelist of packages which can be loaded by etl_entities:
            ETL_ENTITIES_PLUGINS_WHITELIST='not-failing-plugin1,not-failing-plugin2'

        Please take into account that plugin name may differ from package or module name.
        See package metadata for more details
        """,
    ).strip()

    with pytest.raises(ImportError, match=error_msg):
        etl_entities.plugins_auto_import()


def test_autoimport_failing_disabled(monkeypatch):
    monkeypatch.setenv("ETL_ENTITIES_PLUGINS_ENABLED", "false")

    # no exception
    etl_entities.plugins_auto_import()


def test_autoimport_failing_whitelist(monkeypatch):
    monkeypatch.delenv("ETL_ENTITIES_PLUGINS_BLACKLIST", raising=False)

    # skip all plugins instead of some-other-plugin
    monkeypatch.setenv("ETL_ENTITIES_PLUGINS_WHITELIST", "some-other-plugin")

    # no exception
    etl_entities.plugins_auto_import()

    # import only failing-plugin
    monkeypatch.setenv("ETL_ENTITIES_PLUGINS_WHITELIST", "failing-plugin")
    with pytest.raises(ImportError):
        etl_entities.plugins_auto_import()


def test_autoimport_failing_blacklist(monkeypatch):
    # ignore failing plugin
    monkeypatch.setenv("ETL_ENTITIES_PLUGINS_BLACKLIST", "failing-plugin")

    # no exception
    etl_entities.plugins_auto_import()

    # return failing plugin back
    monkeypatch.setenv("ETL_ENTITIES_PLUGINS_BLACKLIST", "some-other-plugin")
    with pytest.raises(ImportError):
        etl_entities.plugins_auto_import()


def test_autoimport_failing_env_variables_priority(monkeypatch):
    # blacklist is applied after whitelist
    monkeypatch.setenv("ETL_ENTITIES_PLUGINS_BLACKLIST", "failing-plugin")
    monkeypatch.setenv("ETL_ENTITIES_PLUGINS_WHITELIST", "failing-plugin")

    etl_entities.plugins_auto_import()
