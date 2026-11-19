# Balance workbook format

One `.xlsx` per game, at the config's **Balance → Workbook** path. Only the
script writes to it, through `run.sh` (see SKILL.md). People write to it in
Excel or Numbers.

## Sheets

| Sheet | Who edits | Contents |
|---|---|---|
| `README` | nobody | How to edit, and the color legend. |
| `Targets` | GD and AI | `id, metric, target, min, max, actual, source, status, notes`. Balance goals with tolerances. |
| `Benchmarks` | GD and AI | `id, game, system, metric, value, unit, context, source_url, accessed, confidence, notes`. Competitor and reference-game numbers. |
| *data sheets* | GD and AI | One per system, such as `Weapons`, `Enemies`, `Levels` or `Economy`. |
| `Changelog` | script only | `when, by, sheet, id, field, old, new, reason, status`. |
| `Sync` | script only | `sheet, id, field, code_ref, last_synced_value, synced_at`. |
| `_snapshot` | script only, hidden | The last state the AI saw, used to detect GD edits. |

## Data sheets

- Row 1 holds the headers. Column A is `id`: a stable, unique, lowercase
  key such as `sword_t1` or `level_012`. Never reuse or rename an id. Add a new
  row instead, and retire the old one with a `status` column.
- One row per thing (a weapon, enemy, level, reward or price) and one column
  per tunable value.
- **Inputs** are plain values in blue. **Derived metrics** are Excel formulas
  in black. The script colors cells by type when it writes them.
- When the AI writes a formula, it uses **placeholders, never column letters**:
  `{field}` for a cell in the same row and `{Sheet:id:field}` for any other
  cell. For example, `={damage}/{fire_rate_s}` becomes `=B3/C3`. The script
  resolves them and refuses unknown names. Formulas typed by the GD in Excel
  are kept exactly as written.
- Put derived metrics in the same row as the inputs, so that a GD who changes
  an input sees the effect at once in Excel.
- Formulas must refer only to cells in the same workbook, never to other files.
- Units go in the header: `cooldown_s`, `price_gems`, `reward_coins`,
  `hp`.
- Recommended columns where they apply: `tier`, `unlock_level`, `status`
  (`live`, `new` or `retired`) and `notes`.

### Example: `Weapons`

| id | tier | damage | fire_rate_s | cost_coins | dps | dps_per_1k_coins |
|---|---|---|---|---|---|---|
| pistol | 1 | 10 | 0.5 | 0 | `={damage}/{fire_rate_s}` | `=IF({cost_coins}=0,"",{dps}/{cost_coins}*1000)` |
| smg | 2 | 6 | 0.15 | 1200 | `={damage}/{fire_rate_s}` | `=IF({cost_coins}=0,"",{dps}/{cost_coins}*1000)` |

(The table shows the formulas as the AI sends them; the cells hold the
resolved `=C2/D2`-style references.)

### Example: `Targets`

| id | metric | target | min | max | actual | source | status |
|---|---|---|---|---|---|---|---|
| dps_curve | DPS growth per tier | 1.6 | 1.4 | 1.8 | 1.52 | Estimated (model) | ok |
| d1_hints_net | Hints earned − spent, D1 non-payer | 1 | 0 | 3 | −2 | Observed (devtodev 2026-11-10, 2026-11-01..07) | low |
| hint_price | Price of 1 hint, coins | 100 | 80 | 150 | 300 | Benchmark (3 games: A, B, C; 2026-11-18) | high |

`source` is always one of:
- `Observed (<tool> <pull date>, <date range>)`: taken from our live analytics.
- `Benchmark (<games>; <accessed date>)`: taken from the `Benchmarks` rows for
  those games. One game alone is written `Benchmark (reference: <game>; <date>)`.
- `Measured (<test or sim> <date>)`: produced by running a test or simulation.
  Add `, assumed inputs` if any of its inputs were not observed or benchmarked,
  `, fitted <parameter>` if one was fitted, and `, not calibrated` if the
  simulation hasn't passed the calibration gate in `balance-checks.md`.
  An agent playtest is `Measured (agent playtest <date>, build <version>, <device>)`.
- `Estimated (model)`: calculated in the workbook or by Python from its values.

### Example: `Benchmarks`

| id | game | system | metric | value | unit | context | source_url | accessed | confidence |
|---|---|---|---|---|---|---|---|---|---|
| gamea_hint_price | Game A | boosters | hint price | 90 | coins | from level 1 | https://… | 2026-11-18 | medium |
| gamea_coin_pack_s | Game A | iap | smallest coin pack | 1000 | coins per $0.99 | store, US | https://… | 2026-11-18 | high |

- One row per number per game. The id is `<game>_<metric>` in snake case.
- `confidence`: `high` for official patch notes, store listings or datamined
  config; `medium` for wikis and deconstructions; `low` for forums and videos.
- Normalize units before writing (per minute, per session, per day, USD tier)
  and note the conversion in `notes`.

## Sync `code_ref`

This is where the value lives in the game:

- `path/to/file.ts:SYMBOL.field`, such as `src/config/weapons.ts:WEAPONS.smg.damage`;
- `remote:<config_key>.<json.path>`, such as `remote:daily_quests_config.rewards.hint.weight`;
- `asset:path/to/data.json:$.json.path` for data files.

## What the script protects against

- **GD edits are never lost.** Every run starts with `diff`. Pending edits must
  be acknowledged with `ack` before any AI write, and once acknowledged they
  are GD-owned.
- **GD-owned cells are only overwritten with approval.** `apply` refuses them
  unless each change says `"approved": true`, which means the GD has said yes
  to that exact value in this session.
- **A workbook open in Excel is never written to.** Excel's lock file
  (`~$name.xlsx`) blocks every write.
- **Content the script can't keep is never destroyed.** Charts, images, pivot
  tables and macros block every write. They go in a separate workbook.
- **Every write is backed up.** A copy goes to `.history/` next to the
  workbook, and the last 30 are kept. Add `.history/` to `.gitignore`.
- **Formulas are recalculated on open.** The script can't compute formulas, so
  `dump` reports `formulas_stale: true` after a write. Compute any metric you
  need in Python from the input values, label it `Estimated (model)`, and
  don't trust a null cached value.
