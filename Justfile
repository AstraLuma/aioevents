# Show this help
help:
  @just --list

# Get the CI status of the last commit
ci:
  poetry run watch_gha_runs

# Run the test suite
test *ARGS:
  poetry run pytest {{ARGS}}

# Lints
lint:
  poetry run flake8

# Runs type checks
mypy:
  poetry run mypy aioevents


# Call the docs Makefile
docs +TARGETS:
  make -C docs {{TARGETS}}
