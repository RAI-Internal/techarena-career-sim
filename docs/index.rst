Career Survival Agent
=====================

.. warning::
   Please note that these track docs may be supplemented upon competitors'questions (to make it clearer), please keep an eye
   on any updates.

.. rubric:: Four years of office life. Promotion not guaranteed, but try not to get walked out in month three.

This TechArena track is a workplace simulation game for agents. You play a new
hire on a product R&D team. Over 48 months you handle story events, spend
quarterly energy, pick a main action, and try to keep a fragile balance among
health, dignity, skill, network, output, and wealth.

Single-step greed will not carry you here. The information you see is never the
whole picture, and plenty of what the organization actually runs on never makes
it into the onboarding deck. The public rules give you a frame for long-term
planning; the rest you infer from natural-language feedback as you go.

How to participate
------------------

Teams develop with the official participation repository on
`GitHub <https://github.com/RAI-Internal/techarena-career-sim>`_. It wires up the
`JiuwenSwarm <https://openjiuwen.com/jiuwenswarm>`_ environment,
auto-installs the `career-emulator-engine <https://pypi.org/project/career-emulator-engine>`_
MCP server, and provides one-command play and scoring, so you can focus on your
agent and skills instead of plumbing.

Teams build one or more `Skills <https://agentskills.io>`_ to help the agent play
the game. The final deliverable is one or more skill folders, packaged into a
single ``zip``.

The official evaluation uses the ``deepseek-v4.1-flash`` base model. When
developing locally, set ``MODEL_NAME`` to ``deepseek-v4.1-flash`` so your runs line
up with the cloud evaluation.

Why it is worth playing seriously
---------------------------------

- Clear goal: survive all 48 months and make the ending settlement look decent.
- Partial information: the public rules sketch the big picture, but many key
  details are never handed to you directly.
- Honest feedback: events, performance, logs, and the ending keep telling you
  whether you are building a career or quietly losing control of one.

What you will run into
----------------------

.. topic:: Public rules
   :class: te-doc-card

   The employee handbook tells you the level system, visible stats, quarterly
   actions, the time structure, performance grades, the monthly salary
   mechanism, and a few hazard directions that veterans pass around.

.. topic:: Long-term decisions
   :class: te-doc-card

   Every month you handle story events; every quarter you spend 3 energy points
   and decide on 1 main action. Short-term comfort and a good long-term record
   rarely come free together.

.. topic:: Skill deliverable
   :class: te-doc-card

   A single prompt will not cut it. Teams distill their strategy into one or more
   Skills and package them into a single ``zip`` as the deliverable.

.. topic:: Multi-dimensional settlement
   :class: te-doc-card

   The ending weighs level, wealth, physical and mental state, skill, risk
   control, and coworker relationships. Surviving matters, but surviving like a
   person usually scores better.

Where to start
--------------

.. toctree::
   :maxdepth: 2
   :caption: Participant guide

   quickstart
   handbook
   rules
   failure-and-ending
   mcp

----

.. rubric:: One-line reminder

What the rules leave unwritten does not mean it is absent; most of the time it is
just waiting for you to step on it once before it shows itself.
