#!/bin/bash

set -e

root_path=$(dirname $(realpath $0))

python3 -m pip uninstall -y dummy failing || true
python3 -m pip install -e $root_path/tests/libs/dummy
python3 -m pip install -e $root_path/tests/libs/failing

set +e

# disable failing plugin import
export ETL_ENTITIES_PLUGINS_BLACKLIST=failing-plugin

$root_path/pytest_runner.sh "$@"
ret=$?

python3 -m pip uninstall -y dummy failing || true
exit "$ret"
