---
name: review
description: 'Code review of one game feature: correctness, conformance to its GDD, remote-config safety, economy and ad gating, analytics, copy and debug leaks. Fixes critical and major issues automatically, re-runs the checks, and reports the minor ones. Use when the user runs /gd:review or /review with a feature name, or asks to review a feature''s code.'
argument-hint: '<feature name> [--no-fix]'
---

# Review a feature

`<skill-dir>` is the folder that holds this SKILL.md, and `<plugin-root>` is two folders above it. Replace them with real paths in commands. (In Claude Code they are `${CLAUDE_SKILL_DIR}` and `${CLAUDE_PLUGIN_ROOT}`.)

Input: a feature name. Output: a findings report, with critical and major
findings already fixed and verified. `--no-fix` only reports.

Read `<plugin-root>/shared/conventions.md` and the repo config first.
The repo's own review rules (CLAUDE.md, AGENTS.md, change gates) still apply
after this review. This one doesn't replace them.

## 1. Scope the feature's code

- Resolve the feature and load its GDD and implementation plan if they exist.
  A feature without a GDD can still be reviewed; skip the conformance checks
  and say so.
- Collect the files: those in the implementation plan, commits that mention
  the slug or config key (`git log --all --oneline -i --grep <slug>`), and a
  search for the config key, screen names and event names. Include the
  callers at each place the feature plugs into the existing game.
- If the work isn't merged, compare the branch against its base and review
  that diff, plus the surrounding code.

## 2. Review

Read the code. For every finding you need a concrete path to the failure:
the inputs or state that lead to the wrong output or a crash. Without one, it
isn't a finding.

Check these areas:

1. **Correctness:** logic errors, state that breaks across app restarts,
   resume from background, reinstall or cloud restore, races, timezone and
   day boundaries, and off-by-one errors in counts and rewards.
2. **GDD conformance:** every rule, screen and state, the config fields and
   their defaults, and the copy. A screen in the GDD that has no code is a
   finding, and so is a behavior in the code the GDD doesn't mention.
3. **Remote config:** a missing or malformed value falls back to the
   bundled default. The feature ships as the config's default says. A switch
   turned off mid-session is safe. No A/B test fields in the config or the
   parser, and no branching on a variant name (conventions §5c).
4. **Economy:** no grant that can repeat (double claims, claims on retry,
   rewards granted before the ad has finished), no faucet without its sink, and
   caps enforced. Run the non-payer, the 10x failer and the hoarder through the
   code paths.
5. **Ads:** every placement is gated by its switch, the reward is granted only
   on the completed callback, and interstitials respect the cooldowns.
6. **Analytics:** each event fires exactly once per real occurrence, never on
   retries, re-renders or resume, and with the parameters the docs list.
   Progression start and finish events come in pairs.
7. **Copy and localization:** no hardcoded player-facing strings, and every
   key exists in the copy source.
8. **Debug leaks:** debug commands, menus and test payloads don't reach
   release builds.
9. **Tests:** the riskiest logic is covered by tests. A missing test is minor,
   unless the logic moves currency.

## 3. Rate

- **Critical:** crashes, data or progress loss, economy exploits, real money
  or ads granted wrongly, or a release that exposes debug tools.
- **Major:** player-visible wrong behavior, a GDD rule broken, an event
  missing or double-firing, or a config fallback that's unsafe.
- **Minor:** edge-case polish, missing tests for non-currency logic, or
  cleanup.

## 4. Fix (unless `--no-fix`)

- Fix every critical and major finding with the smallest change that does it.
  Add a test where the repo has a pattern for one.
- When the GDD itself is wrong, or a fix needs a design call, such as
  changing a rule or the economy, don't fix it. Ask with the question tool,
  giving 3 or more options.
- Re-run the config's typecheck, lint and feature tests after fixing, and then
  any verification the repo requires for code changes.
- Leave minor findings unfixed, and list them.

## 5. Report

Use the ReportFindings tool if it's available, otherwise a short table with
the columns Severity, File:line, Problem, Path to failure and Status (Fixed
or Open). After it, add:

- the check results after the fixes;
- GDD differences, and whether the code or the doc was changed;
- the questions that need the owner;
- the next step: `/gd:gdd <feature>` for the QA page.

Don't commit unless the user asks or the repo's rules require it.
