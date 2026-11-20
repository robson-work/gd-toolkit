---
name: feature
description: 'Write a concise high-level feature GDD as one self-contained HTML page with phone mockups of every screen: player problem, rules, loop, economy, remote config, success metric, risks and open questions. By default asks the user the open questions; --list-questions only lists them in the doc. Use when the user runs /gd:feature or /feature, or asks for a GDD, design doc or high-level design of a new feature.'
argument-hint: '<feature description> [--list-questions]'
---

# Feature GDD

`<skill-dir>` is the folder that holds this SKILL.md, and `<plugin-root>` is two folders above it. Replace them with real paths in commands. (In Claude Code they are `${CLAUDE_SKILL_DIR}` and `${CLAUDE_PLUGIN_ROOT}`.)

Input: a feature description, from one line to a pasted brief. It may name an
existing GDD to revise.
Output: one HTML file at the config's **Feature GDD path**.

Read `<plugin-root>/shared/conventions.md` and the repo config first.

The readers are the owner, designers, developers and the `/gd:make` command.
The doc says **what** the feature is and **why**. It doesn't say how the code
works.

## Modes

- **Default:** ask the user every open question (step 3), write the answers
  into Decisions, and keep only the questions they skip as open.
- **`--list-questions`:** don't ask. Write every open question into the doc,
  each with its options and the recommended one first. `/gd:make` asks them
  later.

## Hard rules: concise

1. **One line per element.** Every bullet, table cell and spec line fits on one
   line. There are no paragraphs, except the pitch, which is at most 2 sentences.
2. **Say everything once.** Nothing appears twice, for example in a
   mockup and in its spec, or in a rule and in a table. Link with `§N` or a
   screen id `S3` instead of repeating.
3. **Mockups carry no redundant text.**
   - A mockup holds only the copy the player would really see, in the game's
     language and tone.
   - It has no annotations, arrows with labels or "this button does X"
     inside the phone.
   - The spec beside it lists only what the picture can't show: where each tap
     goes, states, timing and conditions. It never repeats visible copy.
   - The `aria-label` is the screen name only.
4. **No implementation detail.** Leave out files, classes and architecture.
   Config keys, event names and ids are allowed.
5. **No history or rationale essays.** A decision gets one line, and its reason
   goes in a short clause if it's needed.
6. **Target length:** under 250 lines of visible text, excluding the mockups.
   If it's longer, cut it.

## 1. Understand the feature and the game

- Read the repo config, CLAUDE.md and the GDDs for features this one touches,
  using the config's docs dir.
- Read enough code to know the current screens, economy (currencies, sources,
  sinks), remote-config patterns, ads and notifications that the feature has to
  fit with.
- If the feature already has a GDD, revise it: bump the revision in the
  header and move settled questions into Decisions. Don't create a second file.
  If it has open data requests, look for their files and use what has arrived
  (conventions §5b).
- Use the reference game (config) as the first anchor for the design.

## 2. Design it

Work out each of these before writing:

- **Player problem:** what the player lacks today, in one line.
- **Loop:** core, progression or meta. Say whether it's reinforcing (name the
  brake and when it engages) or balancing.
- **Economy:** every faucet with its sink, or a statement that inflation is
  intended. Run the three edge cases through it: the player who never pays,
  the player who fails 10 times on one level, and the hoarder.
- **First-session cost:** does it add tutorial load or delay the first win?
- **Screens:** every entry point, screen, popup, sheet, toast, and empty,
  locked, finished and closed state.
- **Remote config:** the key and its fields. The feature ships in the state the
  config's **Remote config default** says, usually off.
- **Proof:** the metric that would move, its baseline with source, the target,
  and the kill criterion. If no metric would move, say the feature can't be
  tested and price it as content. If the baseline or any number the design
  rests on isn't available, write a data request for it (conventions §5b)
  instead of guessing.
- **Open questions:** each with 3 or more real options and a recommendation.

## 3. Ask (default mode only)

Ask the open questions with the question tool, following the asking rules in the
conventions. That's at most 4 questions per call, so batch them if there are
more. Then:

- Write each answer into **Decisions** as `Settled` with today's date.
- Leave questions the user skips or answers with "later" under **Open
  questions**.
- If an answer changes the design, update the affected sections. Don't append
  it as a note.

## 4. Write the page

Start from the template `<skill-dir>/assets/feature-gdd-template.html`.
If the config names a **Feature GDD house reference**, take its colors and its
mockup style for the game's look, but keep the template's sections and the
concise rules.

These are the sections, in order. Drop any the feature doesn't have.

1. **Header:** a label, the `h1` name, the pitch, and a meta row with Status,
   Revision, Updated, Config and Target.
2. **In short:** at most 4 bullets, in player terms.
3. **Decisions:** `Settled` items, each with its date.
4. **Goal and proof:** the player problem, the loop line, and a table with the
   columns Metric, Baseline (source), Target and Kill if.
5. **Rules:** the numbered rules of the feature, one line each.
6. **Screens:** a `.screens` grid. Each `.screen` has a `.phone` mockup and a
   `.spec` with an id `S1…Sn`.
7. **Economy:** a table with the columns Item, Faucet or sink, Amount and Cap,
   plus the edge-case lines for the non-payer, the 10x failer and the hoarder.
8. **Remote config:** the key, a one-line JSON default with a Copy button, and
   a table with the columns Field, Effect and Default. No A/B test fields
   (conventions §5c).
9. **Ads, notifications, analytics:** a short table each, and only the main
   events.
10. **Risks:** churn, first-session cost and the non-payer, one line each,
    plus anything specific to this feature.
11. **Data needed:** one copy-ready prompt per request (conventions §5b).
    Keep the `id="data-needed"`, `data-dr` and `data-status` attributes.
12. **Open questions:** each as `Q1 …` with its options, the recommended one
    marked. Keep the `id="open-questions"` and `data-q` attributes, because
    `/gd:make` reads them.
13. **Later:** what's out of scope, one line each.
14. **Footer:** the related docs.

Mockups use the template's phone kit (`.phone`, `.ps`, `.pstatus`, `.pbody`,
`.btn`, `.card`, `.veil`, `.popup`, `.bar`). Draw icons as inline SVG
symbols. Use no images unless the user supplies art. Never generate images
for mockups: final art is made later, by `/gd:make` through `/gd:asset`.

## 5. Check

- Validate every JSON block with `node -e 'JSON.parse(...)'` or Python.
- Check the hard rules: one line per element, nothing said twice, no text in a
  mockup the player wouldn't see, and the length target.
- Check that every screen in Rules and Economy has a mockup, and that every
  mockup is referenced.
- Check the page at 360 px wide: no horizontal scroll.

## 6. Report

Give the file path, the decisions made in this run, the questions still open,
every open data prompt as its own code block, and the next step:
`/gd:make <feature>`. When the user sends the data, update the GDD as
conventions §5b describes. If the feature adds tunable values,
such as prices, rewards, timers or curves, suggest `/gd:balance <feature>`
first, to put them in the balance workbook and check them against
competitors.
