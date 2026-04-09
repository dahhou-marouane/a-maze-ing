CONFIG = config.txt

install:
	@python3 -m pip install --upgrade pip
	@pip install -r requirements.txt

run:
	@python3 a_maze_ing.py $(CONFIG)

debug:
	@python3 -m pdb a_maze_ing.py $(CONFIG)

clean:
	@rm -rf .mypy_cache __pycache__ mazegen/__pycache__

clean-deep:
	@rm -rf .mypy_cache __pycache__ mazegen/__pycache__ dist mazegen.egg-info maze.txt

lint: install
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict: install
	python3 -m flake8 .
	python3 -m mypy . --strict

.PHONY: install run debug clean clean-deep lint lint-strict
