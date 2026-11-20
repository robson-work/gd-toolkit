---
name: balance
description: 'Review and redo the balance of one game feature or system, using an Excel workbook as the persistent, shared source of truth between the AI and the game designer. Proposes and creates the balance sheets when they are missing, analyzes the game''s mechanics, requests the team''s live data, researches competitor and reference-game numbers as benchmarks, plays the build itself on an attached phone or a web build (requesting debug controls when needed), respects and logs manual designer edits, detects overpowered, underpowered, scaling, synergy and exploit problems, validates with data, benchmarks and simulation (--no-data when there is no player data, such as before launch), tracks every change, and syncs approved values into the code. No GDD needed. Use when the user runs /gd:balance or /balance, or asks to balance, tune or rebalance values, stats, rewards, prices, difficulty or an economy.'
argument-hint: '<feature or system> [--report-only] [--no-data]'
---

# Balance

`<skill-dir>` is the folder that holds this SKILL.md, and `<plugin-root>` is two folders above it. Replace them with real paths in commands. (In Claude Code they are `${CLAUDE_SKILL_DIR}` and `${CLAUDE_PLUGIN_ROOT}`.)

Input: a feature or system, such as `weapons`, `daily quest rewards` or
`levels 1-50`. Output: balance sheets for it in the workbook, a report page
at *config: Balance → Report* with copy-ready prompts for any data still
needed, and, after approval, game code that matches the workbook. When that
data arrives, the same report is updated.

Read `<plugin-root>/shared/conventions.md`, the repo config and
`<skill-dir>/references/workbook-format.md` first. Each step below names the
reference it needs (all in `<skill-dir>/references/`); read it when you
reach that step, not before.

## Modes

- **Default:** uses the team's live data where it exists, and requests what's
  missing.
- **`--report-only`:** proposes changes without applying them (step 7).
- **`--no-data`:** for when there's no player data, such as a game that
  hasn't launched. It's on automatically when *config: Live data* is `none`.
  Read `no-data.md` now: it changes steps 4, 5, 7, 9 and 10.

## Core principles

- **The workbook is the balancing database.** Decide from its values, the
  team's live data and competitor benchmarks, never from fresh guesses. A
  simulation projects what a change will do; it doesn't say what the right
  number is. Write to the workbook only through the script, and never
  overwrite a value the GD set without their approval.
- **The code answers first.** When the model and the live data disagree, or
  you're unsure what a metric counts, read the code path that produces it
  before you form a hypothesis or ask: the event emitter, what its counter
  counts, the formula and any filters.
- **When your own check fails, fix it and carry on.** If calibration fails,
  a sheet is missing or data is missing, change the model, add the sheet or
  write the data prompt in the same turn. Ask only when the fix needs the
  user, such as data access or a design decision.

```sh
BB="<skill-dir>/scripts/run.sh"   # creates its own venv with openpyxl on first run
"$BB" <command> <workbook> …               # init | dump | diff | ack | owners | apply | link | sync-status | mark-synced
```

Every command prints JSON. The exit codes are: 3 for unacknowledged GD edits,
4 for a GD-owned cell without approval, 5 when the workbook is open in Excel,
and 6 when the workbook holds charts or images that would be lost. Handle each
one as the steps below describe. Never get around them, for example by
writing the file another way.

## 1. Analyze the game

Before judging any number, understand the system as the code runs it:

- Find every tunable value of the feature in the code, remote config and data
  files: stats, costs, rewards, timers, caps, weights, curves and formulas.
- Trace how they combine: damage formulas, multiplier stacking order, reward
  rolls, level gates, and what feeds what (the loops). Note the systems it
  touches and the values those already use.
- Trace what each metric depends on: what grants progress, whether currency
  can buy progress at all, and which levers only change the balance on
  hand. Step 7's lever map starts here.

**Live baseline.** The code defaults are not what players run. Before any
modelling, write a table with one row per value the analysis rests on:
Value, Code default, Live value, Source (remote-config export, analytics,
code, or `unconfirmed`), Platforms, Population (all players, a test arm or
a segment). Look in the code, the remote config and the exports for these,
and ask only about what you can't find:

- remote-config overrides, including a whole curve replaced, not only one
  changed parameter;
- values that differ by platform, or systems live on one platform only;
- flags for one segment only, such as incentivised users, testers or an
  A/B arm;
- game-speed or clock multipliers.

Where the shape of the live data can confirm a value, back-solve it, for
example progress needed per level against each candidate formula. Mark what
you can't confirm and say which conclusions depend on it.

## 2. Load the workbook, the GD's edits and the last report

If the workbook at *config: Balance → Workbook* doesn't exist yet, go to
step 3.

- If this system already has a report, read it. For every open `data-dr`
  request, look for its file under the expected name, and use what has
  arrived (step 10).
- Run `diff`. If there are pending GD edits, show them to the user in a short
  table (sheet, id, field, old → new), then run `ack`. They are now GD-owned
  and logged as `by=GD`. Treat them as intended design: balance **around**
  them. If one breaks a target, report it in step 7 and propose a change,
  but don't revert it.
- If it exits 5, ask the GD to save and close the file, and wait. If it exits
  6, explain that charts and images must move to a separate workbook.
- Run `dump` and `owners` to get the current values and the GD's cells.
- Run `sync-status`, and compare the code with `last_synced_value`. A value
  that changed in the code but not in the workbook is a code-side edit. Ask
  which one is right; don't pick silently.

## 3. Propose the balance sheets

Every system you balance gets sheets in the workbook. Don't skip this
because the values look fine or because the run is `--report-only`.

- Draft the sheet plan from step 1: one sheet per system, one row per thing,
  the input columns (blue, values from the code today), the derived columns
  (formulas such as value per cost or time to next upgrade) and the
  `Targets` rows the checks need. Show it as a table: Sheet, Rows, Inputs,
  Derived.
- **No workbook yet:** ask with the question tool: create it at the config
  path with these sheets (Recommended); create it at another path; or only
  report, which means the GD can't edit the values and the next run starts
  from scratch. On a yes, run `init`, and write the path into the config if
  it was a placeholder.
- **Missing sheet, rows or columns:** list what you'll add, then add it.
  Copying the code is not a balance change, so it needs no approval beyond
  the plan.
- Write them with `apply`: inputs as values, derived metrics as formulas with
  `{field}` placeholders, never column letters. Use the reason
  `import from code`. Then `link` every imported value to its code location
  and `mark-synced` the imported keys.

## 4. Gather evidence: our data and competitor benchmarks

Do this on every run, before setting targets. Don't wait to be asked.

**4a. Our data (Observed).** For live content, the team's own numbers beat
everything else.

- Look first in *config: Live data* and the repo's data folders for exports
  that cover the current build and the last 14 days or more. If they're
  missing or stale, pull them yourself when the config gives you access.
- Otherwise, write the request following `data-request-template.md`
  (conventions §5b). Ask for everything the analysis and a calibrated
  simulation will need in one prompt per tool, because four rounds of data
  mean four rounds of rework. Check in the code that each event is actually
  sent before asking for it (allowlists, sampling, tier filters).
- Don't wait for the data: carry on with benchmarks, mark each gap
  `DATA NEEDED: DRn`, and mark the targets that rest on benchmarks alone as
  lower confidence.
- Interrogate every number before using it: the sample size and window,
  whether the event fires when you think it does, mix shifts in traffic, the
  build filter and incomplete data for today. Follow the repo's own
  analytics rules, and state the row count and source of each number.

**4b. Competitors (Benchmark).** Research automatically, following
`benchmarks.md`, and write every number into the `Benchmarks` sheet.

**4c. Play the build (Measured).** When a playable build exists, ask to
play it on an attached phone or a web build, then play it, following
`playtest.md`. It checks the values the build really uses, the real time
between rewards and upgrades, and the edge cases and exploits. Missing
debug controls (set currency, jump to a level or day, skip time, read the
economy state) are requested with options, and added debug-only on a yes.
A playtest is one tester, not a player: never use it for player behaviour.

## 5. Set targets

Every balance judgment needs a target. Read `Targets`. For each check that has
no target, propose one, in this order:

1. targets the GD already set;
2. our observed data, for live content;
3. the reference game's benchmark;
4. the competitor benchmark range, using its median and spread;
5. the genre anchors in the repo's CLAUDE.md.

Add them with `apply`, each with a `source` naming where it came from, such
as `Benchmark (3 games: A, B, C; 2026-11-18)`. Targets set by the GD are
GD-owned like any other cell.

## 6. Detect problems

Run the checks in `balance-checks.md` that apply. Compute metrics in Python
from the dumped input values, never from a stale cached formula value, and
write them into `Targets.actual`, with `source` and `status`, through
`apply`.

Before reporting an anomaly between our numbers and the model, trace the
live metric's code path, and run the like-for-like checklist in
`balance-checks.md`. Most anomalies come from definitions that don't match.

## 7. Validate and propose

For each problem, design the smallest change that brings the metric back
within its target. Give every proposal at least one outside anchor (our data
or a benchmark), or say there isn't one. Use the strongest evidence you have:

1. **Observed:** our live data shows the problem, or a past change of the
   same value shows its effect.
2. **Benchmark:** where the proposed value sits in the competitor range.
3. **Measured:** a simulation or test, built and calibrated as the
   Simulations section of `balance-checks.md` says. Before it passes the
   calibration gate, its results are relative only.
4. **Estimated:** closed-form maths from the workbook values.

Label every result with its kind. Never present an estimate as a test
result, or a simulation run on assumed inputs as proof. A proposal that
rests only on a simulation is low confidence: say so, and name the data that
would settle it.

- **Lever map:** every proposal gets its line from `balance-checks.md` §8:
  lever → mechanism → metric it moves → why players can't route around it.
  A lever that can't fill in the last part is not a proposal yet.
- **Rank by revenue impact:** order the proposals by their likely effect on
  revenue per install at D14 and D30, in tiers High, Medium and Low, plus
  Enabler (telemetry, gating code, test rules). Give each a one-line reason,
  and say the tier is a judgement unless it was measured. When new evidence
  changes one lever's strength, re-rank the whole list.

Present them in chat as a table in tier order: Tier, Sheet/id/field,
Current, Proposed, Benchmark range, Lever → metric, Evidence (and its kind)
and Owner (AI or GD). Then:

- **AI-owned values:** apply them once the user has approved the batch.
  Where the trade-off is real, ask with the question tool and give 3 or more
  options, such as nerf it, buff its peers, or raise its cost.
- **GD-owned values:** always ask, one question per value or per group of
  related values. Send `"approved": true` only for the exact values the user
  approved.
- **`--report-only`:** stop after the table. Write nothing except the sheets
  from step 3, the `Benchmarks` rows, `Targets.actual` and the report page.

Run `apply` with a specific reason on every change, for example "smg
dps_per_1k 31% over tier-2 curve and above the 3-game benchmark; cost
1200→1500 puts it at +4%".

## 8. Sync into the game

- Run `sync-status`. For each `pending` row, change the value at its
  `code_ref` in the code or the remote-config default. Remote-config values
  that are live go to the user as a JSON payload to paste, because you don't
  change remote config yourself. The payload holds plain values only, with no
  A/B test fields. A proposal to test gets one payload per group, to set up
  in *config: A/B testing* (conventions §5c).
- Run the config's typecheck and the feature's tests, then `mark-synced` the
  rows you changed. If you played the build in step 4c, replay the changed
  values to confirm the build uses them.
- If the code can't follow the workbook, for example because it computes the
  value, update the `code_ref` and tell the user.

## 9. Report

Write the page at *config: Balance → Report* from
`<skill-dir>/assets/balance-report-template.html`, following
`report-rules.md` (sections, cards, language, charts) and the HTML rules in
the conventions. If the system already has a report, update it and bump its
revision; don't create a second file. Before every write, run the
consistency pass in `report-rules.md`, then open the page at desktop width
and at 360 px.

In chat, give the report path, the workbook path, the sheets created or
extended, the GD edits acknowledged, the changes applied, and every open data
prompt as its own code block, so it can be copied straight from the chat.
End with one line: "Send me the files, paste the data or drop them under the
names in the prompts, and I'll update the report."

## 10. When the data arrives

When the user provides data (in this session or a later run), follow
conventions §5b, plus:

- Write the observed values into the workbook through `apply`:
  `Targets.actual` with an `Observed (…)` source, and any target that should
  now come from our data instead of a benchmark.
- If a simulation depends on the data, recalibrate it and re-run every
  option that uses it in the same turn.
- Re-run the checks the data touches (step 6), and redo the proposals it
  changes (step 7). A change already applied that the data contradicts gets a
  new proposal, not a silent revert. GD-owned values still need approval.
- Update the report in place: the live baseline, the evidence and the cards,
  re-ranked if a lever's strength changed, and the request marked received.
  Remove cards the data shows were not problems; don't mark them "Resolved".

Don't commit unless asked. The workbook and its `Changelog` are the record of
what changed; add `.history/` to `.gitignore` if it isn't there.
