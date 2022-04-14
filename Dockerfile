# https://hub.docker.com/_/python
FROM python:3.8-slim-bullseye

LABEL maintainer="giacomo@giacomodebidda.com"

# Debian bullseye slim images do not include curl, so we install it now
RUN apt-get -qq update && \
    apt-get -qq -y install curl

# https://stackoverflow.com/questions/46288847/how-to-suppress-pip-upgrade-warning
ENV APP_DIR=/usr/src/app \
    APP_PORT=5000 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/root/.local/bin:$PATH"

RUN mkdir -p ${APP_DIR}

# The WORKDIR instruction sets the working directory for any RUN, CMD,
# ENTRYPOINT, COPY and ADD instructions that follow it in the Dockerfile.
WORKDIR ${APP_DIR}

# copy just the dependencies here, since they change less frequently than the application
COPY poetry.lock pyproject.toml ${APP_DIR}/

# install poetry, configure it, show some debug info, then use poetry to install the app's dependencies
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    poetry config virtualenvs.create false && \
    poetry --version && \
    poetry config --list && \
    poetry show --tree && \
    poetry install --verbose --no-interaction --no-ansi

# copy the application's source code and assets
COPY app.py ${APP_DIR}/
COPY assets/* ${APP_DIR}/assets/

EXPOSE ${APP_PORT}

CMD gunicorn --bind :${APP_PORT} "app:server"
