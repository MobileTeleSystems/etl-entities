ARG PYTHON_VERSION=3.7
FROM docker.rep.msk.mts.ru/platform/python:${PYTHON_VERSION} as base
LABEL maintainer="ONEtools"

ENV REQUESTS_CA_BUNDLE=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem
ENV CURL_CA_BUNDLE=$REQUESTS_CA_BUNDLE \
    SSL_CERT_FILE=$REQUESTS_CA_BUNDLE

RUN yum -y install autoconf zlib-devel perl-devel gcc g++ make && \
    yum -y remove pyparsing && \
    yum clean all

RUN set -ex; \
    cd /tmp; \
    curl -s -q -L -k http://rep.msk.mts.ru/artifactory/files/git/git-2.28.0.tar.gz --output git.tar.gz; \
    tar -zxf git.tar.gz; \
    cd /tmp/git-2.28.0; \
    make configure; \
    ./configure --prefix=/usr/local --without-tcltk; \
    make install NO_GETTEXT=1; \
    git --version; \
    rm -rf /tmp/git*

ENV LANGUAGE=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN useradd -ms /bin/bash -d /app etl-entities \
    && chown -R etl-entities:etl-entities /app

COPY requirements.txt requirements-test.txt /app/

ARG BUILD_NUMBER
ARG BRANCH_NAME

RUN pip3 install -r requirements.txt -r requirements-test.txt

USER etl-entities
COPY --chown=etl-entities:etl-entities ./ /app/
