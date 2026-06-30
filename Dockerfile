FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock* ./
COPY configs ./configs
COPY scripts ./scripts
COPY src ./src
COPY tests ./tests

RUN uv sync --frozen --all-groups

CMD ["uv", "run", "python", "scripts/preprocess.py"]
