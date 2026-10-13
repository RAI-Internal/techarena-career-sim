Public handbook
===============

This page reorganizes the "employee handbook" into a version that reads better
for participants. It only covers public information, i.e. the part of the rules
you can openly rely on when planning for the long term.

What is public
--------------

The public rules tell you explicitly:

- The level structure and promotion windows.
- The visible stats and roughly what they mean.
- The framework of quarterly energy actions and the quarterly main action.
- The 48-month time structure.
- The monthly salary mechanism and performance grades.
- A few hazard and failure directions.

Some things are not published, though, such as the promotion score, the
performance scoring index, hidden-hazard details, and random-event trigger
probabilities. In other words, the organization tells you roughly where the pit
is, but will not kindly draw the exact coordinates of every open manhole.

Level system
------------

The organization has ten levels, ``L1`` through ``L10``. A promotion window opens
every 6 months, but higher levels carry higher overall requirements, and the
exact thresholds are not published.

.. list-table:: Levels at a glance
   :header-rows: 1
   :widths: 12 32 56

   * - Level
     - Name
     - Public description
   * - L1
     - Junior Engineer
     - Mainly executes tasks; needs clear guidance.
   * - L2
     - Engineer
     - Can complete module-level tasks independently.
   * - L3
     - Senior Engineer
     - Owns core modules; starts taking on technical responsibility.
   * - L4
     - Staff Engineer
     - Developer of key systems with significant project impact.
   * - L5
     - Technical Expert / Team Lead
     - Owns a subsystem or a small team.
   * - L6
     - Senior Expert / Tech Lead
     - Owns a large project or a technical direction.
   * - L7
     - Technical Director / Department Tech Lead
     - Owns department-level technical strategy.
   * - L8
     - Senior Technical Director
     - Owns cross-department technical planning.
   * - L9
     - Principal Expert / Architecture Committee Member
     - Influences company-level technical direction.
   * - L10
     - Chief Architect / Technical Fellow
     - Company-level technical decisions and long-term strategy.

Visible stats
-------------

You make decisions around a set of explicit stats. They are not the whole truth,
of course, but they are already enough to decide whether you are steadily
building a record or quietly planting landmines in your own resume.

.. list-table:: Core stats visible on the panel
   :header-rows: 1
   :widths: 24 16 60

   * - Key
     - Range
     - Meaning
   * - ``Health``
     - 0 to 10
     - Physical condition; long-term overdraft causes problems.
   * - ``Dignity``
     - 0 to 10
     - Organizational recognition and self-respect; staying too low tends to go
       badly.
   * - ``Skill``
     - 0 and up
     - Your professional capability reserve.
   * - ``Network``
     - 0 and up
     - Your connection to coworkers and the organization.
   * - ``Level``
     - L1 to L10
     - Current career level.
   * - ``Output``
     - 0 and up
     - Visible performance capital the organization can see and evaluate.
   * - ``Wealth``
     - unbounded
     - Accumulated wealth.
   * - ``Energy``
     - 0 to 3
     - Quarterly action budget, spent only at the end of a quarter.
   * - ``CurrentLevelDuration``
     - 0 and up
     - How many months you have stayed at the current level.

Time structure
--------------

A full game lasts 48 months. Each month shows at most 3 story events by default,
and the overall flow is roughly:

1. Advance the month and pay the base salary according to level.
2. The system generates the month's story events from the event pool.
3. You handle events one by one and make choices.
4. At the end of a quarter, enter the quarterly energy-action phase.
5. Spend 3 ``Energy`` points; you may repeat energy actions until they run out or
   you stop.
6. Choose 1 quarterly main action, or choose not to act.
7. The system settles stats and issues warnings when necessary.
8. Every 6 months, run a formal performance review and settle the bonus.

One line is enough to remember: monthly events handle the present, quarterly
actions decide the trajectory, and the semi-annual review tallies whether, over
the recent stretch, you were actually working or just getting good at explaining
why results were inconvenient lately.
