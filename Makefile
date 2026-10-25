.PHONY: format lint docstring check test sync setup play score replay start-jiuwen resume
.DEFAULT_GOAL := setup

# ----- Useful for participants of the competition -----

# Install dependencies
sync:
	uv sync

# Setup environment variables and mcp config
setup:
	uv run python -m career_sim_runner setup

# Play a game with the current solution.
# Package versions come from `make sync`. This only reloads the dev dataset.
play:
	uv run career-emulator-engine update --source distribution --split dev
	uv run python -m career_sim_runner play --submission solution

# Check last run's score
score:
	uv run python -m career_sim_runner score

# Render readable markdown from the last run's events log
replay:
	uv run python -m career_sim_runner replay --live

# Start JiuwenSwarm instance in current terminal
start-jiuwen:
	uv run jiuwenswarm-start --name career_emu all

# ----- Please ignore, this is only used by internal developers -----

# Resume an unfinished game
resume:
	uv run python -m career_sim_runner play --submission solution --continue

# Format code with ruff
format:
	uv run ruff check --select I --select E --select F --fix
	uv run ruff format

# Type check with mypy
lint:
	@uv run --group format mypy -p career_sim_runner

# Check docstring convention (with pydocstyle rules in ruff)
docstring:
	@uv run ruff check --select D career_sim_runner/

# Check format, docstring, typing
check: format docstring lint

# Run unit tests
test:
	@uv run pytest tests/
