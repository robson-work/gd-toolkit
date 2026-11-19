# gd-toolkit

Plugin for Claude Code and Codex with game design commands for mobile games. It takes a
feature from design to code to QA, and keeps its balance in an Excel workbook
that the designer and the AI edit together.

## Install

```text
/plugin marketplace add robson-work/gd-toolkit
/plugin install gd@gd-toolkit
```

Then run `/gd:setup` once in each game repo.

### Codex

```sh
codex plugin marketplace add robson-work/gd-toolkit
codex plugin add gd@gd-toolkit
```

Restart Codex. The skills show up as `gd:feature`, `gd:make` and so on: pick
one from `/skills`, mention it with `$`, or just ask, for example "write a
feature GDD for …". The skills, the repo config and the workbook are the same
in both hosts.

Codex's sandbox blocks the network and writes outside the workspace by
default, so approve the request when:
- `/gd:asset` calls the OpenAI API, or reads the key from the Keychain (or use
  `$OPENAI_API_KEY` instead);
- `/gd:balance` creates its venv under `~/.cache/gd-toolkit/`, which happens
  once.

## Commands

| Command | Does | AI model |
|---|---|---|
| `/gd:feature <description>` | Writes a concise HTML feature GDD with a phone mockup of every screen, and asks the open questions. | Opus 5.5 |
| `/gd:make <feature>` | Implements the feature from its GDD: settles the open questions, plans, builds in checked steps and updates the GDD. | Opus 5.5 |
| `/gd:review <feature>` | Reviews the feature's code against its GDD and fixes the critical and major issues. | GPT-6.1 Sol |
| `/gd:gdd <feature>` | Writes the QA GDD: config payloads, debug steps and real device captures of every screen. | Opus 5.5 |
| `/gd:balance <system>` | Creates or extends the balance sheets, pulls your live data and competitor benchmarks, and rebalances values with the Excel workbook as the source of truth. | Opus 5.5 |
| `/gd:asset <description>` | Generates final in-game art with OpenAI's newest GPT Image model (2.0 or later), matched to the game's existing art. | Opus 5.5 |
| `/gd:setup` | Writes the repo config. Other commands run it when the config is missing. | Opus 5.5 |

The usual order is `feature` → `make` → `review` → `gdd`. `balance` runs at
any time and doesn't need a GDD; run it before `make` when a feature adds
prices, rewards, timers or curves.

### Flags

| Flag | Effect |
|---|---|
| `/gd:feature --list-questions` | Writes the open questions into the doc instead of asking them. |
| `/gd:make --auto` | Settles open questions with the decision rules: reference game → systems principles → top competitors. |
| `/gd:review --no-fix` | Reports findings only. |
| `/gd:balance --report-only` | Proposes changes without applying them. |
| `/gd:setup --refresh` | Re-checks an existing config against the repo. |

## Per-repo config

Each game repo has `.claude/gd-toolkit.md`. It holds the doc paths, build and
device commands, debug channel, remote-config conventions, checks and the
balance workbook path, so the commands never hardcode one game. The repo's own
`CLAUDE.md` and `AGENTS.md` always win. The template is
[`skills/setup/references/config-template.md`](skills/setup/references/config-template.md).

## Data requests

When a report or GDD needs data the agent can't pull itself, it doesn't stop
or guess. It finishes with what it has, marks each gap `DATA NEEDED: DR1`, and
adds a **Data needed** section with one copy-ready prompt per request (the
tool, metric, filters, dates, CSV columns and the file name to save it as).
Paste the prompt into your analytics tool's assistant or send it to an
analyst. When you send the data back, or save it under that file name, the
next run checks it and updates the same doc, saying what changed.

## Balance workbook

- **Sheets are proposed for you.** If a system has no sheet, or there's no
  workbook yet, `/gd:balance` shows the sheet plan and creates it from the
  values in the code.
- **Evidence first, simulation second.** Each run requests the exports it needs
  from your analytics (devtodev, Firebase…) and researches the reference game
  and 2–4 top genre competitors. Their numbers go in the **Benchmarks** sheet
  with source links. Simulations project a change; they never set a target
  alone. Every result is labelled Observed, Benchmark, Measured or Estimated.
- **Edit freely in Excel.** Blue cells are inputs and black cells are formulas.
  Every sheet has an `id` column.
- **Your edits are respected.** Each run detects them, logs them as `by=GD`, and
  never overwrites them without your approval.
- **Changelog** records every change: who made it, why, and the old and new
  values.
- **Sync** maps each value to its place in the code and tracks what's been synced.
- **Report page:** each run writes or updates an HTML report at the config's
  `Report` path, with findings, proposals, the remote-config payload and the
  data prompts.
- **Close the file before running** `/gd:balance`. Keep charts and images in a
  separate workbook, because the script refuses to write a file that has them.

The format is in
[`skills/balance/references/workbook-format.md`](skills/balance/references/workbook-format.md).
The helper script runs in a private venv under `~/.cache/gd-toolkit/`, which
is created on first use.

## Image generation

Final art uses OpenAI's newest GPT Image model, version 2.0 or later, which
the script detects at run time. GDD mockups are never generated images.

- **First image in a project:** `/gd:asset` explains how to set up an OpenAI
  API key, or lets you turn image generation off for that project. The choice is
  saved as `Image generation:` in the repo config.
- **Key lookup, in order:** `$OPENAI_API_KEY`; `OPENAI_API_KEY` in the game
  repo's `.env.local` or `.env`; the macOS Keychain
  (`security add-generic-password -U -a "$USER" -s gd-toolkit-openai -w`);
  `~/.config/gd-toolkit/openai_api_key`. Never paste the key into the chat.
- **Pin a model:** set `Image model:` in the config. `auto` picks the newest one.

## Layout

```
.claude-plugin/   Claude Code plugin.json, marketplace.json
.codex-plugin/    Codex plugin.json
.agents/plugins/  Codex marketplace.json
shared/           rules every command follows
skills/<name>/    SKILL.md + assets/, references/, scripts/
```

## Updating

Edit, bump `version` in both `.claude-plugin/plugin.json` and
`.codex-plugin/plugin.json`, run `claude plugin validate .`, then push. Users
update with `/plugin update gd@gd-toolkit` in Claude Code, or with
`codex plugin marketplace upgrade` and then `codex plugin add gd@gd-toolkit`
in Codex.
