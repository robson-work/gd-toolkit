# Balance checks

Run every check that applies to the feature's systems. Each finding states
the value, the comparison it fails, and whether the evidence is estimated,
measured or observed.

## 1. Power and value curves (OP and UP)

- Compute a **value per cost** metric for each comparable group, such as DPS
  per coin, reward per minute or hints per ad. Flag any item more than about
  25% off the curve fitted to its peers in the same tier or unlock band. Look at
  it in context before calling it a problem.
- **Dominated options:** an item that is worse on every axis than another one
  available at the same point. Nobody will pick it, so it's dead content.
- **Must-picks:** an item that is better on every axis than its peers. The
  choice collapses to one option.
- **Tier steps:** the growth from one tier to the next should be steady,
  for example ×1.4–1.8 for idle games and gentler for puzzle games. A step much
  bigger than its neighbours makes the content before it pointless.

## 2. Scaling

- Check the growth type for each curve (cost, HP, reward, XP to level):
  linear, polynomial or exponential. Compare each **cost** curve with its
  **income** curve, because the gap between them is the time to the next upgrade.
- Project the time to the next upgrade, or to the next level, at sample
  points such as day 1, 3, 7, 14 and 30. If it grows faster than the target
  session cadence, it's a wall. If it shrinks to near zero, it's a runaway.
- **Reinforcing loops:** income that buys more income. Name the brake (a
  cost exponent above the income exponent, a soft cap or a prestige) and the
  day it takes effect. A loop with no brake is a finding.

## 3. Synergies and exploits

- **Multiplicative stacks:** list every multiplier that can apply at once and
  compute the worst-case product. Flag stacks that beat the next tier's base
  value.
- **Infinite or negative loops:** a buy-sell arbitrage, a reward greater than
  its cost on a repeatable action, a refund that's larger than the price, or
  ad rewards with no daily cap.
- **Edge values:** zero or negative costs, a cooldown of 0, division by zero
  in formulas, caps lower than a single grant, and levels whose requirement is
  lower than the previous one.

## 4. Economy flow

- Make a faucet and sink table for each currency: sources and sinks per day
  for the **non-payer**, the **10x failer** (the one stuck on a hard level) and
  the **hoarder** (the one who never spends), at day 1, 7 and 30.
- A balance that only grows means inflation, and the sink is missing or too
  weak. A balance stuck near zero for the non-payer means frustration, which
  shows up as churn. A hoarder's balance with no cap means future content will
  be trivialized.
- **Hint and booster rescue:** does the 10x failer earn enough help to get
  past the level, or does the free help remove the challenge for everyone
  else?
- **Headroom:** for each segment, at fixed times since install, divide the
  balance on hand by lifetime spend. Well above 1 means a cost increase
  smaller than that multiple won't bind for that segment.
- **Unused capacity:** the share of owned units (buildings, slots,
  vehicles) that are actually earning. A gap between bought and in use
  inflates any simulation that assumes all of them earn.

## 5. Difficulty (puzzle and level-based games)

- Compare the intended difficulty per level with observed attempts-to-win
  and churn-by-level (devtodev). A fat tail of attempts before a churn cliff is
  a spike.
- Check the rhythm: hard levels should be followed by relief levels, and there
  should be no two spikes in a row in the first 30 levels.
- First-session cost: the first win should come within the first minute.

## 6. Against benchmarks

- Place each key value in the competitor range from `Benchmarks`: below the
  minimum, inside it, or above the maximum. A value outside the range is a
  finding only if nothing in our design explains it, such as a faster core
  loop or a different session length. Write down the explanation when there
  is one.
- Compare rates, not raw numbers: reward per minute of play, price per hour
  of content, ad rewards per day. Raw amounts differ with each game's
  currency scale.
- Where we have observed data and the benchmark disagrees, trust our data
  for our players, and use the benchmark to decide which direction to test.

## 7. New content against existing content

When adding an item, enemy, level or reward:

1. Put it on the existing curve for its group, and derive its values from the
   curve, not from a guess.
2. Run checks 1–4 with the new row included.
3. Write it with `"status": "new"` until it's approved.

## 8. Lever → metric map

Before proposing a lever, write one line for it:
**lever → mechanism → metric it moves → why players can't route around it.**

- **Progress versus currency:** if progress comes from activity (actions,
  plays, deliveries) and currency can't buy progress, then prices, sinks
  and income multipliers change only the balance on hand, not the pace.
  Say so instead of proposing them as pace levers.
- **Substitution:** if a cheaper option is always available, raising the
  price of the top option doesn't constrain anyone. They buy the cheaper
  one.
- **Headroom:** a cost increase smaller than a segment's balance-to-spend
  ratio (check 4) won't bind for that segment.
- **Reach:** the share of each segment that reaches the content the lever
  changes within the test window. A lever on late content can't move light
  players, so name the segments it reaches.
- If the effect depends on a behaviour change the simulation holds fixed,
  give the two-bound result (SKILL.md step 7) and the live test that would
  settle it.

## Like-for-like checklist

Run it before any comparison between live data and a model, or between two
cohorts. Most "anomalies" come from mismatched definitions.

- **Same population:** never compare players still active on day N
  (survivors) with a simulation of every player. Either simulate survivors
  or measure everyone.
- **Hold play time constant:** the main calibration target is progress at
  fixed times since install (hours for idle games, days for level-based
  games), grouped by minutes played in that window: light, mid and heavy
  players.
- **One chart, one definition:** every number in a chart uses the same
  cohort, window and exclusions. If that's impossible, footnote the mix.
- **Windows:** check the day boundaries, the timezone and whether day 0
  counts. An off-by-one window creates false anomalies.
- **Event meaning:** check what the counter actually counts (bought or
  owned, started or completed, one route stop or the whole route) in the
  code before naming the metric.

## Calibration gate

A simulation counts as **Measured** only after it reproduces live
**progress** and **income** at fixed times since install, for every
play-time segment, within a stated tolerance (±25% by default).

- Until it passes, show results only relative to the current values, and
  label them `not calibrated` in the evidence kind and the chart subtitle.
  Never rank levers on an uncalibrated simulation's absolute numbers.
- Allow at most one fitted parameter per segment, such as the share of
  owned units in use. Label it `FITTED`, say what it was fitted to, and
  request the data that would measure it.
- Check the fit against a second target it wasn't fitted to, for example
  fit to level and then check income.
- Without player data (`--no-data`) there is nothing to calibrate against,
  so every simulation stays `not calibrated` and relies on the sensitivity
  check instead.

## Validation ladder

Prefer the strongest evidence available, and always label which one you used:

1. **Observed:** our live analytics for the current values (only for content
   that's already live).
2. **Benchmark:** competitor and reference-game numbers from `Benchmarks`,
   from at least two games for a range.
3. **Measured:** the repo's simulations or tests (*config: Simulations and
   tests*), or a Python simulation saved next to the workbook. It counts as
   Measured only after passing the calibration gate; before that, its
   results are relative only and labelled `not calibrated`. Report its seed
   and number of runs. Its inputs come from observed data or benchmarks;
   any assumed input is labelled, and the result is then low confidence.
4. **Estimated:** closed-form maths from the workbook values.

A simulation tells you what a value will do, not what it should be. Don't
set a target from a simulation alone.

Without player data there's no Observed evidence, except playtest data,
which comes from a few testers and not the market. Benchmarks become the main
evidence, and simulations need a sensitivity check across the benchmark range
(see SKILL.md, `--no-data`).

If two levels disagree, say so and say which one you trust and why.
