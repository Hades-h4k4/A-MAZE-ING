# Makefile for a_maze_ing automation constraints (Section III.2)

.PHONY: install run debug clean lint

install:
	pip install --upgrade pip setuptools build wheel flake8 mypy

run:
	python3 a_maze_ing.py default_config.txt

debug:
	python3 -m pdb a_maze_ing.py default_config.txt

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache build dist *.egg-info maze.txt

run:
	python3 -m src.main default_config.txt

debug:
	python3 -m pdb -m src.main default_config.txt

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
