Competition API key
===================

This page explains how a team obtains the API key issued for the competition,
in three steps: submit a preliminary design, pass organiser verification, and
configure the issued key. A key is issued only after the organisers have
verified a preliminary design submission. Participants must not assume that a
key will be issued without this verification. The final submission structure
that the preliminary documents later grow into is defined in
:doc:`submission`.

.. important::

   Competition week: **26 October 2026** through **1 November 2026**
   (UK time, GMT, UTC+0).

   Submit the preliminary design on the official competition website:
   https://techarena-uk.hydro.ac/

   Questions: Discord, https://discord.gg/Ds4JC3gJjj. The organisers reply
   during working hours.

Step 1: Submit the preliminary design
-------------------------------------

Before requesting a key, submit an initial, good-faith version of the team's
design and Skills documents on the official competition website,
https://techarena-uk.hydro.ac/. The preliminary submission must contain at
least:

.. code-block:: text

   preliminary/
     manifest.json
     design/
       skills_design.md
     skills/
       <skill-name>/
         SKILL.md

The preliminary ``skills_design.md`` should explain the team's understanding
of the task, the responsibilities planned for each Skill, the information the
agent will use when making decisions, and the main risks in the proposed
approach. Each preliminary ``SKILL.md`` should describe the intended purpose
and decision responsibilities of that Skill. Every preliminary deliverable
must be written entirely in English, including the ``manifest.json``
instruction, ``skills_design.md``, each Skill's front-matter ``description``
and instructions, and any supporting natural-language text for the agent.
Preliminary deliverables in any other language will not be accepted; the
organisers may request an English version before issuing an API key.

The preliminary ``manifest.json`` must already use the required competition
platform: JiuwenSwarm ``0.2.4b3`` in single-agent mode, with
``"mode": "agent"``. Do not submit a preliminary manifest with
``"mode": "team"`` or design the preliminary Skills around JiuwenSwarm
``team`` mode; that mode is prohibited for the entire competition.

This is an initial working version, not a final polished submission. It must
nevertheless represent the team's genuine proposed solution. A blank file,
placeholder text, or a document unrelated to the team's intended agent does
not establish genuine participation.

The preliminary submission is used only to verify that the team is genuinely
participating in the competition. It is not scored and does not form part of
the team's competition result. Submitting it does not replace the final
submission requirements in :doc:`submission`.

Step 2: Organiser verification
------------------------------

The organisers will review the preliminary design and Skills documents. If the
submission establishes genuine participation, the API key and connection
details will be sent by email to the team's designated contact.

If the documents are insufficient to establish genuine participation, the
organisers may request further information before issuing a key. A key should
not be treated as approved until the team receives it by email from the
organisers.

Step 3: Configure the key
-------------------------

After receiving the key, enter the values provided by the organisers in the
local ``.env`` file:

.. code-block:: bash

   cp .env.example .env

.. code-block:: text

   API_BASE="<value provided in the organiser email>"
   API_KEY="<key provided in the organiser email>"
   MODEL_NAME="<designated competition model>"

Configure only these three values. Do not add OpenRouter ``provider``,
``order``, ``only``, ``allow_fallbacks``, or any other hosting-route
preference to the local ``.env``, to JiuwenSwarm configuration, or to
submission code.

The competition API key may be used only with the model designated by the
competition. At the time of publication, the designated base model is
``deepseek-v4-flash``. If the organiser email specifies a provider-qualified
form of that model name, participants must use the name exactly as provided in
that email.

Participants must not use the competition key with another model, another
model API product, or an unrelated application. If the designated model is
unavailable or the correct model name is uncertain, ask in the Discord
channel rather than substituting another model.

Official LLM routing
--------------------

Official scoring uses the designated competition model under
organiser-controlled upstream routing. Participants must not select, pin, or
rely on a particular OpenRouter hosting provider (for example by setting a
``provider`` field on chat-completion requests). Any such preference in a
submission may be ignored or overwritten in the official evaluation
environment.

Local runs that use the competition API key may therefore see different
latency or availability from official scoring. Design Skills for the
designated model and the public game interface; do not optimise for a
specific hosting provider.

Limits and period of use
------------------------

The competition API key is subject to all of the following restrictions:

- **Maximum credit:** USD 50 per issued key.
- **Permitted period:** the competition week only, from **26 October 2026**
  to **1 November 2026** (UK time, GMT, UTC+0).
- **Permitted model:** only the designated competition model described above.
- **Permitted purpose:** development and evaluation activity for this
  competition only.
- **No participant-controlled hosting route:** OpenRouter provider routing
  for official scoring is set by the organisers, not by the submission.

The key may be suspended, expire, or stop working when the credit limit or the
permitted period is reached. Participants are responsible for monitoring their
own usage and for designing Skills that use model calls proportionately.

Do not share the key outside the registered team, publish it in a repository,
include it in a submission, or commit it to version control. If a key may have
been exposed, tell the organisers in the Discord channel immediately.

Participants should plan their testing before using a substantial part of the
credit. The organisers are not required to restore credit consumed through
repeated runs, inefficient prompts, programming errors, or use outside the
conditions above.
