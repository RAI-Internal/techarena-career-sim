# TechArena: Career Survival Agent

[![Documentation](https://img.shields.io/badge/Docs-blue?style=for-the-badge&logo=readthedocs&link=https%3A%2F%2Ftecharena-career-sim.readthedocs.io%2Fen%2Flatest%2Findex.html)](https://techarena-career-sim.readthedocs.io/en/latest/) [![GitHub](https://img.shields.io/badge/GitHub-black?style=for-the-badge&logo=GitHub)](https://github.com/RAI-Internal/techarena-career-sim)

This TechArena track is **Career Survival Agent**, a workplace simulation game for agents. You play a new hire on a product R&D team. Over 48 months you handle story events, spend quarterly energy, pick a main action, and try to keep a fragile balance among health, dignity, skill, network, output, and wealth.

Track docs: <https://techarena-career-sim.readthedocs.io/en/latest/>

## Prerequisites

This project uses [uv](https://docs.astral.sh/uv/) to manage Python dependencies and the virtual environment, and `make` to wrap common commands.

<details>
<summary>Install <code>make</code></summary>

#### Windows

Use [Chocolatey](https://docs.chocolatey.org/en-us/choco/setup/#more-install-options) and run `choco install make`.

#### macOS

If Xcode is already installed, run `xcode-select --install` to install the Xcode command-line tools, which include `make`. Or use [Homebrew](https://brew.sh) and run `brew install make`.

#### Linux

Run `sudo apt update`, then `sudo apt install make`. You can also install `sudo apt install build-essential`, which includes `make` and other common development tools.

</details>

## Quick start

### 1. Install dependencies

```bash
make sync
```

This installs [career-emulator-engine](https://pypi.org/project/career-emulator-engine/) (English engine + MCP; pulls in [career-emulator-techarena](https://pypi.org/project/career-emulator-techarena/) dev data), plus `uv` and the rest of this project's dependencies.

> **Tip:** Keep both [jiuwenswarm](https://openjiuwen.com/jiuwenswarm) and [career-emulator-engine](https://pypi.org/project/career-emulator-engine/) inside this repo's [uv](https://docs.astral.sh/uv/) environment, and prefix commands with `uv run`. Do not install them into the global Python environment or another venv, or they may conflict.

### 2. Configure the environment

Copy `.env.example` to `.env` and fill in your model settings:

```bash
cp .env.example .env
```

`.env` only needs three variables:

```bash
API_BASE=""
API_KEY=""
MODEL_NAME="deepseek-v4-flash"
```

Then run setup. It initializes the JiuwenSwarm named instance `career_emu` and writes the config into the instance directory:

```bash
make setup
```

### 3. Start JiuwenSwarm

Start the `career_emu` instance in a separate terminal:

```bash
make start-jiuwen
```

You can check instance status at any time:

```bash
uv run jiuwenswarm-start --list
```

Example output:

```text
INSTANCE     STATUS     PID     WORKSPACE                                          PORTS
--------------------------------------------------------------------------------
default      stopped  -       /Users/you/.jiuwenswarm                              18092/19000/19001/5173
career_emu   running  58987   /Users/you/.jiuwenswarm-instances/career_emu         19092/20000/20001/6173
```

The last number in the `PORTS` column is the frontend UI. In the example above, `career_emu` uses `6173`, so open `http://localhost:6173` for the JiuwenSwarm web UI.

### 4. Play a game

```bash
make play
```

### 5. Check the score

```bash
make score
```

### 6. Generate a readable replay

Build a Markdown recap from the latest `events-*.jsonl` run:

```bash
make replay
```

## How the game works

Each month the system advances time, generates a story event, and asks you to choose based on the current state. At the end of each quarter you also get 3 `Energy` points for energy actions, plus one extra quarterly main action. Performance reviews and bonuses land every 6 months.

- **Story choices** drive short-term stat changes and later event branches.
- **Quarterly actions** are the main way you steer your career path.
- **Long-term planning** matters: many risks do not explode in the same month; they accumulate and settle later.

A full game lasts 48 months. If you survive all 48, the ending score (D through S) combines level, wealth, wellbeing, skills, risk control, and coworker relationships.

## Deliverable

Teams must build an agent with [JiuwenSwarm](https://openjiuwen.com/jiuwenswarm) and one or more [Skills](https://agentskills.io) that help the agent play. Package the skill folders into a single `zip` as the submission.

Expected layout:

```text
solution/
  manifest.json
  README.md
  design/
    skills_design.md
    decision_report.md
  skills/
    environment-perception/
      SKILL.md
    risk-analysis/
      SKILL.md
    ...
```

`manifest.json` records the team name and submission metadata:

```json
{
  "team": "your-team-name",
  "name": "your-submission-name",
  "mode": "agent",
  "instruction": ""
}
```

`mode` tells [JiuwenSwarm](https://openjiuwen.com/jiuwenswarm) how to run the agent:

| mode | Description |
|---|---|
| `agent` | Single-agent mode. Supports general tools, skills, and MCP, plus task planning, sub-agent orchestration, and skill evolution. Memory is passive and read/written on demand. |
| `team` | Multi-agent collaboration. A leader plans and schedules work; teammates execute in parallel by role. Members inherit tools and MCP, which fits multi-agent workflows. |

## Useful Makefile commands

| Description | Make target |
|---|---|
| Install project dependencies with `uv` | `make sync` |
| Initialize the environment and JiuwenSwarm instance | `make setup` |
| Start the JiuwenSwarm `career_emu` instance | `make start-jiuwen` |
| Mount skills from `solution` and play one game through JiuwenSwarm | `make play` |
| Re-read the ending score from the last run | `make score` |

You can also call the `career_sim_runner` CLI directly (example: validate `solution`):

```bash
uv run python -m career_sim_runner validate --submission solution
```

## Run artifacts

Each run writes output under `.career_sim_runner/career_emu/`:

```text
.career_sim_runner/career_emu/
  active_install.json        # currently mounted submission
  career_emulator.sqlite3    # shared state database
  emulator_logs/             # Career Emulator logs
  outputs/
    <submission_name>/
      <timestamp>/
        transcript-*.log     # conversation transcript
        events-*.jsonl       # structured event stream
        score_report.json    # ending score report
```

## Track interaction

The track talks to the agent through the [MCP](https://modelcontextprotocol.io) service provided by [career-emulator](https://pypi.org/project/career-emulator/). Common tools:

- `new_game`: start a new game.
- `observe(session_id)`: read current state, the current event, and available choices.
- `take_action(session_id, choice, notes)`: apply a choice and write notes to the log.
- `show_employee_handbook()`: fetch the public handbook.
- `check_latest_logs(session_id)`: read recent logs.
