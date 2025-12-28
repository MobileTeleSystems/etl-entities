#!/bin/bash

set -e

root_path=$(dirname $(realpath $0))

pip uninstall -y dummy failing || true
pip install -e $root_path/tests/libs/dummy
pip install -e $root_path/tests/libs/failing

set +e

$root_path/pytest_runner.sh "$@"
ret=$?

pip uninstall -y dummy failing || true
exit "$ret"
