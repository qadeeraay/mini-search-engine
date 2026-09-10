.PHONY: setup run test bench docker-up docker-down clean

setup:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt

run:
	.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload

test:
	.venv/bin/pytest -v tests/

bench:
	.venv/bin/python scripts/benchmark_search.py

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
