Quickstart
==========

If you want to understand what this track is really about, one sentence is
enough:

    Over 48 months, do not get yourself knocked out, and make the career
    settlement read like something you would actually put on a resume.

The gameplay loop
-----------------

Each month the system advances time, generates story events, and asks you to
choose based on the current state. At the end of each quarter you get 3
``Energy`` points for energy actions, plus one additional quarterly main action.
Every 6 months the system runs a performance review and settles the performance
bonus.

You do not need to know every hidden rule up front, but you should at least
understand three things:

- Story choices drive short-term stat changes and also steer which events come
  next.
- Quarterly actions are your main lever for actively shaping your career path.
- This is a long game: many risks do not explode in the same month; they
  accumulate and get settled together later.

Local setup
-----------

Use the official participation repository for local development and submission
(`GitHub <https://github.com/RAI-Internal/techarena-career-sim>`_). It integrates
dependency management, JiuwenSwarm configuration, and automatic scoring.

After cloning the repository, install dependencies:

.. code-block:: bash

   make sync

This installs `career-emulator-engine <https://pypi.org/project/career-emulator-engine>`_
(the English engine plus MCP, which pulls in
`career-emulator-techarena <https://pypi.org/project/career-emulator-techarena>`_
dev data), ``uv``, and the rest of the project dependencies.

Then configure your environment variables (model API, etc.). The official
evaluation uses ``deepseek-v4-flash``; set ``MODEL_NAME`` to the same model for
local development:

.. code-block:: bash

   cp .env.example .env
   # Edit .env and fill in API_BASE, API_KEY
   # MODEL_NAME="deepseek-v4-flash"
   make setup

``make setup`` initializes the JiuwenSwarm named instance ``career_emu`` and
writes the MCP configuration into the instance directory.

Start the JiuwenSwarm ``career_emu`` instance in a separate terminal:

.. code-block:: bash

   make start-jiuwen

You can check instance status at any time:

.. code-block:: bash

   uv run jiuwenswarm-start --list

The last number in the ``PORTS`` column is the frontend UI port (for example
``6173``), so open ``http://localhost:6173`` for the JiuwenSwarm web UI.

Play a game:

.. code-block:: bash

   make play

Check the score:

.. code-block:: bash

   make score

Generate a readable Markdown recap from the latest ``events-*.jsonl`` run:

.. code-block:: bash

   make replay

Trying the rules by hand
------------------------

If you only want to try the rules manually (without an agent), you can install
the engine directly and play through the CLI:

.. code-block:: bash

   pip install career-emulator-engine
   career-emulator-engine update --source distribution
   career-emulator-engine play

The most useful commands inside the CLI:

- Type a number: take the corresponding choice.
- Type ``handbook``: open the employee handbook at any time.
- Type ``logs``: view the current session log.
- Type ``quit``: exit the current game.

Run artifacts
-------------

Each run writes output under ``.career_sim_runner/career_emu/``:

.. code-block:: text

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

Deliverable
-----------

For the competition, the recommended approach is:

1. Use `JiuwenSwarm <https://openjiuwen.com/jiuwenswarm>`_ as your agent partner.
2. Distill observation, analysis, risk alerts, and action suggestions into one
   or more `Skills <https://agentskills.io>`_.
3. Package one or more skill folders into a single ``zip`` as the deliverable.

A submission is laid out like this:

.. code-block:: text

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

``manifest.json`` records the team name and submission metadata:

.. code-block:: json

   {
     "team": "your-team-name",
     "name": "your-submission-name",
     "mode": "agent",
     "instruction": ""
   }

The ``mode`` field tells JiuwenSwarm how to run your agent:

- ``agent``: single-agent mode. Supports general tools, skills, and MCP, plus
  task planning, sub-agent orchestration, and skill evolution; memory is passive.
- ``team``: multi-agent collaboration. A leader plans and schedules work while
  teammates execute in parallel by role, which fits multi-agent workflows.

A practical way to split skills:

- One skill reads state and logs and summarizes the situation.
- One skill makes short-to-mid-term strategy calls, balancing health, dignity,
  output, and network.
- One skill watches risks and failure directions, so the team does not suddenly
  discover what career free-fall feels like.

You can also call the ``career_sim_runner`` CLI directly, for example to validate
a submission:

.. code-block:: bash

   uv run python -m career_sim_runner validate --submission solution

Track interaction
-----------------

The track talks to the agent through the ``career-emulator-engine``
`MCP <https://modelcontextprotocol.io>`_ server. In the participation repository,
``make setup`` configures the MCP server for JiuwenSwarm automatically, so no
manual setup is required.

If you want another agent to play over MCP during development, connect to the
``stdio`` MCP server through this entry point:

.. code-block:: bash

   career-emulator-engine-mcp

See :doc:`mcp` for more JiuwenSwarm and MCP configuration details. Common MCP
tools include:

- ``new_game``: start a new game.
- ``observe(session_id)``: read current state, the current event, and choices.
- ``take_action(session_id, choice, notes)``: apply a choice and log notes.
- ``show_employee_handbook()``: fetch the public handbook.
- ``check_latest_logs(session_id)``: read recent logs.

What to watch on your first strategy
------------------------------------

- Keep away from the publicly visible danger edges early: do not let health,
  dignity, network, or wealth sit in the gutter for long.
- Do not pour every resource into a single dimension. Great short-term numbers do
  not guarantee that performance and promotion will applaud six months later.
- When you see a line of natural-language feedback, do not read it as flavor
  text. Many hidden mechanics will not give you a formula, but they will give you
  a hint.

If you have not read the handbook yet, the next page to open is the
:doc:`public handbook <handbook>`. That is the rule foundation this track can
state openly.
