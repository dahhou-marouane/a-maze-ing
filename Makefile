CONFIG = config.txt

install:
	pip install -r requirements.txt

run:
	@python3 a_maze_ing.py $(CONFIG)

debug:
	python3 -m pdb a_maze_ing.py $(CONFIG)

clean:
	find . -type d -name __pycache__ -exec rm -rf __pycache__
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -name "*.pyc" -delete

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

.PHONY: install run debug clean lint lint-strict
