Competition packages
====================

Career Survival Agent is distributed through two separate PyPI packages. They
have different purposes and should not be confused. This page first describes
those two simulation packages and how to load the development dataset, and
then states the required agent platform, which is not one of the two
simulation packages.

``career-emulator-engine``
--------------------------

`career-emulator-engine <https://pypi.org/project/career-emulator-engine/>`_ is
the simulation engine. It contains the game logic and state handling, the
command line program, and the MCP server used by agents.

It provides two commands:

- ``career-emulator-engine``: load a dataset and play or test the simulation
  from the command line.
- ``career-emulator-engine-mcp``: start the MCP server through which an agent
  starts a game, observes state, and takes actions.

Install the engine with the MCP component as follows:

.. code-block:: bash

   pip install "career-emulator-engine[mcp]"

Installing the engine also installs a compatible version of the data package
as a dependency.

``career-emulator-techarena``
-----------------------------

`career-emulator-techarena
<https://pypi.org/project/career-emulator-techarena/>`_ is the data package.
It contains the development validation dataset: the public events and related
configuration with which participants develop and test their agents.

The data package does not contain a playable engine and does not provide the
competition commands by itself. It is normally installed automatically when
``career-emulator-engine`` is installed. Install it separately only when the
dataset package is required without explicitly managing the engine dependency:

.. code-block:: bash

   pip install career-emulator-techarena

Loading the development dataset
-------------------------------

After installing the engine, load the packaged development dataset as follows:

.. code-block:: bash

   career-emulator-engine update --source distribution --split dev
   career-emulator-engine play

For MCP use, start the official server with:

.. code-block:: bash

   career-emulator-engine-mcp --help

Participants using the official participation repository should normally use
its dependency and setup commands rather than installing these packages into
the system Python environment. See :doc:`quickstart`.

Development and evaluation data
-------------------------------

The ``career-emulator-techarena`` package published for participants contains
the development (``dev``) validation dataset. It is provided so that teams can
build, test, and compare agent designs locally.

The dataset and parameters used for official evaluation are not published in
the participant package and are not available for local inspection. Behaviour,
thresholds, event composition, and results in the development dataset must not
be assumed to be identical during official evaluation.

Package contents are not a participant interface. Participants must access the
simulation through the public CLI and MCP interfaces and must not inspect or
extract the packaged data in order to derive internal rules. The binding
restrictions are stated in :doc:`competition-rules`.

Required agent platform: JiuwenSwarm
------------------------------------

JiuwenSwarm is the agent platform, not one of the two simulation packages
above. The required version is `JiuwenSwarm
<https://openjiuwen.com/jiuwenswarm>`_ ``0.2.4b3`` (also written as
``0.2.4.beta3`` in the repository dependency pin; both spellings normalise to
the same version). Participants must use exactly this version. Do not
upgrade, downgrade, replace, or separately install another JiuwenSwarm
version, and do not override the version pinned by the official participation
repository. Behaviour observed with another version is not accepted as a
substitute for testing with ``0.2.4b3``.

Only JiuwenSwarm's single-agent mode may be used. Submissions must set
``"mode": "agent"`` in ``manifest.json``. The ``team`` mode is prohibited:
do not set ``"mode": "team"``, do not run an evaluated agent through
JiuwenSwarm team execution, and do not design Skills that require a leader
with multiple teammate agents. See :doc:`competition-rules` for the binding
rule and :doc:`submission` for the manifest requirements.
