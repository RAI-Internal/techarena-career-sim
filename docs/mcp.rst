Configuring the track MCP server
================================

The agent interacts with the simulation through the MCP server provided by
``career-emulator-engine``. This page describes the supported configuration
and the official tool interface.

Configuration in JiuwenSwarm
----------------------------

Use JiuwenSwarm version ``0.2.4b3`` only, in single-agent (``agent``) mode.
The JiuwenSwarm ``team`` mode is prohibited for this competition, including
when testing a design that will be submitted. Install the version pinned by
the official participation repository; do not substitute another version.

In the official participation repository, install the dependencies and
configure the environment:

.. code-block:: bash

   make sync
   cp .env.example .env
   # Enter API_BASE, API_KEY, and MODEL_NAME as instructed in the API key email.
   # Do not add OpenRouter provider routing settings.
   make setup

``make setup`` performs the following actions:

1. Creates a JiuwenSwarm named instance called ``career_emu``.
2. Writes ``career-emulator-engine-mcp`` into the instance MCP configuration.
3. Copies ``API_BASE``, ``API_KEY``, and ``MODEL_NAME`` from ``.env`` into the
   instance environment.

Official scoring uses the designated model under organiser-controlled
upstream routing. See :doc:`api-key` and :doc:`competition-rules`.

Start the instance with:

.. code-block:: bash

   make start-jiuwen

After startup, use the JiuwenSwarm web interface on the port assigned to the
``career_emu`` instance.

Connecting another MCP client
-----------------------------

During development, another MCP client may connect to the official server
through its standard input/output transport:

.. code-block:: bash

   career-emulator-engine-mcp

Use the server executable provided by the installed
``career-emulator-engine`` package. Do not replace it with a modified server,
connect directly to the simulation database, or call internal package
functions as a substitute for the MCP interface.

Available MCP tools
-------------------

The official MCP interface provides five tools:

- ``new_game()``: start a new simulation and return a ``session_id``.
- ``observe(session_id)``: return the current state, event, and choices.
- ``take_action(session_id, choice, notes)``: apply a selected choice and
  record an agent note.
- ``check_latest_logs(session_id, count=10)``: return recent log entries for
  the session.
- ``show_employee_handbook()``: return the public employee handbook.

The server also exposes the session log through the
``logs://{session_id}`` resource where that resource is supported by the MCP
client.

These tools are the complete official agent interface for evaluated runs.
Restrictions on direct package inspection and hard-coded dataset knowledge are
stated in :doc:`competition-rules`.
