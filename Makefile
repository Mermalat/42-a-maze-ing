CONFIG ?= config.txt
UV ?= uv
VENV_DIR := .venv
.DEFAULT_GOAL := install

install: check-uv
	$(UV) sync --locked

check-uv:
	@command -v $(UV) >/dev/null 2>&1 || \
		{ echo "Error: uv is required (https://docs.astral.sh/uv/)."; exit 1; }

run: check-uv
	$(UV) run --locked python a_maze_ing.py "$(CONFIG)"

debug: check-uv
	$(UV) run --locked python -m pdb a_maze_ing.py "$(CONFIG)"

build: check-uv
	$(UV) build --wheel --out-dir .

clean:
	find . \( -path './.git' -o -path './$(VENV_DIR)' \) -prune -o \
		-type d -name __pycache__ -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache build dist
	find . -maxdepth 1 -type d -name '*.egg-info' -exec rm -rf {} +

fclean: clean
	rm -rf .venv

lint: check-uv
	$(UV) run --locked flake8 .
	$(UV) run --locked mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict: check-uv
	$(UV) run --locked flake8 .
	$(UV) run --locked mypy . --strict

.PHONY: check-uv install run debug build clean fclean lint lint-strict
