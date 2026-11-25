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
- Ask only tools the team has (*config: Balance → Data tools*).
- **Window:** at least one month of installs, read at D14 and D30. Never
  two weeks.
- **Fixed cohorts for day-N curves:** every day on a curve comes from the
  same installs, the ones old enough for the last day shown. Otherwise the
  curve rises and falls because later days come from other players. Say
  so in the prompt.
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

Request <DR1> v<1>, <YYYY-MM-DD>.

Cohort: players who installed from <YYYY-MM-DD> to <YYYY-MM-DD> (one month
or more), on build <x> or later, <platforms>, <countries or all>.
Exclude: testers and internal devices <how to spot them>, cheaters <rule>,
incentivised or offerwall installs <rule>, <any other segment>.
Segments: by minutes played in each window: light <0–N>, mid <N–M>,
heavy <M+>. Also split by <platform | payer | A/B arm> where it differs.

Day-N curves use a fixed cohort: only installs old enough for the last day
shown, so every day comes from the same players.

Metrics, per segment, at <1h, 4h, 24h, 72h, 7d, 14d, 30d> since install:
1. Play time (minutes) and sessions: median, p25, p75.
2. Ads: ads seen per player per day and over the lifetime, by type and by
   placement; offers shown against ads watched, per placement.
3. Purchases: share of payers, spend per player, items or packs bought.
4. Balance on hand of <currency>: median, p25, p75.
5. Progress: <level | stage | chapter>: median, p25, p75.
6. Behaviour: <what players build or choose>; units owned versus units in
   use; how many share <the shared resource>.
7. Live config: the values of <remote-config keys> each segment received.
8. LTV by day since install (D1–D30), cumulative, split by source: IAP,
   rewarded, interstitial.
9. IAP timing: the day and session of the first purchase, and the
   player's state then (<level, balance, last action>).
10. Churn: the last action before a player's last session.
11. Sources and sinks of <currency> over the player's life, by source.

Quality checks, reported with the data:
- row count and players per segment and window;
- nulls per column;
- whether <event> fires once per <action>, or also on <retry | resume>;
- any window with under <200> players, kept but flagged.

Output: CSV, one file per numbered metric block, with columns
<segment, window, metric, p25, p50, p75, players>. Aggregated numbers only,
with no user ids or other personal data. Use JSON only when a block is
nested, and give its schema.
Save as <YYYY-MM-DD>_<title>_<scope>_<DR1>v<1>.csv in <data folder from config: Live data>.
```

Blocks 2–4 and 8–11 are the standard economy list: keep them in every first
request for an economy, with every block split by segment and platform.
Drop only the ones the system doesn't have.

## Never edit a sent request

Once the user has the prompt, it's frozen. A change gets a new id (`DR5` →
`DR5b`) and a new version in the prompt and the file name, and the old
block is marked replaced. Otherwise an export made from the old prompt
gets read as if it answered the new one.

## When one tool can't answer it all

Split it by tool, one prompt each, as `DR1`, `DR2` and so on. Within one
tool, keep it to one prompt. Several small prompts to the same tool mean
several rounds of rework.
