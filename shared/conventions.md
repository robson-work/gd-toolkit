# Shared conventions for every gd command

Every `gd` skill reads this file first. The skills run in Claude Code and in Codex.
`<plugin-root>` is the plugin's root folder (two folders above any skill's
SKILL.md), and `<skill-dir>` is the folder of the running skill. The game repo's own `CLAUDE.md` and
`AGENTS.md` always win over it: verification rules, commit rules, change
gates and limits on global tools apply exactly as the repo states them.

## 1. Repo config

Each game repo has a `.claude/gd-toolkit.md` file. It says where docs go, how
to build, how the debug channel works, where remote config lives and so on.

- Read it before doing anything else.
- If it's missing, follow `<plugin-root>/skills/setup/SKILL.md` to
  write it, then carry on with the command the user ran.
- If a field you need is empty or wrong, ask for it once, then write the answer
  into the config so nobody has to be asked again. The **Reference game** is the
  exception: if it's missing or not set, never ask. Choose one as step 2 of
  the setup skill describes, and write it into the config.
- Never hardcode one game's paths, commands or names in a doc or plan. Take
  them from the config.

## 2. Resolving a feature name

- Turn the name into a kebab-case slug: `Daily Quests` → `daily-quests`.
- Find its docs using the path patterns in the config: the feature GDD, the
  implementation plan and the QA GDD. Choose the highest revision if there are
  several, and say which one you used.
- Find its code by searching for the slug, the remote-config key and the names
  of its screens.
- If more than one feature matches, ask which one is meant and list the
  candidates you found. Never guess.

## 3. Asking the user

Use the host's structured question tool, called "the question tool" in these
skills: `AskUserQuestion` in Claude Code, or `request_user_input` in Codex
when it's available. If the host has none, ask in chat as a numbered list of
options and wait for the answer.

- Ask 1–4 questions per call, and group related ones.
- Give every question **at least 3 real alternatives**, each with a different
  mechanism and its trade-off. Never ask a yes/no question or offer one option
  to rubber-stamp.
- Put the recommended option first and add "(Recommended)" to its label.
- When the options look different from each other (layouts, curves, flows),
  add a `preview` so they can be compared side by side.
- Each question must make sense on its own. Say what you found that raised it.

## 4. Deciding without asking (auto mode)

When a command runs with `--auto`, or the user tells you to decide, settle
each open question with these rules, in this order, and record which one
settled it:

1. **The reference game.** Pick the option closest to the reference game named
   in the config. Use a `Reference game for <system>` line when one matches the
   question. If the reference is `AI-picked`, write `rule 1 (AI-picked
   reference)` so the owner can see what the decision rests on. If the
   reference game has no equivalent, say so and go to rule 2.
2. **Systems principles (Sellers, *Advanced Game Design*).** Name the loop it
   closes: core (seconds), progression (session) or meta (days). Every
   reinforcing loop needs a named brake and the day it engages. Every faucet
   needs a sink. The player must see the result of an action quickly enough
   to learn from it.
3. **High-ranking competitors.** Do the same as the top-grossing games in the
   genre, and say which ones you checked.

If the rules still leave a real fork that changes scope, cost or the economy,
ask anyway. Auto mode is for small questions, not for owner-level calls.

## 5. Facts and numbers

- Write absolute dates, such as `2026-11-17`, never "yesterday".
- Every number in a doc gets a source: the tool (devtodev, AppsFlyer,
  Firebase, the code or the balance workbook), the date it was pulled and the
  date range it covers. A guess is labelled as an estimate.
- Tell estimated results (from a model or calculation) apart from measured
  ones (from a test or simulation run) and observed ones (from live data).
- Only state facts that are in the code or the docs. Mark anything you assumed
  with `[ASSUMED]`.

## 5b. Requesting data

When a doc or report needs a number you don't have, don't stall and don't
guess silently.

- **Pull it yourself** when the config gives you access (an export folder,
  BigQuery, a bucket). Then no request is needed.
- **No player data** (a game before launch, a system with no history, or
  *config: Live data* is `none`): don't request analytics that don't exist.
  Use benchmarks and mark the number `no player data`. Write down what to
  measure once data exists, and the prompt to get it, marked
  `data-status="future"`.
- **Otherwise, request it in the doc.** Finish the doc with what you have,
  labelled Estimated or Benchmark, mark each gap `DATA NEEDED: DR1`, and add
  a **Data needed** section with one block per request, `DR1…DRn`.
- **Each request is a copy-ready prompt**, written so the user can paste it
  as-is into the analytics tool's AI assistant, a SQL or BigQuery assistant,
  or a message to an analyst. It says:
  - what it's for (the section or finding it settles);
  - the tool, picked from the source the repo trusts for that question;
  - the report or event, and the exact metric definition;
  - the filters: build or version, platform, country, payer segment;
  - the date range as absolute dates, and the granularity (per day, per level);
  - the minimum sample that makes it usable;
  - the output: CSV with named columns, aggregated, with no user ids or
    other personal data;
  - the file name to save it as, `YYYY-MM-DD_<title>_<scope>.csv`, in the
    data folder named in *config: Live data*.
- In HTML, each request is a `<div class="dr" data-dr="DR1"
  data-status="open">` with the prompt in a `<pre>` and a Copy button. In
  chat, each prompt is its own code block.

**When the data arrives** (pasted, given as a path, or found under the
expected file name at the start of a later run), update the same doc. Never
write a second one:

1. Check it before using it: the shape, the date range, nulls, the row
   count, and whether the events fire when you think they do.
2. Recompute everything that depended on it.
3. Replace the placeholders and estimates with the observed values and their
   source. Revise the findings, proposals and decisions that change. Don't
   append the new data as a note.
4. Set the request to `data-status="received"`, with the date, the file and
   the row count. Bump the revision and the Updated date.
5. Tell the user in a few lines what changed, and say plainly if a conclusion
   flipped. If the data contradicts the doc, say so; don't reconcile it
   silently.

Every command that updates a doc first looks for its open `data-dr` requests
and for files under their expected names.

## 5c. Remote-config JSON

Every remote-config JSON in a doc, a payload or the code holds only the
feature's own values: switches, amounts, timers, curves.

- **Never add A/B test fields**, such as `variant`, `group`, `arm`,
  `experiment`, `test_id`, `cohort`, a rollout percentage or audience
  targeting. Tests, groups, splits and audiences are set up in the tool
  named in *config: A/B testing*, such as devtodev, never in the JSON.
- **For a test,** give one complete, plain payload per group, each with
  its own Copy button. Name the group outside the JSON ("Control", "Group
  B: hint price 120"), and say to set up the test in that tool and paste
  each payload into its group.
- **The code reads plain values.** It never branches on a variant or group
  name sent in the config.

## 6. HTML pages

All the generated docs are single self-contained HTML files, which open
offline and can be shared on their own.

- Define the colors as `:root` tokens, with a
  `@media (prefers-color-scheme: dark)` variant.
- Use 16 px side gutters and allow no horizontal scroll at a phone width of
  360 px. Wide tables go in a `.table-scroll` wrapper.
- No external scripts, fonts or images. Images are embedded as data URIs.
- Copy buttons use the script from the templates, with its `execCommand`
  fallback for `file://` pages.

## 6b. Final image assets

Any command that needs a **final** image asset, meaning art that ships in the
game or the store, makes it by following
`<plugin-root>/skills/asset/SKILL.md`. It defaults to OpenAI's
newest GPT Image model, version 2 or later. The first time in a project, that
skill asks the user to set up an API key or opt the project out; respect
*config: Image generation* after that. GDD mockups are never generated images:
they stay HTML and CSS.

## 7. Git

Don't commit, push or open a PR unless the user asks, or the repo's rules say
to. If you change code only to reach a state temporarily, revert it.

## 8. The pipeline

`/gd:feature` writes the design → `/gd:make` builds it → `/gd:review` reviews
the code → `/gd:gdd` writes the QA page. `/gd:balance` runs at any time, and
before `/gd:make` when a feature adds tunable values. When
a command finishes, suggest the next one in one line.
