FROM docker.rep.msk.mts.ru/platform/python:3.7.7
LABEL maintainer="ONEtools"

ENV LANGUAGE=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN useradd -ms /bin/bash -d /app hwmlib \
    && chown -R hwmlib:hwmlib /app

COPY requirements.txt requirements-test.txt /app/

ARG BUILD_NUMBER
ARG BRANCH_NAME

RUN pip3 install -r requirements.txt -r requirements-test.txt

USER hwmlib
COPY --chown=hwmlib:hwmlib ./ /app/

# Build /app/dist/hwmlib*.whl
RUN python3 setup.py bdist_wheel
