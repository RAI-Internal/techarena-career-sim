Configuring the track MCP server
================================

This page explains how to configure the ``career-emulator-engine`` MCP server in
`JiuwenSwarm <https://openjiuwen.com/jiuwenswarm>`_.

Wiring it into JiuwenSwarm
--------------------------

In the participation repository, run:

.. code-block:: bash

   make sync
   cp .env.example .env
   # Edit .env and fill in API_BASE, API_KEY
   # MODEL_NAME="deepseek-v4.1-flash"
   make setup

``make setup`` will:

1. Create a JiuwenSwarm named instance called ``career_emu``.
2. Write ``career-emulator-engine-mcp`` into the instance's MCP config file.
3. Sync the model variables from ``.env`` into the instance environment. The
   official evaluation uses ``deepseek-v4.1-flash``, so set ``MODEL_NAME`` to
   ``deepseek-v4.1-flash``.

Start the instance:

.. code-block:: bash

   make start-jiuwen

Once started, open the JiuwenSwarm frontend UI (default port ``6173``) to
interact with the agent in the browser.

Connecting another agent
------------------------

If you need to connect an agent other than JiuwenSwarm during development, use the
``stdio`` MCP server directly:

.. code-block:: bash

   career-emulator-engine-mcp

Available MCP tools
-------------------

- ``new_game()``: start a new game and return a ``session_id``.
- ``observe(session_id)``: read current state, the current event, and choices.
- ``take_action(session_id, choice, notes)``: apply a choice and log notes.
- ``show_employee_handbook()``: fetch the public handbook.
- ``check_latest_logs(session_id)``: read recent logs.
