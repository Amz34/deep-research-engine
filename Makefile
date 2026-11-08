.PHONY: test lint clean run

PYTHON ?= python3

test:
	$(PYTHON) -m unittest discover -s tests -v

lint:
	$(PYTHON) -m py_compile deep_research.py core/*.py scripts/*.py tests/*.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:
	$(PYTHON) deep_research.py list
