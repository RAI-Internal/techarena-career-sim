Quickstart
==========

This page is the supported local development workflow, in order: obtain the
competition API key, install the participation repository, configure the
local environment, run and inspect a game, and validate a submission before
packaging it. Manual command line testing and the list of run artifacts are
included at the end as reference.

Simulation overview
-------------------

A complete run lasts 48 simulated months. Each month, the simulation presents
workplace events and the agent selects a response. At the end of each quarter,
the agent receives 3 ``Energy`` points for quarterly energy actions and may
select one quarterly main action. A formal performance review is held every
six months.

Story choices affect current statistics and may affect later events. Quarterly
actions have a longer-term effect on career development. Risks may accumulate
over several months before their consequences become visible. Participants
should therefore evaluate decisions over the full 48-month run rather than
optimise only the next event. See :doc:`handbook`, :doc:`rules`, and
:doc:`failure-and-ending` for the published game information.

1. Obtain the competition API key
---------------------------------

Follow the procedure in :doc:`api-key`. The organisers issue the key by email
after verifying the team's preliminary design and Skills documents.

The issued key is limited to the designated competition model, a maximum of
USD 50 in credit, and the competition week. Enter only the ``API_BASE``,
``API_KEY``, and ``MODEL_NAME`` values supplied by the organisers in the
local environment file. Do not configure OpenRouter provider routing
locally; official scoring applies organiser-controlled routing (see
:doc:`api-key`).

Before using the competition API key, read :doc:`api-key` and submit the
preliminary design documents required for verification.

2. Install the participation repository
---------------------------------------

Clone the official participation repository from `GitHub
<https://github.com/RAI-Internal/techarena-career-sim>`_ and install its
dependencies:

.. code-block:: bash

   make sync

This prepares the project environment, including JiuwenSwarm and the
``career-emulator-engine`` package. The engine installation includes the MCP
component and the ``career-emulator-techarena`` development dataset. See
:doc:`packages` for the separate roles of the two PyPI packages.

.. important::

   The required JiuwenSwarm version is exactly ``0.2.4b3``. The official
   participation repository pins this version, so use ``make sync`` rather
   than installing, upgrading, downgrading, or replacing JiuwenSwarm
   separately. If a local environment contains another version, re-run
   ``make sync`` and test again with ``0.2.4b3`` before relying on the
   results.

   Only single-agent mode may be used. Keep ``"mode": "agent"`` in
   ``solution/manifest.json``. Do not use JiuwenSwarm ``team`` mode for
   development runs intended to represent the submitted agent, and do not
   submit a manifest with ``"mode": "team"``.

3. Configure the local environment
----------------------------------

Copy the example environment file and enter the API values supplied by the
organisers:

.. code-block:: bash

   cp .env.example .env
   # Set API_BASE, API_KEY, and MODEL_NAME from the organiser email only.
   # Do not add OpenRouter provider / order / only preferences.
   make setup

``make setup`` creates the JiuwenSwarm named instance ``career_emu`` and writes
the engine MCP configuration and model settings into that instance. Only
``API_BASE``, ``API_KEY``, and ``MODEL_NAME`` from the repository ``.env``
are overlaid onto the instance environment.

Start the instance in a separate terminal:

.. code-block:: bash

   make start-jiuwen

Instance status can be checked with:

.. code-block:: bash

   uv run jiuwenswarm-start --list

The command reports the ports assigned to the instance. The final port is the
JiuwenSwarm web interface. See :doc:`mcp` for the MCP configuration this
setup creates.

4. Run and inspect a game
-------------------------

Copy ``example_submission_structure/`` to ``solution/`` at the repository
root, then play one game with that directory. ``solution/`` is the working
copy. It is not part of the clone.

.. code-block:: bash

   make play

``presentation.mp4`` is not required for this local run. You can play before
the video is recorded. The final ZIP still requires that file, and the
validation command below reports it when it is missing.

Read the score from the latest completed run:

.. code-block:: bash

   make score

This is the score of one local run only. ``quantitative_score`` is the
0–100 career outcome. Official live play is the mean of three runs'
``quantitative_score`` values. That mean is multiplied by 0.80 once,
alongside document design quality (10%) and token efficiency (10%).
``competition_partial_score`` is ``quantitative_score × 0.7`` and is not
used in that formula. The team's Stage 1 score is its
highest valid automated version score; only the top ten teams after Stage 1
advance to expert review, where the final competition score is 70% Stage 1
score plus 30% expert review score (see :doc:`competition-rules`). A single
local score is therefore neither an official live play score, nor an
automated version score, nor the team's final score.

Create a readable Markdown replay from the latest run events:

.. code-block:: bash

   make replay

5. Validate and prepare the submission
--------------------------------------

Validate the submission before packaging it:

.. code-block:: bash

   uv run python -m career_sim_runner validate --submission solution

This command checks the submission directory only. It does not contact
JiuwenSwarm, so a stopped instance does not fail the command. It fails when
``manifest.json`` sets a mode other than ``"agent"``, including
``"mode": "team"``. Local validation is a development aid. It does not
replace the complete submission requirements in :doc:`submission`.

Prepare the final ZIP archive according to :doc:`submission`. The required
``design/`` and ``skills/`` directories must both be present, and so must
``solution/presentation.mp4``. The validation command reports a missing
video, an empty video, a placeholder team name, and a prohibited run mode. Before packaging, confirm that the final
test used JiuwenSwarm ``0.2.4b3``, and that every deliverable in the final
ZIP — the ``manifest.json`` instruction, ``README.md``, the spoken
presentation, both design documents, and every Skill — is written entirely
in English. A submission missing a required folder or file, using the
prohibited ``team`` mode, or containing a non-English deliverable is invalid
and may receive no score.

Manual command line testing
---------------------------

The rules may also be tested manually without an agent. Install the engine with
its MCP component, load the development dataset, and start the command line
interface:

.. code-block:: bash

   pip install "career-emulator-engine[mcp]"
   career-emulator-engine update --source distribution --split dev
   career-emulator-engine play

Within the command line interface:

- enter a number to select the corresponding choice;
- enter ``handbook`` to display the public employee handbook;
- enter ``logs`` to display the current session log;
- enter ``quit`` to end the session.

Manual command line use is for familiarisation and testing. An evaluated agent
must interact with the simulation through the official MCP tools described in
:doc:`mcp` and :doc:`competition-rules`.

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

These files are outputs of local runs. Participants must not modify them in
order to alter a result, and must not use the local database as a substitute
for the official MCP interface.
