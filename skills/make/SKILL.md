---
name: make
description: 'Implement a feature from its high-level GDD (written by /gd:feature): resolve its open questions, write an implementation plan, build it in verified steps behind its remote config, and update the GDD status. Offers to write the GDD first if none exists. --auto resolves open questions with the design decision rules instead of asking. Use when the user runs /gd:make or /make, or asks to build or implement a designed feature.'
argument-hint: '<feature name> [--auto]'
---

# Make a feature

`<skill-dir>` is the folder that holds this SKILL.md, and `<plugin-root>` is two folders above it. Replace them with real paths in commands. (In Claude Code they are `${CLAUDE_SKILL_DIR}` and `${CLAUDE_PLUGIN_ROOT}`.)

Input: a feature name. Output: working code that matches the GDD, an
implementation plan at the config's **Implementation plan path**, and a GDD
whose status is updated.

Read `<plugin-root>/shared/conventions.md` and the repo config first.
The repo's CLAUDE.md and AGENTS.md rules apply in full, for example branches,
change gates, reciprocal review and limits on global tools.

## 1. Find the GDD

Resolve the feature as the conventions describe.

- **No GDD:** say so, and ask with the question tool. The options are: write it
  now with `/gd:feature` and then continue (recommended); write it with
  `--list-questions` for the owner to review first and stop there; or build from
  the user's description without a GDD, which `/gd:review` then can't check
  for conformance. If the user picks the first option, follow
  `<plugin-root>/skills/feature/SKILL.md`, then come back here.
- **Status `Draft` with no owner decisions:** warn once that the design isn't
  approved, then carry on if the user says so.

## 2. Close the open questions

Read the `#open-questions` section, and also list any gap you find yourself:
a screen without a spec, a faucet without a sink, a config field with no
default, or a rule that contradicts another.

- **Default:** ask every open question with the question tool, following the
  conventions. That's at most 4 per call, so batch them if there are more.
- **`--auto`:** settle each one with the decision rules (conventions §4). Still
  ask if a question changes scope, cost or the economy.
- Write every answer back into the GDD under **Decisions**, with the date and
  `owner` or `auto: rule N`, and update the sections it affects. The GDD stays
  the source of truth, and the code follows it.

Open data requests in the GDD (`data-dr`) don't block the build. If their
data has arrived, update the GDD first (conventions §5b); otherwise list them
in the report.

Don't start the code while any question is unresolved. If a question is
deferred, build the recommended option and say so.

## 3. Plan

Write the implementation plan as markdown at the config path:

- **Scope:** the GDD revision it implements, its rules, and its screens
  `S1…Sn`.
- **Fit:** which existing systems it uses, with file paths. Reuse the repo's
  patterns for remote-config gates, parsers, ads, notifications, analytics,
  copy and debug commands. Read the code before choosing.
- **Steps:** one system per step, riskiest first. Each step has a check
  that proves it works: a test, a typecheck, or a debug command and what it
  should show.
- **QA hooks:** a debug command or menu row to reach every state of every
  screen, so `/gd:gdd` can capture it later without playing by hand.
- **Balance:** where every tunable value lives. The values come from the
  balance workbook (see `/gd:balance`) and are never invented in the code. If
  the workbook has no sheet for this feature, or doesn't exist, ask with the
  question tool: run `/gd:balance <feature>` now to create its sheets and set
  benchmarked values (Recommended); build with the GDD's values and balance
  afterwards; or build with the GDD's values and skip balance for this
  feature.

Show the plan summary. If the plan has a fork the GDD doesn't settle, ask
before building.

## 4. Build

Work step by step, in order:

- Implement the step, then run its check plus the config's typecheck, lint
  and feature tests. Fix a failure before moving on.
- Follow the config's **Remote config default**: the feature ships as the GDD
  says, usually off. The parser reads plain values only, with no A/B test
  fields (conventions §5c).
- Put all player-facing copy in the config's **UI copy source**, with the
  wording from the mockups.
- **New art** (icons, items, backgrounds): make the final images with
  `<plugin-root>/skills/asset/SKILL.md`, as one batch for the whole
  feature. If image generation is `off`, use the repo's placeholder pattern and
  list the missing assets in the report.
- Add the analytics events the GDD lists, each firing exactly once per real
  occurrence and never on retries or a resume from background.
- Keep debug-only controls out of release builds, following the repo's
  existing pattern.

## 5. Verify and update the GDD

- Run every check in the config, and the repo's verification rules in full.
  If a required step is blocked, such as a missing review tool, report it as
  blocked rather than done.
- Compare the code with the GDD: every rule, every screen and state, the
  config fields and defaults, and the events. List any difference. Fix it, or
  if the GDD was wrong, update the GDD and say so.
- Set the GDD's status to `Implemented` and add a Decisions line for any
  choice made during the build.

## 6. Report

- What was built, step by step, with the evidence: check output in short form.
- The questions settled in this run and how each was settled.
- Any difference from the GDD, and anything blocked or skipped.
- The next steps: `/gd:review <feature>`, then `/gd:gdd <feature>`.

Don't commit unless the user asks or the repo's rules require it.
