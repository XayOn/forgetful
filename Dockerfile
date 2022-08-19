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

WORKDIR /forgetful

RUN pip install pipx
RUN pipx install "poetry==$POETRY_VERSION"
RUN pipx ensurepath
COPY pyproject.toml poetry.lock ./
RUN apt-get update && apt-get install -y build-essential cmake libgl1 libgcc-s1 libopencv* \
    && poetry install --no-dev --no-root --no-interaction --no-ansi \
    && rm -rf /var/lib/apt/lists/* && apt-get remove -y build-essential cmake

# copy and run program
copy app.py ./
CMD [ "poetry", "run", "uvicorn", "app:app" ]
