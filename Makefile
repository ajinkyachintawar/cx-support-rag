.PHONY: install ingest test eval serve load-test clean

install:
	pip install -e ".[dev]"

ingest:
	python -m scripts.ingest

test:
	pytest tests/ -v --tb=short

eval:
	python -m scripts.run_evals

serve:
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

load-test:
	python eval/load_test.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true
	rm -rf .pytest_cache .coverage htmlcov
