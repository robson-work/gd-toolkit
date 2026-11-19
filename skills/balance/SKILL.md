---
name: balance
description: 'Review and redo the balance of one game feature or system, using an Excel workbook as the persistent, shared source of truth between the AI and the game designer. Proposes and creates the balance sheets when they are missing, analyzes the game''s mechanics, requests the team''s live data, researches competitor and reference-game numbers as benchmarks, respects and logs manual designer edits, detects overpowered, underpowered, scaling, synergy and exploit problems, validates with data, benchmarks and simulation, tracks every change, and syncs approved values into the code. No GDD needed. Use when the user runs /gd:balance or /balance, or asks to balance, tune or rebalance values, stats, rewards, prices, difficulty or an economy.'
argument-hint: '<feature or system> [--report-only]'
---

# Balance

`<skill-dir>` is the folder that holds this SKILL.md, and `<plugin-root>` is two folders above it. Replace them with real paths in commands. (In Claude Code they are `${CLAUDE_SKILL_DIR}` and `${CLAUDE_PLUGIN_ROOT}`.)

Input: a feature or system, such as `weapons`, `daily quest rewards` or
`levels 1-50`. Output: balance sheets for it in the workbook, a report page
at *config: Balance → Report* with copy-ready prompts for any data still
needed, and, after approval, game code that matches the workbook. When that
data arrives, the same report is updated.

Read `<plugin-root>/shared/conventions.md` and the repo config first.
Then read `<skill-dir>/references/workbook-format.md` (the workbook
contract) and `<skill-dir>/references/balance-checks.md` (what to
check).

## Core principle

The workbook is the balancing database. You make decisions from its values,
from the team's live data and from competitor benchmarks, never from fresh
guesses. A simulation projects what a change will do; it doesn't say what
the right number is. You write to the workbook only through the script, and
you never overwrite a value the GD set without their approval.

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
- Trace how they combine: damage formulas, multiplier stacking order,
  reward rolls, level gates, and what feeds what (the loops).
- Note the systems it touches, such as currencies, other items or progression,
  and the values those already use.

## 2. Load the workbook, the GD's edits and the last report

If the workbook at *config: Balance → Workbook* doesn't exist yet, go to
step 3.

- If this system already has a report, read it. For every open `data-dr`
  request, look for its file under the expected name, and use what has
  arrived (see step 10).

- Run `diff`. If there are pending GD edits, show them to the user in a short
  table (sheet, id, field, old → new), then run `ack`. They are now GD-owned
  and logged as `by=GD`. Treat them as intended design: balance **around**
  them. If one of them breaks a target, report it in step 7 and propose a
  change, but don't revert it.
- If it exits 5, ask the GD to save and close the file, and wait. If it exits
  6, explain that charts and images must move to a separate workbook.
- Run `dump` and `owners` to get the current values and to know which ones are
  the GD's.
- **Values that differ between the code and the workbook:** run
  `sync-status`, and also compare the code with the `last_synced_value`. A
  value that changed in the code but not in the workbook is a code-side edit.
  Ask which one is right; don't pick silently.

## 3. Propose the balance sheets

Every system you balance gets sheets in the workbook. Don't skip this
because the values look fine or because the run is `--report-only`.

- Draft the sheet plan from step 1: one sheet per system, one row per thing,
  the input columns (blue, values from the code today) and the derived
  columns (formulas such as value per cost or time to next upgrade), plus the
  `Targets` rows the checks need. Show it as a short table: Sheet, Rows,
  Inputs, Derived.
- **No workbook yet:** ask with the question tool. The options are: create
  the workbook at the config path with these sheets (Recommended); create it
  at another path; or don't create one and only report, which means the GD
  can't edit the values and the next run starts from scratch. On a yes, run
  `init` and write the path into the config if it was a placeholder.
- **Workbook exists, but the system has no sheet, or rows or columns are
  missing:** list what you'll add, then add it. Adding rows and sheets that
  copy the code is not a balance change, so it needs no approval beyond the
  plan.
- Write them with `apply`: inputs as values, derived metrics as formulas with
  `{field}` placeholders, never column letters (see workbook-format.md). Use
  the reason `import from code`.
- **Link every imported value to its code location** with `link`, then
  `mark-synced` the imported keys, because the code and the workbook match at
  that point.

## 4. Gather evidence: our data and competitor benchmarks

Do this on every run, before setting targets. Don't wait to be asked.

### 4a. Request the team's data (Observed)

For content that's live, the team's own numbers beat everything else.

- Look first in *config: Live data* and the repo's data folders for exports
  that cover the current build and the last 14 days or more.
- If they're missing or stale, pull them yourself when the config gives you
  access (such as a BigQuery export or a bucket). Otherwise, write a data
  request for each one, as conventions §5b describes: a copy-ready prompt
  naming the tool, the report, the metric, the filters, the absolute date
  range, the minimum sample, the CSV columns and the file name to save it
  as. Don't wait for the data: carry on with benchmarks, mark each gap
  `DATA NEEDED: DRn`, and mark the targets that rest on benchmarks alone as
  lower confidence.
- Interrogate every number before using it: the sample size and window,
  whether the event fires when you think it does (retries, resume from
  background), mix shifts in traffic, the build filter, and incomplete data
  for today. Follow the repo's own analytics rules where they exist, and
  state the row count and source of each number you use.

### 4b. Research competitors (Benchmark)

Research automatically. Don't ask first.

- **Which games:** the reference game from the config, plus 2–4 games that
  rank high in the same genre now, starting with the "also considered" list
  from the config's reference-game line. Use WebSearch where it's available.
- **What to find:** the same values this system tunes. For example: prices
  and pack sizes, reward amounts and cadence, timers and caps, cost and
  income curves, energy or lives, ad reward caps, and difficulty pacing.
- **Where to look, from most to least reliable:** official patch notes and
  store listings (IAP prices), datamined or public config, wikis, and
  deconstructions such as Deconstructor of Fun, GameRefinery, Naavik or
  mobilegamer.biz. Use forum and video sources only when nothing else exists,
  and mark them low confidence.
- **Privacy:** a search names the competitor games and the genre. It never
  names this repo's game, its unreleased features or its internal numbers.
- Normalize the units before comparing: per minute of play, per session, per
  day, or a USD price tier. Note the context of each number, such as the
  level, the day or the tier.
- Write each number into the `Benchmarks` sheet with `apply` (reason: `research`),
  with its game, source URL, the date you accessed it and a confidence level
  (high, medium or low).
- One game is a reference, not a benchmark. A benchmark range needs at least
  two games.
- If WebSearch isn't available, say so, ask the user for competitor numbers
  they have, and fall back on the genre anchors in the repo's CLAUDE.md.

## 5. Set targets

Every balance judgment needs a target. Read `Targets`. For each check that has
no target, propose one, in this order:

1. targets the GD already set;
2. our observed data, for live content;
3. the reference game's benchmark;
4. the competitor benchmark range, using its median and spread;
5. the genre anchors in the repo's CLAUDE.md.

Add the targets with `apply`, and give each one a `source` that names where
it came from, such as `Benchmark (3 games: A, B, C; 2026-11-18)`. Targets set
by the GD are GD-owned like any other cell.

## 6. Detect problems

Run the checks in `balance-checks.md` that apply: power and value curves,
scaling, synergies and exploits, economy flow (the non-payer, the 10x failer
and the hoarder), difficulty, new content against existing content, and our
values against the benchmarks.

Compute metrics in Python from the dumped input values. Don't trust a stale
cached formula value. Write the results into `Targets.actual`, with `source`
and `status`, through `apply`.

## 7. Validate and propose

For each problem, design the smallest change that brings the metric back
within its target. Back it with the strongest evidence you have, and give
every proposal at least one outside anchor (our data or a benchmark), or say
there isn't one:

1. **Observed:** our live data shows the problem, or a past change of the
   same value shows its effect.
2. **Benchmark:** where the proposed value sits in the competitor range.
3. **Measured:** the repo's simulations or tests (*config: Simulations and
   tests*). If none exists and the question needs one, write a small Python
   simulation in the scratchpad, such as a Monte Carlo of reward rolls or a
   30-day economy for each player type. Feed it observed or benchmark
   inputs, such as the real attempts-per-level distribution. Label any input
   you assumed, and report the seed and number of runs.
4. **Estimated:** closed-form maths from the workbook values.

Always label each result Observed, Benchmark, Measured or Estimated. Never
present an estimate as a test result, and never present a simulation run on
assumed inputs as proof. A proposal that rests only on a simulation is low
confidence: say so, and name the data that would settle it.

Present the proposals as a table with the columns Sheet/id/field, Current,
Proposed, Benchmark range, Why, Evidence (and its kind) and Owner (AI or GD).
Then:

- **AI-owned values:** apply them once the user has approved the batch.
  Where the trade-off is real, ask with the question tool and give 3 or more
  options, such as nerf it, buff its peers, or raise its cost.
- **GD-owned values:** always ask, one question per value or per group of
  related values. Send `"approved": true` only for the exact values the user
  approved.
- **`--report-only`:** stop after the table. Write nothing except the sheets
  from step 3, the `Benchmarks` rows, `Targets.actual` and the report page.

Then run `apply` with a reason on every change. The reason should be
specific, for example "smg dps_per_1k 31% over tier-2 curve and above the
3-game benchmark; cost 1200→1500 puts it at +4%".

## 8. Sync into the game

Once the changes are applied to the workbook:

- Run `sync-status`. For each `pending` row, change the value at its
  `code_ref` in the code or remote-config default. Remote-config values that
  are live go to the user as a payload to paste: give them the JSON, because
  you don't change remote config yourself.
- Run the config's typecheck and the feature's tests, then `mark-synced` the
  rows you changed.
- If a code change can't follow the workbook, for example because the code
  computes the value, update the `code_ref` and tell the user.

## 9. Report

Write the report page at *config: Balance → Report*, starting from
`<skill-dir>/assets/balance-report-template.html` and following the HTML
rules in the conventions. If the system already has a report, update it and
bump its revision; don't create a second file. It holds:

- In short: at most 4 bullets.
- The evidence used: the data exports (source, range, rows), the games
  researched, and the simulations (seed, runs, which inputs are assumed).
- Findings, each with its evidence kind, and proposals with their status
  (applied, approved by GD, or pending approval).
- What was synced to code, and the remote-config payload the user has to
  push, with a Copy button.
- **Data needed:** one copy-ready prompt per open request (conventions §5b).
- What to watch after release: the metric, its baseline and its source.

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
- Re-run the checks the data touches (step 6), and redo the proposals it
  changes (step 7). A change already applied that the data contradicts gets a
  new proposal, not a silent revert. GD-owned values still need approval.
- Update the report in place: the evidence, findings and proposals, and the
  request marked received.

Don't commit unless asked. The workbook and its `Changelog` are the record of
what changed; add `.history/` to `.gitignore` if it isn't there.
