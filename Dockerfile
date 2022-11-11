FROM python:3.10-slim as python
ENV PYTHONUNBUFFERED=true

ENV POETRY_VERSION=1.2.0
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache

RUN apt-get update && apt-get install gcc -y && apt-get clean

RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /app

COPY pyproject.toml ./
RUN poetry install

COPY . /app

EXPOSE 5000
CMD [ "poetry", "run", "gunicorn", "app:app", "-b", "0.0.0.0:5000" ]
