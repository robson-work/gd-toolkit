# Balance report rules

The defaults for the report page. They exist because each one was asked
for, one turn at a time, in real reviews.

## Sections

The template's sections, in order. Delete the ones that are empty.

- **In short:** at most 4 bullets.
- **Live baseline** (SKILL.md step 1), with its unconfirmed values marked.
- **Evidence:** the data exports (source, range, rows), the games
  researched, the simulations (seed, runs, calibration status, which inputs
  are assumed or fitted), and the segment definitions.
- **Recommendations:** the cards (below), in tier order.
- **Enablers:** telemetry, gating code, test-evaluation rules.
- **Sync:** what was synced to code, and the remote-config payload the user
  has to push, with a Copy button.
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

- Keep it short. Detail goes in the workbook's `Targets.notes`, not on the
  page. When a review adds findings, replace the old text; don't append to
  it.
- Name segments in plain words: light, mid and heavy players, not raw
  bucket ranges. Give the ranges once, in the Evidence section.
- A status chip says what happens next or what it blocks, such as "Ready
  to build", "Blocks option B", "Run A; B optional" or "Waiting on DR2".
  Never use a vague state like "Half passed".

## Charts

Inline SVG or the template's CSS bars, with no chart libraries.

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
- [ ] Every link and workbook link opens, the page has no console errors,
      and it has no horizontal scroll at 360 px.
