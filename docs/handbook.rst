Public handbook
===============

This page summarises the public employee handbook: what information is
public, the time structure, the level system, and the visible statistics. It
states the information that participants may rely on when designing a
long-term strategy. It does not publish every internal condition used by the
simulation. The published action effects, salary, performance, and promotion
rules are in :doc:`rules`; failure directions and ending evaluation are in
:doc:`failure-and-ending`.

Public and non-public information
---------------------------------

The public information includes:

- the ten-level career structure and six-month promotion windows;
- the visible statistics and their general meanings;
- the quarterly Energy actions and quarterly main action;
- the 48-month time structure;
- the monthly salary schedule and performance grade meanings;
- the general directions of the principal failure conditions.

The following information is not published:

- exact promotion and performance formulas;
- exact thresholds and counters for failure conditions;
- hidden-risk conditions and consequences;
- event composition, trigger probabilities, and evaluation parameters.

Participants must design for incomplete information. Feedback returned during
a run may indicate increasing risk, but it does not disclose the underlying
formula or the distance to an unpublished threshold.

Time structure
--------------

A complete run lasts 48 months. By default, a month contains up to three story
events. The normal sequence is:

1. Advance the month and pay the base salary for the current level.
2. Present the month's story events.
3. Resolve the events through the available choices.
4. At the end of a quarter, enter the quarterly action phase.
5. Spend up to 3 ``Energy`` points on energy actions.
6. Select one quarterly main action, or select no main action.
7. Settle statistics and issue any applicable warnings.
8. Every six months, conduct a performance review and settle the associated
   bonus.

Monthly choices primarily determine immediate outcomes. Quarterly actions have
greater influence on the longer-term career trajectory, while the six-month
review evaluates performance over a longer period.

Level system
------------

The organisation has ten levels, from ``L1`` to ``L10``. A promotion window
opens every six months. Higher levels have higher overall requirements. Exact
promotion thresholds are not published.

.. list-table:: Levels at a glance
   :header-rows: 1
   :widths: 14 30 56

   * - Level
     - Name
     - Public description
   * - L1
     - Junior engineer
     - Carries out tasks with clear guidance.
   * - L2
     - Engineer
     - Owns modules independently.
   * - L3
     - Senior engineer
     - Owns core modules, with growing technical responsibility.
   * - L4
     - Staff engineer
     - Works on critical systems with major project impact.
   * - L5
     - Principal / team lead
     - Leads a subsystem or small team.
   * - L6
     - Senior principal / tech lead
     - Leads large programmes or sets technical direction.
   * - L7
     - Director of engineering
     - Department-level technical strategy.
   * - L8
     - Senior director
     - Cross-department technical planning.
   * - L9
     - Distinguished fellow / architecture committee
     - Company-wide technical influence.
   * - L10
     - Chief architect / fellow
     - Makes company-wide technical decisions over a long horizon.

Visible statistics
------------------

Decisions should be based on the statistics returned through the official
interface. The visible statistics do not represent every internal condition,
but they are the principal public indicators of career development and risk.

.. list-table:: Visible statistics
   :header-rows: 1
   :widths: 24 16 60

   * - Key
     - Range
     - Meaning
   * - ``Health``
     - 0 to 10
     - Physical condition. Sustained overwork may create serious risk.
   * - ``Dignity``
     - 0 to 10
     - Organisational standing and self-respect. Sustained low values are
       dangerous.
   * - ``Skill``
     - 0 and above
     - Accumulated professional capability.
   * - ``Network``
     - 0 and above
     - Professional relationships within the organisation.
   * - ``Level``
     - L1 to L10
     - Current career level.
   * - ``Output``
     - 0 and above
     - Visible work results available for organisational evaluation.
   * - ``Wealth``
     - Unbounded
     - Accumulated wealth; it may become negative.
   * - ``Energy``
     - 0 to 3
     - Quarterly action budget, available at the end of a quarter.
   * - ``CurrentLevelDuration``
     - 0 and above
     - Number of months spent at the current level.
