CONFIG ?= config.txt
UV ?= uv
VENV_DIR := .venv
LINT_EXCLUDE := .git,.venv,__pycache__,.mypy_cache,.pytest_cache,build,dist
MYPY_EXCLUDE := (^|/)(\.venv|build|dist)/


install: check-uv
	$(UV) sync
	$(UV) run python -c "import sys; assert sys.version_info >= (3, 10)"

check-uv:
	@command -v $(UV) >/dev/null 2>&1 || \
		{ echo "Error: uv is required (https://docs.astral.sh/uv/)."; exit 1; }

run: check-uv
	$(UV) run python a_maze_ing.py $(CONFIG)

clean:
	find . \( -path './.git' -o -path './$(VENV_DIR)' \) -prune -o \
		-type d -name __pycache__ -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache build dist
	find . -maxdepth 1 -type d -name '*.egg-info' -exec rm -rf {} +

fclean: clean
	rm -rf .venv

lint: check-uv
	$(UV) run flake8 . --exclude=$(LINT_EXCLUDE)
	$(UV) run mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs --exclude '$(MYPY_EXCLUDE)'

lint-strict: check-uv
	$(UV) run flake8 . --exclude=$(LINT_EXCLUDE)
	$(UV) run mypy . --strict --exclude '$(MYPY_EXCLUDE)'

.PHONY: check-uv install run debug clean lint lint-strict
