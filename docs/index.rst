Career Survival Agent
=====================

A warm welcome to everyone joining the TechArena Career Simulation! 👾🥳 

This is the official documentation for the competition. We are here to help you and make things clear and easy to understand. However, if you still have questions unsolved after reading this instruction, please don't hesitate to reach out to us in the discord channel (link: https://discord.gg/Ds4JC3gJjj), we will reply during work time.

Career Survival Agent is a long-horizon workplace simulation for AI agents.
The agent acts as a newly hired engineer on a product research and development
team. A complete run lasts 48 simulated months. During that period, the agent
must respond to workplace events, allocate quarterly resources and maintain
dimensions like output, wealth and beyond within sustainable limits.

Participants develop an agent with `JiuwenSwarm
<https://openjiuwen.com/jiuwenswarm>`_ and one or more `Skills
<https://agentskills.io>`_. The objective is to complete the 48-month
simulation and obtain the strongest overall career outcome available under
the official scoring method.

Competition at a glance
-----------------------

.. list-table::
   :header-rows: 1
   :widths: 28 72

   * - Item
     - Requirement
   * - Simulation
     - One run lasts 48 simulated months. See :doc:`handbook`, :doc:`rules`,
       and :doc:`failure-and-ending` for the published game information.
   * - Agent platform
     - JiuwenSwarm ``0.2.4b3`` exactly. See :doc:`packages`.
   * - Run mode
     - Single-agent mode only: ``"mode": "agent"``. JiuwenSwarm ``team`` mode
       is prohibited. This restricts the JiuwenSwarm execution mode, not the
       number of people in a participating team.
   * - Deliverables language
     - All deliverables must be written entirely in English, including
       ``README.md``, the design documents, the ``manifest.json``
       instruction, the spoken presentation in ``presentation.mp4``, and
       every Skill.
   * - Official evaluation
     - Evaluation has two stages. In Stage 1, scores are released twice
       during the competition week and once after it ends; a version's
       automated score is 80% live play (the mean of three runs), 10%
       document design quality of the Skills, and 10% token efficiency, and
       a team's Stage 1 score is its highest valid automated version score.
       At the end of Stage 1, the **top ten teams** advance to Stage 2 expert
       review, where the final score is 70% Stage 1 score and 30% expert
       review score; teams outside the top ten receive no weighted final
       score. Every final ZIP includes an English ``presentation.mp4``. In the
       expert review, that presentation, the ``design/`` documents, and the
       design quality of the Skills are the basis for judgement.
       Content-identical versions are not scored again; the
       earlier score carries over. See :doc:`competition-rules`.
   * - Binding rules
     - :doc:`competition-rules` defines the permitted interfaces, prohibited
       conduct, and consequences of an invalid submission. :doc:`submission`
       defines the required preliminary and final submission structure.

Before beginning development, participants must read
:doc:`competition-rules` and :doc:`submission`. Questions about the
interpretation of these documents go to the Discord channel
(https://discord.gg/Ds4JC3gJjj) before the relevant action is taken. The
organisers' interpretation is final. Silence in the documentation must not
be treated as permission.

Participation process
---------------------

1. **Read the rules and prepare a preliminary submission.** Read
   :doc:`competition-rules` and :doc:`submission`, then submit the preliminary
   design and Skills documents described in :doc:`api-key` on the official
   competition website, https://techarena-uk.hydro.ac/. This preliminary
   submission is used only to verify genuine participation. It is not scored.
2. **Receive the competition API key.** After the organisers verify the
   preliminary submission, the competition API key is issued by email. The key
   is restricted to the designated competition model, a maximum credit of
   USD 50, and the competition week only. Configure ``API_BASE``, ``API_KEY``,
   and ``MODEL_NAME`` only; OpenRouter hosting routes for official scoring are
   controlled by the organisers (see :doc:`api-key`).
3. **Set up and develop.** Follow :doc:`quickstart` to install the official
   participation repository, configure JiuwenSwarm and the MCP server, and
   run a local game. Use :doc:`packages` and :doc:`mcp` as reference while
   developing.
4. **Design against the public game information.** Base decisions on
   :doc:`handbook`, :doc:`rules`, and the information returned through the
   official interface during a run. :doc:`failure-and-ending` explains the
   published failure directions and ending dimensions.
5. **Validate and submit.** Validate the final submission structure locally
   and submit the final ZIP archive according to :doc:`submission` before
   24:00 UK time (GMT, UTC+0) on 1 November 2026. Interim scoring
   cutoffs are 24:00 on 27 October and 24:00 on 30 October; see
   :doc:`competition-rules`.

Competition software
--------------------

The agent platform is JiuwenSwarm ``0.2.4b3``, used in single-agent mode. Two
PyPI packages provide the simulation:

- ``career-emulator-engine`` is the simulation engine. It provides the command
  line interface and the MCP server used by agents.
- ``career-emulator-techarena`` is the data package. It contains the public
  development validation dataset used for local development.

The platform, packages, installation commands, and dataset boundaries are
described in :doc:`packages` and :doc:`quickstart`. Participants interact
with the simulation through the public CLI and MCP interfaces only. Reading
or extracting the internal package data or rules is prohibited; see
:doc:`competition-rules`.

Where to start
--------------

.. toctree::
   :maxdepth: 2
   :caption: 1. Before you start

   competition-rules
   api-key

.. toctree::
   :maxdepth: 2
   :caption: 2. Set up and develop

   quickstart
   packages
   mcp

.. toctree::
   :maxdepth: 2
   :caption: 3. Understand the game

   handbook
   rules
   failure-and-ending

.. toctree::
   :maxdepth: 2
   :caption: 4. Submit

   submission
