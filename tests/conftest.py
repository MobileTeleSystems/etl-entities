import os

# disable failing plugin import
os.environ["ETL_ENTITIES_PLUGINS_BLACKLIST"] = "failing-plugin"
