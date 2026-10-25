Submission requirements
=======================

This page defines what participants must submit, first for API-key
verification and then as the final evaluated submission. It is organised as:
the preliminary submission, the final submission package, the conditions that
make a submission invalid, and the checks to run before submitting. The
binding conduct rules are in :doc:`competition-rules`.

Preliminary submission
----------------------

Before an API key is issued, a team must submit the initial design and Skills
documents described in :doc:`api-key`. The preliminary submission verifies
genuine participation only. It is not scored and is not a substitute for the
final submission.

Final submission
----------------

Package the final submission as a single ZIP archive containing one top-level
``solution/`` directory. After extraction, the structure must be:

.. code-block:: text

   solution/
     manifest.json
     README.md
     presentation.mp4
     design/
       skills_design.md
       decision_report.md
     skills/
       <skill-name>/
         SKILL.md
         script/ (optional)
         reference/ (optional)
       <another-skill-name>/
         SKILL.md

At least one directory under ``skills/`` is required. Each submitted Skill
must have its own directory and a ``SKILL.md`` file. A Skill may also contain
a ``script/`` directory and a ``reference/`` directory. Both are optional.
Additional supporting files may be included inside a Skill directory where
they are required by that Skill, but they do not replace any required item
above.

The repository contains ``example_submission_structure/`` with this same
layout. That directory is a starting copy, not the submission itself. Copy it
to ``solution/`` at the repository root, then replace the sample text with
the team's own English deliverables and replace ``presentation.mp4`` with the
team's video. ``solution/`` is the working directory used by ``make play`` and
by the validation command below. It is not part of the cloned repository.
When the files are ready, package a ZIP whose top-level directory is that
filled-in ``solution/``.

Required contents
-----------------

``manifest.json``
   Identifies the team and controls how JiuwenSwarm runs the submission. It
   must contain a real team name, a submission name, a supported ``mode``, and
   any instruction required by the team's design. The ``instruction`` and
   other natural-language values must be written in English.

   .. code-block:: json

      {
        "team": "your-team-name",
        "name": "your-submission-name",
        "mode": "agent",
        "instruction": ""
      }

   ``your-team-name`` in that sample is a placeholder. A blank team name and
   this sample value are invalid. Local validation rejects both. Replace
   ``your-team-name`` with the team's real name before submitting.

   ``mode`` must be ``agent``. Only JiuwenSwarm ``0.2.4b3`` in single-agent
   mode may be used. ``"mode": "team"`` is prohibited: the JiuwenSwarm
   ``team`` mode must not be used, and a submission that requires multi-agent
   team execution is invalid. A blank or placeholder team name is also
   invalid. Here ``team`` refers only to the prohibited JiuwenSwarm run mode,
   not to the people who make up a participating team.

``README.md``
   Identifies the submission and summarises the submitted Skills. It must be
   written in English.

``design/skills_design.md``
   Explains the purpose of each Skill, how the Skills divide responsibilities,
   what information each Skill uses, and how their outputs are combined into a
   decision. It must be written in English.

``design/decision_report.md``
   Explains the team's overall decision approach, the public information and
   in-run feedback on which the approach relies, the principal risks, and how
   the design is intended to generalise beyond the development validation
   dataset. It must be written in English.

   The two ``design/`` documents are scored deliverables, not administrative
   paperwork. They do not affect the automated document design quality
   component, which is scored from the Skills themselves; instead, they are
   an important basis for the **expert review** in Stage 2 (30% of the
   weighted final score for the top ten teams), where reviewers watch
   ``presentation.mp4`` and read the design documents together with the
   design quality of the Skills.
   Write them accurately and specifically for the Skills as submitted, and
   keep them consistent with those Skills. See :doc:`competition-rules` for
   how the final score is composed.

``presentation.mp4``
   An English video from the team. Every final ZIP includes this file inside
   ``solution/``. It is required for every team. The preliminary package used to request an API key does
   not include it. The video answers all five questions below, in this order:

   1. How did you think while designing the Skills? Describe the reasoning,
      not only the finished structure.
   2. While debugging your submission, what did you find in the logs of an
      earlier version that was worth improving, and how did you change it in
      a later version?
   3. Why did you use scripts or reference files in the Skills, or why did
      you not use them?
   4. How general and robust are your Skills? If the environment settings
      change, how well can the agent adapt?
   5. What did this competition lead you to think about the relationship
      between an agent and agent Skills? What do Skills add for an agent,
      and where do they fall short?

   The video is at most ten minutes long. There is no minimum length. After
   these five topics, teams are encouraged to share anything else they want
   reviewers to hear.

   A person on camera is enough. Slides are not required. To meet the upload
   size limit, teams may reduce the video resolution. The video must keep its
   original playback speed.

   A final submission without ``presentation.mp4`` is invalid. For a team
   that reaches Stage 2, reviewers watch this file with the ``design/``
   documents and the Skills.

``skills/<skill-name>/SKILL.md``
   Contains the instructions for one Skill. The file must begin with valid YAML
   front matter containing at least ``name`` and ``description`` fields,
   followed by the Skill instructions.

   .. code-block:: yaml

      ---
      name: skill-name
      description: What this Skill decides, and when the agent should use it.
      ---

      Replace this text with the Skill instructions.

   All deliverables must be written entirely in English. This includes every
   Skill's front-matter ``description`` and instructions, and any supporting
   natural-language text included inside a Skill directory for the agent to
   read or use. A deliverable written in any other language, in whole or in
   part, is not accepted and may make the submission invalid. The spoken
   presentation in ``presentation.mp4`` must also be in English.

Invalid submissions
-------------------

The following are examples of an invalid final submission:

- the ZIP does not contain a top-level ``solution/`` directory;
- ``manifest.json``, ``README.md``, or ``presentation.mp4`` is missing;
- the ``design/`` directory is missing, or either required design document is
  missing;
- the ``skills/`` directory is missing;
- no Skill directory contains a ``SKILL.md`` file;
- a Skill's ``SKILL.md`` file is missing required front matter;
- the manifest contains a placeholder team name or unsupported run mode;
- the manifest sets ``"mode": "team"``, omits ``mode``, or sets any mode
  other than ``"mode": "agent"``;
- a Skill or design document requires JiuwenSwarm ``team`` mode or any
  JiuwenSwarm version other than ``0.2.4b3``;
- any deliverable is written wholly or partly in a language other than
  English — including the ``manifest.json`` instruction, ``README.md``,
  the spoken presentation in ``presentation.mp4``, either design document,
  a ``SKILL.md`` file, or supporting natural-language text inside a Skill
  directory.

Missing folders or files will not be supplied by the organisers. Teams should
extract the final ZIP into a clean directory and inspect the resulting
structure before submitting it.

Local validation
----------------

The participation repository provides a validation command:

.. code-block:: bash

   uv run python -m career_sim_runner validate --submission solution

This command checks the submission directory only. It does not contact
JiuwenSwarm, so a stopped instance does not fail the command or change its
exit code.

It checks the complete required file and folder structure of the
final submission: ``manifest.json``, ``README.md``, ``presentation.mp4``,
the ``design/`` directory with both ``design/skills_design.md`` and
``design/decision_report.md``, the ``skills/`` directory, and at least one
``skills/*/SKILL.md``. It also checks the manifest fields and each
``SKILL.md`` file's front matter, and reports each missing required item by
name. ``mode`` must be ``agent``. ``"mode": "team"``, a missing ``mode``,
or any other mode fails the command. A blank team name and the sample value
``your-team-name`` also fail the command. An empty ``presentation.mp4``
fails the command. The video shipped in ``example_submission_structure/``
is an empty placeholder, so validation fails until that file is replaced
with the team's video.

``make play`` may run a local game when ``presentation.mp4`` is not yet
present. This validation command still requires that file, because it checks
the final submission.

Passing local validation does not waive any other requirement in this
document. The command checks that required items are present and that
``mode`` is ``agent``. It does not certify their contents. In particular,
participants must themselves confirm that the submission was tested with
JiuwenSwarm ``0.2.4b3``, and that every deliverable —
``manifest.json`` instruction, ``README.md``, the spoken presentation in
``presentation.mp4``, both design documents, and every Skill — is written
entirely in English. The final archive must satisfy
the complete requirements above even if a local check does not inspect every
document or condition.

Revised, duplicate, and superseded versions
-------------------------------------------

Teams may submit a revised version of their work before the relevant
submission deadline. How versions are treated for scoring is defined in
:doc:`competition-rules` and summarised here:

.. important::

   - The competition week is 26 October 2026 through 1 November 2026 (UK time,
     GMT, UTC+0). Scores are collected at 24:00 on 27 October, at
     24:00 on 30 October, and at 24:00 on 1 November, then released once each
     batch has been scored. A batch ordinarily takes one or two days. When
     many teams submit, it takes longer, because each version is a full
     simulation run three times.
   - An evaluated version receives an **automated score**: 80% live play
     (the mean of three runs' ``quantitative_score``), 10% document design
     quality, and 10% token efficiency. ``competition_partial_score`` is
     ``quantitative_score × 0.7`` and is not that live play score. See
     :doc:`competition-rules`.
   - If you submit more than one version before a cutoff, only the latest
     version that has not yet been scored is evaluated. Earlier unscored
     versions are superseded and receive no score.
   - If a submitted version is **content-identical** to a version that has
     already been scored, it will **not** be scored again. Reformatting,
     renaming, repackaging, or changing only the identifying metadata does
     not create a distinct version. The automated score already issued for
     that work carries over.
   - Your team's **Stage 1 score** is the **highest valid automated version
     score issued to your team** across all score releases. A later version
     that scores lower does not replace an earlier higher automated score.
   - At the end of Stage 1, the **top ten teams** by Stage 1 score advance
     to Stage 2 expert review. Only their final competition score is then
     calculated as **70% Stage 1 score plus 30% expert review score**; teams
     ranked 11th or below receive no expert review score and no weighted
     final score. In the expert review, the ``presentation.mp4`` already in
     the ZIP, the ``design/`` documents, and the design quality of the Skills
     are the basis for judgement.

See :doc:`competition-rules` for the binding rules on evaluation, duplicate
and superseded submissions, and invalid submissions.
