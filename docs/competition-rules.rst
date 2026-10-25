Competition rules and fair play
===============================

This page is the binding statement of the competition requirements and
prohibited conduct for Career Survival Agent. It is organised in four parts:

1. the required platform, run mode, and language of deliverables;
2. how official evaluation and scoring work;
3. fair play: permitted interfaces and the definitions of prohibited conduct
   (the detailed cheating definitions); and
4. duplicate and invalid submissions, and how to ask the organisers about an
   uncertain method.

Participants must comply with this page, :doc:`submission`, and any later
written clarification issued by the organisers.

.. warning::

   Read the detailed definitions of prohibited conduct on this page in full.
   The examples in each section illustrate the prohibitions; they do not
   narrow them. The organisers will carefully inspect submissions manually
   after the competition, and only the organisers' final interpretation and
   decision determine whether conduct constitutes cheating or another rule
   breach, and whether a submission is invalid or excluded from scoring.

Required JiuwenSwarm version and run mode
-----------------------------------------

Participants must use JiuwenSwarm version ``0.2.4b3`` exactly. No other
version may be used to develop, test, or run a submission, and participants
must not override the version pinned by the official participation
repository. Results obtained with another JiuwenSwarm version do not
establish that a submission works under the official configuration.

Only JiuwenSwarm's single-agent mode is permitted. Every preliminary and
final ``manifest.json`` must set ``"mode": "agent"``. Use of the JiuwenSwarm
``team`` mode is prohibited. In particular, participants must not:

- set ``"mode": "team"`` in a preliminary or final submission;
- run an evaluated or evaluation-representative agent through JiuwenSwarm
  team execution;
- design a Skill, prompt, design document, or decision procedure that
  requires a leader agent coordinating multiple teammate agents, parallel
  role-based teammate execution, or any other capability available only in
  ``team`` mode.

This restriction applies to the JiuwenSwarm execution mode. It does not
prohibit several people from working together as one participating team.

A submission that uses ``team`` mode, depends on ``team`` mode, or was
developed against an unapproved JiuwenSwarm version may be treated as invalid
or excluded from scoring.

Language of deliverables
------------------------

All deliverables must be written in English. This requirement applies to
every natural-language file in both the preliminary and the final submission,
including:

- the ``instruction`` and other natural-language values in ``manifest.json``;
- ``README.md``;
- the spoken presentation in ``presentation.mp4``;
- ``design/skills_design.md`` and ``design/decision_report.md``;
- every ``skills/<skill-name>/SKILL.md``, including the front-matter
  ``description`` and the Skill instructions; and
- any supporting natural-language text included inside a Skill directory and
  intended to be read or used by the agent.

Deliverables written wholly or partly in another language will not be
accepted. Do not place non-English instructions or explanations in supporting
files, comments, or other parts of a deliverable in order to circumvent this
requirement. Code, identifiers, file paths, tool names, proper names, and
literal strings that must match the official interface are not themselves
natural-language prose, but they are not a substitute for the required
English text.

A preliminary submission containing a non-English deliverable may not be
accepted as establishing genuine participation. A final submission containing
a non-English deliverable may be treated as invalid or excluded from
scoring.

Official evaluation, score releases, and final score
----------------------------------------------------

.. important::

   **Evaluation has two stages — please read carefully.**

   **Stage 1 is automated scoring for all teams.** Each evaluated version
   receives an automated score made of **live play 80%**, **document design
   quality 10%**, and **token efficiency 10%**. The live play component is
   the arithmetic mean of three official runs of that version, using each
   run's ``quantitative_score`` (0–100). Scores are released
   twice during the competition week (26 October 2026 through 1 November
   2026) and once more after it ends. A team's Stage 1 score is the highest
   valid automated version score issued to that team.

   **Only the top ten teams after Stage 1 enter Stage 2.** When Stage 1
   scoring ends, teams are ranked by their Stage 1 score. The ten
   highest-ranked teams advance to expert review. Teams ranked 11th or below
   do not enter Stage 2 and do not receive an expert review score or a
   weighted final score.

   **Stage 2 is expert review for the top ten teams only.** For each
   advancing team, the final competition score is:

   .. code-block:: text

      final competition score = 0.70 * Stage 1 automated score
                               + 0.30 * expert review score

   The detailed rules below define the components, which version is
   evaluated at each release, and what happens to identical, superseded,
   and already-scored versions.

**The two stages at a glance.**

.. list-table::
   :header-rows: 1
   :widths: 22 22 56

   * - Stage
     - Who takes part
     - What happens
   * - Stage 1: automated scoring
     - All teams with a valid submission
     - Each evaluated version is scored automatically (live play 80%,
       document design quality 10%, token efficiency 10%). A team's Stage 1
       score is its highest valid automated version score across all score
       releases.
   * - Selection
     - All teams
     - At the end of Stage 1, teams are ranked by their Stage 1 score. The
       **top ten teams** advance to Stage 2; teams ranked 11th or below go
       no further.
   * - Stage 2: expert review
     - The top ten teams only
     - Expert reviewers score each advancing team's submission, including
       the ``presentation.mp4`` already in its ZIP. The final competition
       score is ``0.70`` × Stage 1 automated score plus ``0.30`` × expert
       review score.

**Automated score of one evaluated version.** Live play, document design
quality, and token efficiency are each on a 0–100 scale before the weights
below are applied. Each weight is applied once.

.. code-block:: text

   automated version score = 0.80 * live play score
                           + 0.10 * document design quality score
                           + 0.10 * token efficiency score

- **Live play score (80%).** The version is run three separate times. Each
  run's score is its ``quantitative_score``, the career outcome on a 0–100
  scale. An early exit still receives one, from the state at exit. The live
  play score is the mean of the three runs:

  .. code-block:: text

     live play score = (quantitative_1 + quantitative_2 + quantitative_3) / 3

  The score report also includes ``competition_partial_score``, which is
  ``quantitative_score × 0.7`` (maximum 70). It is not shown as the run
  score, and it is not the live play score. Do not multiply it by 0.80: the
  0.7 factor is already inside it, and the 80% weight belongs on
  ``quantitative_score``.

- **Document design quality score (10%).** Each ``SKILL.md`` is scored from
  0 to 100 as instructions for the agent. The submission's score is the
  mean of its Skills. The ``design/`` documents are not part of this
  component; they are read in the expert review below.

  A high score means the agent can find the Skill and follow it. The
  description says what the Skill does and when to use it. The steps are
  executable: priorities and decision criteria, including what to do near a
  limit. The strategy matches the published rules and looks across the 48
  months. The same guidance still applies when the event wording or order
  changes.

  A Skill scores 0 if it has no valid front matter, is empty or unrelated
  to its description, contradicts the game, or contains prohibited conduct
  such as a fixed answer for a named event.

- **Token efficiency score (10%).** Each run is scored from total tokens
  divided by months survived. Wall-clock time is not scored. The version's
  score is the mean of its three runs.

  .. code-block:: text

     tokens_per_month = total_tokens / survival_months
     500,000 or fewer   → 100
     3,000,000 or more  → 0
     otherwise          → 100 * (3,000,000 - tokens_per_month) / 2,500,000

  A run that ends before month 48 is capped at 50 on this term, so an early
  exit cannot outscore a completed run by using fewer tokens. A run with no
  token count or no survival length scores 0.

For teams that reach Stage 2, the effective weights in the weighted final
competition score are:

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - Component
     - Weight in its part
     - Effective weight in final score
   * - Live play
     - 80% of automated score
     - 56%
   * - Document design quality
     - 10% of automated score
     - 7%
   * - Token efficiency
     - 10% of automated score
     - 7%
   * - Expert review (Stage 2, top ten only)
     - —
     - 30%

The 70% weight in the Stage 2 formula applies to the whole Stage 1
automated score. It is not applied to a single run, and it is not the 0.7
inside ``competition_partial_score``.

For example, three runs with ``quantitative_score`` 60, 65, and 51 have a
live play score of ``(60 + 65 + 51) / 3 = 58.67``. The same runs also show
``competition_partial_score`` 42, 45.5, and 35.7, because each is the
quantitative score times 0.7. Those partial numbers are not used in the
formula below. With a document design quality score of 70 and a token
efficiency score of 50, the automated score is
``0.80 * 58.67 + 0.10 * 70 + 0.10 * 50 = 58.94``. If that is the team's
highest valid automated score, the team finishes Stage 1 in the top ten, and
its expert review score is 90, its final competition score is
``0.70 * 58.94 + 0.30 * 90 = 68.26``.

**Stage 2: expert review score (top ten teams only).** After Stage 1
scoring ends, expert reviewers award an expert review score to each of the
ten advancing teams for its submission. Teams outside the top ten are not
expert-reviewed. For an advancing team, this score accounts for 30% of the
final competition score:

.. code-block:: text

   final competition score = 0.70 * Stage 1 automated score
                           + 0.30 * expert review score

The expert review is a judgement of the submission as a designed solution,
not a re-run of the simulation. Reviewers use the ``presentation.mp4`` in
the final ZIP, the documents in ``design/`` — ``design/skills_design.md``
and ``design/decision_report.md`` — and the design quality of the Skills
themselves. From the video and the design documents they look for the
team's intended decision approach, how the Skills divide responsibilities,
which public information and in-run feedback the approach relies on, the
principal risks the team identified, and how the design is intended to
generalise beyond the development validation dataset; they read that
account together with what the submitted Skills actually say and do.

Teams should therefore treat the ``design/`` documents as part of the
scored deliverable, not as administrative paperwork: write them accurately
and specifically for the submitted Skills, and keep them consistent with
the Skills as submitted. A design document that is vague, copied from a
template, or inconsistent with the submitted Skills gives reviewers little
to credit, however polished its presentation. No separate sub-weights for
the elements of the expert review are published.

**Video presentation.** Every final ZIP includes ``solution/presentation.mp4``.
It is part of the first final submission, not a file added after the Stage 1
ranking. The preliminary package for an API key does not include it. The
video is in English and answers all five questions below, in this order:

1. How did you think while designing the Skills? Describe the reasoning,
   not only the finished structure.
2. While debugging your submission, what did you find in the logs of an
   earlier version that was worth improving, and how did you change it in a
   later version?
3. Why did you use scripts or reference files in the Skills, or why did you
   not use them?
4. How general and robust are your Skills? If the environment settings
   change, how well can the agent adapt?
5. What did this competition lead you to think about the relationship
   between an agent and agent Skills? What do Skills add for an agent, and
   where do they fall short?

The video is at most ten minutes long. There is no minimum length. After
these five topics, teams are encouraged to share anything else they want
reviewers to hear.

A person on camera is enough. Slides are not required. To meet the upload
size limit, teams may reduce the video resolution. The video must keep its
original playback speed.

A final submission without this file is invalid. See :doc:`submission`.

**Score-release schedule.** Times are UK time (GMT, UTC+0). 24:00 is
midnight at the end of that calendar day. The competition week is 26 October
2026 through 1 November 2026.

.. list-table::
   :header-rows: 1
   :widths: 28 36 36

   * - Release
     - Submission cutoff
     - When scores are published
   * - Interim release 1
     - 24:00, 27 October 2026
     - As soon as that batch is scored
   * - Interim release 2
     - 24:00, 30 October 2026
     - As soon as that batch is scored
   * - Final release
     - 24:00, 1 November 2026
     - After the competition week, once that batch is scored

A release ordinarily follows its cutoff by one or two days. Each scored
version is a full simulation, repeated three times. When many teams submit,
scoring takes longer. Please allow that extra time.

**Which version is evaluated at a score release.** At each cutoff the
organisers evaluate the latest version that a team has submitted before
that cutoff and that has not yet been scored. If a team submits more than
one version before the cutoff, only the latest unscored version is
evaluated. Earlier unscored versions are superseded and receive no score.

**Content-identical versions are not scored again.** If a submitted version
is content-identical to a version that has already been scored, it will not
be evaluated again. The automated score already issued for that work carries
over and remains one of the team's issued automated version scores. Changing
a file name, archive name, team label in metadata, formatting, or packaging
does not make an otherwise identical work a new version for scoring purposes.

**Stage 1 result and selection for Stage 2.** Every distinct, valid version
that is scored receives its own automated version score. A team's Stage 1
score is the highest of all valid automated version scores issued to that
team at the two interim score releases and the final score release. A later
version that scores lower does not replace or reduce an earlier higher
automated score. For example, if a team's automated version scores are 70
and then 65 at the two interim releases and 80 at the final release, its
Stage 1 score is 80; if the final version had scored 60 instead, its Stage
1 score would remain 70. A score that the organisers invalidate because the
submission is invalid or breaches these rules is not a valid score and does
not count towards the Stage 1 score.

When Stage 1 scoring ends, all teams are ranked by their Stage 1 score and
the **top ten teams advance to Stage 2** for expert review. Only for those
ten teams is the Stage 1 score combined with an expert review score using
the 70%/30% formula above to produce a weighted final competition score.
Teams ranked 11th or below keep their Stage 1 score as their result of the
automated stage; they are not expert-reviewed and no weighted final score
is calculated for them.

No single local run determines any of these scores. A score obtained from
one local run, including a score read with ``make score``, is development
feedback only: it is neither an official live play score (which averages
three official runs), nor an automated version score, nor a Stage 1 score,
nor a weighted final score. Participants should therefore design for
consistent performance across repeated runs rather than optimise for one
favourable run.

Official model and LLM routing
------------------------------

Official evaluation uses only the designated competition model. Participants
must set ``MODEL_NAME`` exactly as provided by the organisers (see
:doc:`api-key`). At the time of publication, the designated base model is
``deepseek-v4-flash``.

Upstream hosting for that model during official scoring is controlled by the
organisers. Participants must not:

- configure OpenRouter provider preferences such as ``provider``, ``order``,
  ``only``, ``allow_fallbacks``, or an equivalent field in Skills, prompts,
  scripts, JiuwenSwarm configuration, or other submission material in order
  to select a specific hosting provider;
- rely on a particular OpenRouter hosting provider being used during
  official scoring; or
- use the competition API key with a model other than the designated
  competition model.

Any participant-supplied provider preference may be ignored or overwritten
by the official evaluation environment. Differences in local latency or
availability under the competition API key do not by themselves establish a
scoring defect.

Scope of the prohibitions
-------------------------

The prohibitions in the following sections apply to everything submitted and
used for the competition, including Skills, ``SKILL.md`` files, supporting
files, the ``manifest.json`` instruction, prompts, design documents, scripts,
and any other text or code on which the agent relies.

Conduct is prohibited whether it is stated directly or indirectly, appears in
an example or comment, is encoded, translated, obfuscated, split across files,
or designed to take effect only during an official run. The sections below
describe the prohibited situations: using non-official interfaces, hard-coded
event answers, hard-coded rules or thresholds, prompt injection and rule
evasion, and dangerous scripts or other harm to the evaluation environment.

Official interfaces only
------------------------

Agents may interact with the simulation only through the five official MCP
tools:

- ``new_game``
- ``observe``
- ``take_action``
- ``check_latest_logs``
- ``show_employee_handbook``

The MCP log resource may be used where it is exposed by the official server.
Participants may also use the public command line interface for manual testing
and may inspect outputs generated by their own runs.

The following conduct is prohibited:

- unpacking, extracting, decompiling, reverse engineering, or directly reading
  the contents of the ``career-emulator-engine`` or
  ``career-emulator-techarena`` packages in order to obtain event data, rules,
  formulas, thresholds, trigger conditions, scoring details, or other internal
  information that is not published in these documents;
- reading the installed package files, packaged ``.data`` files, source code,
  local simulation database, or internal state files instead of using the
  official MCP tools;
- modifying the engine, dataset, simulation database, logs, scores, or run
  artifacts in order to affect an evaluation result;
- bypassing the MCP server or accessing the closed evaluation dataset;
- using information obtained through any of the above methods in an agent,
  Skill, prompt, design document, or decision procedure.

A breach of this section may result in the submission being treated as invalid
or excluded from scoring.

Prohibited hard-coded answers, rules, and thresholds
----------------------------------------------------

Submissions must make decisions from the state, event text, choices, logs, and
other information returned through the official interfaces during the current
run. Submissions must not encode internal knowledge obtained from the
development dataset or package contents.

In particular, submissions must not contain:

- fixed decisions keyed to event identifiers, event titles, dataset file names,
  or memorised event sequences;
- look-up tables that reproduce the contents or outcomes of the development
  dataset;
- unpublished thresholds, formulas, trigger conditions, score calculations, or
  event probabilities presented as known rules;
- decision logic designed to recognise a specific development event and return
  a predetermined answer rather than assess the information visible to the
  agent at that point in the run.

For clarity: an instruction such as "when this named event or this quoted plot
situation appears, choose this option" is a prohibited hard-coded answer,
even if the event name is paraphrased or the mapping is split across files.
Likewise, presenting a number as the simulation's promotion, failure,
hidden-risk, or scoring threshold is prohibited when that threshold is not
published in these documents. Whether content is prohibited under this section
does not depend on whether it is accurate, whether it matches the evaluation
dataset, how it was arrived at, or how it is described in the submission.

General strategies based on the public documentation are permitted. For
example, a Skill may instruct the agent to consider low health, sustained low
dignity, inadequate savings, or an imbalance between output and wellbeing when
choosing an action. Such guidance must remain applicable when event wording,
event order, parameter values, or the evaluation dataset changes.

Use the public employee handbook and the feedback produced by a run as the
basis for strategy. Do not assume that a threshold, formula, or pattern noticed
in the development validation dataset will remain unchanged during official
evaluation.

Prompt injection, manipulation, and rule evasion
------------------------------------------------

Submissions must not contain instructions intended to make the agent, the
model, the MCP server, the evaluator, or a reviewer act outside the permitted
competition process. In particular, participants must not include instructions
that attempt to:

- ignore, override, or conceal violations of system, developer, organiser, or
  competition instructions;
- obtain hidden prompts, internal package or evaluation data, credentials,
  scoring details, or other information that is not returned through the
  official interfaces;
- manipulate scores, logs, agent notes, run artifacts, or the evaluation
  process instead of making decisions through the official MCP tools;
- exploit an error, loophole, or unexpected behaviour in order to bypass the
  simulation or these rules; or
- treat story text, logs, files, web content, or other untrusted content as
  instructions that take priority over the competition rules.

This prohibition also covers indirect, encoded, translated, obfuscated,
conditional, or multi-step instructions designed to evade review or to
activate prohibited behaviour later.

Dangerous scripts and evaluation-environment harm
-------------------------------------------------

Submissions must not include scripts, commands, macros, configuration, or tool
instructions that could damage or interfere with the evaluation environment.
In particular, participants must not include anything that is intended or
reasonably able to:

- delete, overwrite, move, corrupt, or encrypt files or data, including
  destructive operations equivalent to ``rm -rf`` in any language or shell;
- change permissions or ownership, run with elevated privileges, stop
  processes or services, or create persistence;
- download, install, or execute unauthorised software, or make unauthorised
  network requests;
- read or disclose credentials, tokens, API keys, environment files, SSH keys,
  browser data, or other secrets;
- access paths outside the permitted submission and run outputs;
- modify the simulation engine, dataset, packages, simulation database, logs,
  scores, or run artifacts, or conceal traces of such activity.

A dangerous script or command does not become acceptable merely because it is
commented out, described as an example, disabled, or placed in a supporting
file. If a submitted design has no need to execute code in the evaluation
environment, do not include executable scripts in the Skills.

Duplicate and superseded submissions
------------------------------------

Content-identical submissions will be scored only once: a version that is
content-identical to an already-scored version is not evaluated again, and
the score already issued for that work carries over. Changing a file name,
archive name, team label in metadata, formatting, or packaging does not make
an otherwise identical submission a separate entry for scoring purposes.
This applies regardless of whether the duplicate is submitted accidentally
or through more than one channel.

A genuinely revised version is not a duplicate. If it is submitted before a
score-release cutoff and the team's previous version has not yet been
scored, only the revised version will be evaluated and the earlier version
is superseded without a score. If the previous version has already been
scored, its issued automated score stands and the revised version may be
scored at a later release; the highest issued valid automated score is
carried into the team's final score, as defined under "Official evaluation,
score releases, and final score" above.

Invalid submissions
-------------------

A submission that does not follow the required directory structure in
:doc:`submission` is invalid and may receive no score. Missing required folders
or files will not be inferred or reconstructed by the organisers.

The organisers may also treat a submission as invalid if it cannot be loaded by
the official evaluation environment, sets ``"mode": "team"`` or otherwise
depends on JiuwenSwarm ``team`` mode, depends on a JiuwenSwarm version other
than ``0.2.4b3``, contains a deliverable written wholly or partly in a
language other than English, depends on prohibited access to the simulation
packages, or breaches the fair-play requirements above.

Interpretation and questions
----------------------------

The organisers retain the final right to interpret these rules, the competition
documents, the validity of a submission, and the treatment of conduct not
expressly addressed in the documents.

If a document is ambiguous, incomplete, or silent on a proposed method,
participants must ask in the Discord channel before using that method:
https://discord.gg/Ds4JC3gJjj
The organisers reply there during working hours. The absence of an express
prohibition is not permission. Participants must not rely on an assumption
that an unaddressed method is allowed.

Only a reply from the organisers in that channel should be relied upon as
approval for an otherwise uncertain method. The organisers are not responsible
for consequences arising from an assumption that a participant did not ask
for clarification in advance, including loss of score, invalid submission, or
exclusion from evaluation.
