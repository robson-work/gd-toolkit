# `--no-data` mode

For when there's no player data to use: a game that hasn't launched, a new
system with no history, or no access to analytics. It's on automatically
when *config: Live data* is `none`; say so in the report. Read this file
only in that mode. Each section replaces or extends one step of SKILL.md.

## Step 4a: no analytics requests

Never request analytics that don't exist. Use only data the team already
has from playtests or test builds, if the repo or the user has any, and
label it `Observed (playtest <date>, n=<players>)`, because a few testers
are not the market. Then go to 4b.

Playing the build yourself (step 4c) matters most in this mode: it's the
only way to check the values and the timing as the game really runs them.

## Step 4b: more benchmarks

Benchmarks are the main outside evidence, so research 4–6 games instead of
2–4. Also look for published numbers for the genre: retention by day,
session length, early-level funnels and soft-launch results.

## Step 5: targets

Our observed data doesn't exist, so targets come from the GD, the
reference game, the competitor range and the genre anchors. Every target's
`notes` says `no player data`, because no player has tested it.

## Step 7: honest simulation

Simulation carries more of the weight. There's nothing to calibrate
against, so every simulation stays `not calibrated`, and the sensitivity
check takes the calibration gate's place.

- Build the player models (the non-payer, the 10x failer, the hoarder and
  a typical player) from benchmark inputs: sessions per day, session
  length, attempts per level and ad opt-in. Name the source of each input.
- **Sensitivity check:** vary each assumed input across its benchmark
  range, and report which conclusions hold across the whole range and
  which flip. Propose only the changes that hold. List the ones that flip
  as "decide when data exists".
- Prefer values that are easy to change later, such as remote config, over
  values baked into the build.

## Step 9: a data plan in place of open data requests

- **Measure:** each target and the analytics event that measures it. Flag
  any event the game doesn't fire yet, because a target with no event
  can't be checked later.
- **First-data thresholds:** for each key metric, the value that means
  "keep", "tune" or "stop" once real data arrives, taken from the
  benchmarks.
- **Future prompts:** the copy-ready data prompts to run once there is
  data, each with `data-status="future"`. Their date ranges say "the first
  month of installs from the release or soft launch, read at D14 and D30",
  since the dates aren't known yet.

In chat, list the events still missing instead of the prompts, and end
with: "Once there's player data, run `/gd:balance <system>` without
`--no-data`, and the future prompts become data requests."

## When player data first exists

The first run without `--no-data`, or the first run after *config: Live
data* stops being `none`:

- turns the `future` prompts into open requests with real dates;
- compares the first numbers with the thresholds;
- replaces the `no player data` targets that our data now covers.
