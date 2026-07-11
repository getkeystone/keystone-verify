.PHONY: test lint fmt

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check src/ tests/

fmt:
	uv run ruff format src/ tests/
