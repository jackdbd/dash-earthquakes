FROM python:3.8

LABEL maintainer="jackdebidda@gmail.com"

ENV POETRY_VERSION=1.0.0 \
    APP_DIR=/usr/src/app \
    APP_PORT=5000 \
    PATH="/root/.poetry/bin:$PATH"

RUN mkdir -p ${APP_DIR}

# The WORKDIR instruction sets the working directory for any RUN, CMD,
# ENTRYPOINT, COPY and ADD instructions that follow it in the Dockerfile.
WORKDIR ${APP_DIR}

# Install and config Poetry
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/${POETRY_VERSION}/get-poetry.py | python && \
    poetry config virtualenvs.create false

# Copy only requirements, to cache them in Docker layer.
COPY pyproject.toml poetry.lock ${APP_DIR}/
RUN poetry install

COPY assets/* ${APP_DIR}/assets/
COPY app.py ${APP_DIR}/

EXPOSE ${APP_PORT}

CMD gunicorn --bind 0.0.0.0:${APP_PORT} --access-logfile - "app:server"
