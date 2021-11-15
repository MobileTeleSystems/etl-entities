#!/usr/bin/env bash

# Mount local files (tests, etc) into /opt/project, so the directory will be
# consistently cleaned up across test runs.
if [ -d /opt/project ]; then
    echo "========================/opt/project Cleanup========================"
    find /opt/project -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
fi

exec "$@"
