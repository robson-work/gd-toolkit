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

## Validation ladder

Prefer the strongest evidence available, and always label which one you used:

1. **Observed:** our live analytics for the current values (only for content
   that's already live).
2. **Benchmark:** competitor and reference-game numbers from `Benchmarks`,
   from at least two games for a range.
3. **Measured:** the repo's simulations or tests (*config: Simulations and
   tests*), or a Python simulation you write in the scratchpad. Report its
   seed and number of runs. Its inputs come from observed data or benchmarks;
   any assumed input is labelled, and the result is then low confidence.
4. **Estimated:** closed-form maths from the workbook values.

A simulation tells you what a value will do, not what it should be. Don't
set a target from a simulation alone.

If two levels disagree, say so and say which one you trust and why.
