---
name: setup
description: 'Write or update a game repo''s .claude/gd-toolkit.md, the per-repo config that every gd command reads (doc paths, build and device commands, debug channel, remote config, checks, balance workbook). Use when the user runs /gd:setup, asks to set up the gd toolkit in a repo, or when another gd command finds the config missing.'
argument-hint: '[--refresh]'
---

# gd setup

`<skill-dir>` is the folder that holds this SKILL.md, and `<plugin-root>` is two folders above it. Replace them with real paths in commands. (In Claude Code they are `${CLAUDE_SKILL_DIR}` and `${CLAUDE_PLUGIN_ROOT}`.)

Output: `.claude/gd-toolkit.md` at the game repo root, filled in from what the
repo really contains. `--refresh` re-checks an existing file and updates it.

Read `<plugin-root>/shared/conventions.md` first.

## 1. Collect facts from the repo

Use the template `<skill-dir>/references/config-template.md`. Fill
each field from the repo, not from guesses:

- **Game:** the name from the app config or README. Genre and stack come
  from CLAUDE.md, README or package files. If the genre isn't written
  anywhere, infer it from the code: the core mechanic, the session shape and
  the monetization. The reference game is chosen in step 2; never ask for it.
- **Docs:** look for existing GDDs, plans and QA docs (for example
  `docs/plans/*gdd*.html`) and work out their naming patterns. The newest good
  example of each kind is its house reference.
- **Code map:** the screens and components dirs, the UI copy source, how
  remote-config keys are declared and parsed, ad calls, notification
  scheduling, the analytics doc, QA debug commands and the debug menu.
- **Checks:** typecheck, lint and test scripts in package.json or the build
  files, and any verification rules in CLAUDE.md or AGENTS.md (reviews,
  change gates).
- **Build and device:** the QA build, verify and install commands, a
  playable web build (a static web export, not a dev server), the device
  docs, the debug channel port and protocol, and known device quirks. Look for
  existing skills in `.claude/skills/` too, because they often hold exactly
  this, such as a QA or capture skill.
- **Balance:** any balance spreadsheets, simulations or economy tests.

## 2. Choose the reference game

If the repo already names a reference game in CLAUDE.md, a GDD or the
existing config, use that and stop here. Otherwise choose one yourself and
don't ask the user:

1. **Describe the game in one line:** the genre, the core mechanic (what the
   player does every few seconds), the meta (what brings them back over days),
   and the monetization (IAP, rewarded or interstitial ads, or hybrid).
2. **List 3–5 candidates:** live, high-ranking games that share that core
   mechanic and meta. Use WebSearch, if it's available, to check that they're
   still live and ranking now: top-grossing or top-downloaded in the category,
   on store charts or data.ai/Sensor Tower lists. Otherwise use what you know,
   and say so.
3. **Pick one** by how closely its **core loop** matches, then its **meta**,
   then its **monetization**, and only then its theme or art. A game in the same
   theme with a different loop is a poor reference.
4. **Write the line:** `Reference game: <Game> (AI-picked <YYYY-MM-DD>: <one-line
   match reason>; also considered <A>, <B>)`. Add `Reference game for <system>`
   lines when one game clearly fits a single system better, for example the
   meta or the economy.

In the report, say which game you picked and why, in one line, and that
replacing that line in the config overrides it.

## 3. Fill the remaining gaps

List the other fields you couldn't find. Ask about the ones that block the
command the user ran in one call to the question tool, following the asking rules
in the conventions. Leave the rest as `none`. Don't ask about fields that only
other commands need: those commands ask when they need them.

## 4. Write and report

Write `.claude/gd-toolkit.md`. With `--refresh`, keep the user's values unless
the repo plainly contradicts them; list every change you made. Never replace a
reference game the user wrote. You may re-pick one marked `AI-picked`, but
only if the genre or core loop has changed since it was chosen.

Report the path, the fields set to `none`, and anything that looked
inconsistent. Don't commit the file unless asked.
