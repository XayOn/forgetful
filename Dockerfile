FROM python:3.10.2-slim-bullseye as base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 \
    # pip:
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # poetry:
    POETRY_VERSION=1.1.13 \
    POETRY_NO_INTERACTION=1 \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    PATH="$PATH:/root/.local/bin"

WORKDIR /waka-readme

# install poetry
# RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
RUN pip install pipx
RUN pipx install "poetry==$POETRY_VERSION"
RUN pipx ensurepath

# install dependencies
COPY pyproject.toml poetry.lock ./
RUN apt-get update && apt-get install -y build-essential \
 && poetry install --no-dev --no-root --no-interaction --no-ansi \
 && rm -rf /var/lib/apt/lists/* && apt-get remove build-essential 

# copy and run program
copy app.py ./
CMD [ "poetry", "run", "uvicorn", "app:app" ]
