FROM docker.rep.msk.mts.ru/platform/python:3.7-slim

ARG BUILD_NUMBER
ARG BRANCH_NAME

RUN unset HTTPS_PROXY HTTP_PROXY https_proxy http_proxy \
    && yum -y install \
        zlib-devel \
        bzip2-devel \
        make \
        gcc \
        gcc-c++ \
    && pip install -U pip setuptools wheel \
    && yum clean all \
    && rm -rf /tmp/* /var/tmp/* /root/.cache/*

# Build with your own UID and GID in Linux using --build-arg UID=$(id -u) --build-arg GID=$(id -g)
ARG UID=1000
ARG GID=${UID}
ARG WS=/opt/project

RUN groupadd --gid ${GID} user \
    && useradd \
        --create-home \
        --home-dir ${WS} \
        --uid ${UID} \
        --gid ${GID} \
        --shell /bin/bash \
        user \
    && chown -R user:user ${WS} \
    && rm -rf /var/log/lastlog \
    && touch /var/log/lastlog

COPY --chown=user:user \
    ./README.rst \
    ./setup.py \
    ./requirements-test.txt \
    ./docker/entrypoint.sh \
    ${WS}/

ENV WS=${WS} \
    LANGUAGE=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    PYTHONUNBUFFERED=1

WORKDIR ${WS}

COPY --chown=user:user src/ ./src
COPY --chown=user:user tests/ ./tests

# The ${WS}/dist will contain the final artifact
# You can install it with pip install --find-links ${WS}/dist 'hwmlib[dev]'
RUN python3 setup.py bdist_wheel \
    && pip install --editable '.[test]' \
    && rm -rf /tmp/* /var/tmp/* /root/.cache/* \
    && mv "${WS}/entrypoint.sh" / \
    && chmod 755 /entrypoint.sh \
    && chown user:user -R ${WS}

USER user

ENTRYPOINT ["/entrypoint.sh"]