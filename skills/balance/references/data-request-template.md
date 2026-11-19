# Data request template

One self-contained prompt per tool or analyst, covering everything the
analysis and a calibrated simulation need, so the data arrives in one
round. The user pastes it as-is into the analytics tool's AI assistant, a
SQL or BigQuery assistant, or a message to an analyst or a data agent.

Before writing it:

- Check in the code that every event it asks for is actually sent:
  analytics allowlists, sampling and tier filters. Leave an event the
  client doesn't send out of the open request. Fix the code, and put it
  in a `data-status="future"` request for after the release.
- Take the trusted source for each question from the repo's own rules
  (its CLAUDE.md or AGENTS.md), such as the progression tool for level
  funnels and the MMP for attribution.

## Template

Replace every `<…>`. Drop the blocks the system doesn't need.

```text
Read only. Change nothing: no dashboards, no saved queries, no settings.

Purpose: calibrate the <system> balance model for <game build or version>.
It settles <the report sections or DR ids this answers>.

Source: <tool, and the report, table or export to use>.

Cohort: players who installed from <YYYY-MM-DD> to <YYYY-MM-DD>, on build
<x> or later, <platforms>, <countries or all>.
Exclude: testers and internal devices <how to spot them>, cheaters <rule>,
incentivised or offerwall installs <rule>, <any other segment>.
Segments: by minutes played in each window: light <0–N>, mid <N–M>,
heavy <M+>. Also split by <platform | payer | A/B arm> where it differs.

Metrics, per segment, at <1h, 4h, 24h, 72h, 7d> since install:
1. Play time (minutes) and sessions: median, p25, p75.
2. Ad use: rewarded views per player, interstitials per player.
3. Purchases: share of payers, spend per player, items or packs bought.
4. Balance on hand of <currency>: median, p25, p75.
5. Progress: <level | stage | chapter>: median, p25, p75.
6. Behaviour: <what players build or choose>; units owned versus units in
   use; how many share <the shared resource>.
7. Live config: the values of <remote-config keys> each segment received.

Quality checks, reported with the data:
- row count and players per segment and window;
- nulls per column;
- whether <event> fires once per <action>, or also on <retry | resume>;
- any window with under <200> players, kept but flagged.

Output: CSV, one file per numbered metric block, with columns
<segment, window, metric, p25, p50, p75, players>. Aggregated numbers only,
with no user ids or other personal data. Use JSON only when a block is
nested, and give its schema.
Save as <YYYY-MM-DD>_<title>_<scope>.csv in <data folder from config: Live data>.
```

## When one tool can't answer it all

Split it by tool, one prompt each, as `DR1`, `DR2` and so on. Within one
tool, keep it to one prompt. Several small prompts to the same tool mean
several rounds of rework.
