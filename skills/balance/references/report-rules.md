# Balance report rules

The defaults for the report page. They exist because each one was asked
for, one turn at a time, in real reviews.

## Sections

The template's sections, in order. Delete the ones that are empty.

- **In short:** at most 4 bullets.
- **Live baseline** (SKILL.md step 1), with its unconfirmed values marked.
- **Evidence:** the branch analysed, the data exports (source, range,
  rows), the games researched, the agent playtest, the segment definitions,
  and the simulations: seed, runs, what is calibrated and to which data,
  what isn't, and which inputs are assumed or fitted.
- **Recommendations:** the cards (below), in tier order.
- **Enablers:** telemetry, gating code, test-evaluation rules.
- **Roadmap:** every card and enabler placed in this order:
  1. releases already in progress (newer branches with unreleased work);
  2. measurement and telemetry;
  3. bug fixes;
  4. remote-config test waves: independent splits, each read on the
     segment it targets;
  5. changes that need a build (code constants) and new features;
  6. later content.
- **Sync:** what was synced to code, and the remote-config payload the user
  has to push, with a Copy button. Plain values only; a test gets one
  payload per group, named outside the JSON (conventions §5c).
- **Data needed:** one copy-ready prompt per open request (conventions §5b).
  With `--no-data`, the data plan from `no-data.md` instead.
- **Watch after release:** the metric, its baseline and its source.
- **Workbook sheets:** the sheets the report uses, each linked.

## Structure

- **One card per recommendation**, in tier order (High, Medium, Low), then
  the Enablers group (telemetry, gating code, test-evaluation rules). Each
  card has:
  - a title that names the action, such as "Cut the hint price to 120";
  - a one-line lead with the goal or the problem in plain words;
  - 1–2 headline numbers with plain labels, such as "Level on day 7 vs
    today", never "D7 level, A vs Control";
  - 1–2 sentences of why, including its lever line (lever → metric);
  - 2–3 meta rows: Change (sheet / id / field, current → proposed),
    Workbook (a link to the sheet), Evidence (its kind and calibration
    status);
  - its own before-and-after chart;
  - a status chip.
- There are no separate Findings or Proposals lists: each change lives in
  its card. A problem with no fix yet is a card whose chip says what it's
  waiting for.
- If options are named A, B and so on, define them in the title or the
  lead of the card that uses them.
- Show only what can still be acted on. Remove resolved items, and claims
  that turned out not to be problems, instead of marking them "Resolved".
  The one exception is data requests: received ones stay, marked
  `received`, as the conventions require.
- Every card links to its evidence: an in-page chart, a JSON payload or a
  workbook sheet. The report ends with the list of workbook sheets it uses.
- Link between cards by anchor (`<a href="#rec-hint-price">`), never by
  number ("see card 3"), because numbers break when the list is re-ranked.

## Language

- **Charts first, very little text,** unless *config: Balance → Report
  style* says otherwise: one short lead sentence per section, and the
  numbers in charts or headline figures, not in paragraphs.
- Keep it short. Detail goes in the workbook's `Targets.notes`, not on the
  page. When a review adds findings, replace the old text; don't append to
  it.
- Name segments in plain words: light, mid and heavy players, not raw
  bucket ranges. Give the ranges once, in the Evidence section.
- A status chip says what happens next or what it blocks, such as "Ready
  to build", "Blocks option B", "Run A; B optional" or "Waiting on DR2".
  Never use a vague state like "Half passed".

## Claims

- **One cohort per sentence.** A caption's numbers come from the same
  cohort as the chart under it.
- **Check general claims against every segment** before writing them. A
  claim that holds for heavy players only says so.
- **Scope absence claims:** "none observed in the export", never "none
  exist".
- Competitor claims follow `benchmarks.md`.

## Charts

Inline SVG or the template's CSS bars, with no chart libraries.

- **Every mark can be identified without hovering.** No scatter or dot
  charts that need hover for names. For many categories, use horizontal
  bar rows with every label visible; when a row has two values, put two
  columns of bars side by side.
- **Per-day metrics by segment** default to grouped vertical bars, not
  lines.
- **Log scale** when values span more than two orders of magnitude.
- **Different units** go in headline numbers, never on a shared bar chart.
  Unrelated percentages go in tiles, not bars.
- **Changing chart types:** when the user asks for a review of the charts,
  propose the changes first, as a list or quick mock-ups, and apply them
  after approval.
- Use real units: levels, minutes, currency. Avoid indexes ("Today = 100")
  and compound ratios ("cash ÷ spend") unless they're the only fair
  comparison.
- Show the current value as a gray baseline bar next to each option.
- Drop the rows that don't change between options, and say so in the
  subtitle.
- The subtitle states the data source and the calibration status. It must
  not contradict the card it sits in.

## Consistency pass

Run it before writing the file, and again before every update:

- [ ] Every verdict word (Confirmed, Partly, Wrong) matches its card title
      and chart subtitle.
- [ ] Every evidence label matches the simulation's real state (calibrated
      or not, fitted parameters named).
- [ ] No chart mixes cohorts or windows (like-for-like checklist).
- [ ] Metric names match what the event counts: bought or owned, started or
      completed.
- [ ] A claim that holds on one platform or segment only says so and names
      the exception.
- [ ] Cards are in tier order, and every anchor link resolves.
- [ ] Every link and workbook link opens, and the page has no console
      errors.
- [ ] **Render check** at desktop width and at 360 px. Headless Chrome
      won't size a window below about 500 px, so check 360 px inside an
      iframe. Look for horizontal scroll, long labels overflowing, crowded
      ticks and colliding line-end labels.

## Fact-check

Before every write, after the consistency pass, have a reviewer that didn't
write the page recheck it: a subagent where the host has one, otherwise a
separate pass of your own against the source files. Give it the page and
the data files, not your conclusions. It:

- rechecks every number against the source files;
- checks that each sentence, caption and chart uses one cohort (the
  like-for-like checklist in `balance-checks.md`);
- challenges every causal claim and every absence claim;
- checks competitor claims against `benchmarks.md`.

Fix what it finds before writing. Most reviewer corrections come from
these rules.
