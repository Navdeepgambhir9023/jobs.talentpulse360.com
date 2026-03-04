.PHONY: test test-unit test-integration coverage lint

test:
	python3 -m pytest tests/ -v

test-unit:
	python3 -m pytest tests/unit/ -v

test-integration:
	python3 -m pytest tests/integration/ -v

coverage:
	python3 -m pytest tests/ --cov=app --cov-report=term-missing --cov-fail-under=80

lint:
	python3 -m ruff check app/ tests/
