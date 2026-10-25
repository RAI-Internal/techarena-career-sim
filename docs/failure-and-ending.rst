Failure and endings
===================

A run may end before month 48 if a failure condition is met. If the agent
completes all 48 months, the simulation produces an ending evaluation.

Early failure directions
------------------------

The handbook publishes the general failure directions but not the exact
internal thresholds, counters, consecutive-period requirements, or penalties.
The principal public risk directions are:

- health reaching zero;
- dignity remaining at a critically low level;
- accumulated hidden risks producing a serious organisational consequence;
- repeated low performance;
- network remaining at zero for an extended period;
- wealth remaining below zero for an extended period;
- skill falling materially behind organisational expectations.

These descriptions identify the nature of the risks; they do not state that a
single observation of a low value will always cause immediate failure. The
exact conditions are not public. Participants should respond to persistent
adverse statistics and warning feedback rather than wait for a failure to
occur.

Completing the run and ending evaluation
----------------------------------------

Completing the 48-month simulation does not by itself determine the final
competition ranking. The local simulation reports an ending evaluation based
on quantitative career outcomes. Official evaluation is performed under the
organisers' competition configuration, and the local result should be used as
development feedback rather than treated as a guaranteed final score.

The local report prints ``quantitative_score`` on a 0–100 scale. That number
is the career outcome. An early exit still receives a ``quantitative_score``
from the state at exit. Official live play is the mean of three runs'
``quantitative_score`` values. The 80% weight is applied once, to that mean.

The score data also includes ``competition_partial_score``, which is
``quantitative_score × 0.7`` (maximum 70). It is not shown as the run score.
It is not the live play score, and it is not multiplied by 0.80.

Official scoring is defined in :doc:`competition-rules`. Live play counts
for 80% of the version's automated score, alongside document design quality
(10%) and token efficiency (10%). A team's Stage 1 score is its highest
valid automated version score; only the top ten teams after Stage 1 advance
to expert review, where the final competition score is 70% Stage 1 score
plus 30% expert review score. A single local ending is one development
result, not a three-run average.

The quantitative ending reported by the simulation considers the following
dimensions:

.. list-table:: Quantitative ending dimensions
   :header-rows: 1
   :widths: 30 70

   * - Dimension
     - Basis of assessment
   * - Career level
     - The career level reached by the end of the run.
   * - Total wealth
     - Wealth accumulated over the 48 months.
   * - Health & dignity
     - The combined condition indicated by health and dignity.
   * - Professional skill
     - Skill accumulated over the run.
   * - Risk control
     - Whether relevant risks remained within acceptable limits.
   * - Workplace network
     - The state of the agent's organisational relationships.

The ending report states the quantitative score out of 100 and how much each
dimension above contributed to it.

What this means for design
--------------------------

A sound design should avoid persistent weakness in any principal dimension.
Maximising one statistic while allowing health, dignity, relationships, or
financial stability to deteriorate may result in early termination or a poor
ending evaluation. Long-term balance and timely correction are therefore
central to the competition task.
