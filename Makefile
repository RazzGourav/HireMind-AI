.PHONY: install format lint test reproduce demo docker clean

install:
	uv sync --all-groups

format:
	uv run black .
	uv run isort .

lint:
	uv run ruff check .
	uv run mypy --explicit-package-bases src scripts

test:
	uv run pytest

reproduce: install
	python scripts/preprocess.py
	python scripts/build_retrieval_index.py
	python scripts/build_knowledge_layer.py
	python scripts/generate_submission.py
	python scripts/validate_submission.py
	python scripts/package_submission.py

demo:
	docker-compose up --build

docker:
	docker build .

clean:
	python -c "import shutil, pathlib; [shutil.rmtree(path, ignore_errors=True) for path in ['.pytest_cache', '.mypy_cache', '.ruff_cache', 'outputs', 'artifacts']]; [path.unlink(missing_ok=True) for path in pathlib.Path('.').rglob('*.pyc')]"
