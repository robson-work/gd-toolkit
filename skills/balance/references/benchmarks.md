# Competitor research (Benchmark)

Research automatically on every run. Don't ask first.

- **Which games:** the reference game from the config, plus 2–4 games that
  rank high in the same genre now, starting with the "also considered" list
  from the config's reference-game line. Use WebSearch where it's available.
  With `--no-data`, see `no-data.md`.
- **What to find:** the same values this system tunes. For example: prices
  and pack sizes, reward amounts and cadence, timers and caps, cost and
  income curves, energy or lives, ad reward caps, and difficulty pacing.
- **Where to look, from most to least reliable:** official patch notes and
  store listings (IAP prices), datamined or public config, wikis, and
  deconstructions such as Deconstructor of Fun, GameRefinery, Naavik or
  mobilegamer.biz. Use forum and video sources only when nothing else
  exists, and mark them low confidence.
- **Privacy:** a search names the competitor games and the genre. It never
  names this repo's game, its unreleased features or its internal numbers.
- **Normalize the units** before comparing: per minute of play, per
  session, per day, or a USD price tier. Note the context of each number,
  such as the level, the day or the tier.
- Write each number into the `Benchmarks` sheet with `apply` (reason:
  `research`), with its game, source URL, the date you accessed it and a
  confidence level (high, medium or low).
- One game is a reference, not a benchmark. A benchmark range needs at
  least two games.
- If WebSearch isn't available, say so, ask the user for competitor numbers
  they have, and fall back on the genre anchors in the repo's CLAUDE.md.
