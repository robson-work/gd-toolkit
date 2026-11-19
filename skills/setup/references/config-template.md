# gd-toolkit config — <Game name>

<!-- Read by every /gd command. Keep values short; one line each. Leave a
field as "none" when the game doesn't have it, rather than deleting it. -->

## Game
- Name: <Game name>
- Genre: <hypercasual | puzzle/casual | idle | ...>
- Reference game: <Game> (AI-picked YYYY-MM-DD: <why it matches>; also considered <A>, <B>)
<!-- Decision rule 1. /gd:setup picks it from the genre and core loop; replace
the line with your own choice to override (drop the "AI-picked" note). -->
- Reference game for <system>: <optional, when one game fits a system better>
- Platforms: <android, ios, web>
- Stack: <engine/framework, language>

## Docs
- Docs dir: docs/plans/
- Feature GDD path: docs/plans/{date}-{nnn}-feat-{slug}-gdd.html
- Implementation plan path: docs/plans/{date}-{nnn}-feat-{slug}-implementation-plan.md
- QA GDD path: docs/plans/{date}-{slug}-qa-gdd.html
- QA screenshots dir: docs/plans/assets/{slug}-qa/
- Feature GDD house reference: <path to a GDD whose look to copy, or none>
- QA GDD house reference: <path, or none>
- Embed images command: <repo command, or "bundled" to use the plugin script>
- Image check command: <repo command, or none>
<!-- {date} = YYYY-MM-DD of today, {nnn} = next free 3-digit number for that
date, {slug} = kebab-case feature name. -->

## Code map
- Screens and components: <dirs>
- UI copy source: <e.g. src/i18n/locales/en.json>
- Remote config: <provider; value format; how a key is declared; where defaults and parsers live>
- Remote config default: <e.g. features ship off>
- Ads: <API names for rewarded and interstitial calls; how placements are named>
- Notifications: <where they're scheduled; where their copy lives>
- Analytics: <events doc, e.g. src/analytics/README.md>
- QA debug commands: <docs and source dirs>
- Debug menu: <how to open it, e.g. Settings → version ×5 → Debug options>

## Checks
- Typecheck: <command, or none>
- Lint: <command, or none>
- Feature tests: <how a feature's tests are named and run>
- Verification rules: <repo rules to follow before calling work done, e.g. "CLAUDE.md reciprocal Codex review; AGENTS.md change gates">

## Build and device (QA captures)
- Capture platform: <android-adb | ios-device | web | none>
- Device rules docs: <docs to read before touching a device, or none>
- Build command: <the full standalone QA build command>
- Build verify command: <or none>
- Install command: <or none>
- adb path: <e.g. ~/Library/Android/sdk/platform-tools/adb>
- Debug channel: <port; how to list and invoke commands; or none>
- Needs approval: <debug commands that need the user's explicit OK, e.g. reset_app>
- Capture command: <e.g. adb shell screencap -p /sdcard/qa_shot.png && adb pull /sdcard/qa_shot.png <file>>
- Device quirks: <known traps, one line each>

## Art
- Image generation: not set
<!-- not set = ask on the first image | on | off (opted out YYYY-MM-DD). Set by /gd:asset. -->
- Image model: auto
<!-- auto = newest gpt-image ≥ 2, detail variant preferred; or pin an exact model id -->
- Art style: <one-line style description; paths to 2–4 reference assets>
- Assets dir: <where shipped images go, and the naming pattern>
- Art log: art/gen-log.jsonl

## Balance
- Workbook: balance/{game}-balance.xlsx
- Report: docs/balance/{system}-balance.html
- Simulations and tests: <commands that measure balance, or none>
- Live data: <analytics tool, and where its exports are or how to pull them (folder, BigQuery, bucket), or none (no player data yet: /gd:balance runs as --no-data)>
