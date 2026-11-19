---
name: gdd
description: 'Build a QA GDD for one feature: a single self-contained HTML page with a feature summary, copyable remote-config JSON, ad placements, notifications, QA debug commands and a captioned screenshot of every screen, captured on the device from a standalone build. Use when the user types "GDD <feature-name>", "/gd:gdd <feature-name>", "/gdd <feature-name>", or asks for a QA GDD, QA doc or screen walkthrough of a feature.'
argument-hint: <feature-name>
---

# QA GDD

`<skill-dir>` is the folder that holds this SKILL.md, and `<plugin-root>` is two folders above it. Replace them with real paths in commands. (In Claude Code they are `${CLAUDE_SKILL_DIR}` and `${CLAUDE_PLUGIN_ROOT}`.)

Input: a feature name, such as `split-testimony`, `daily challenge` or `cosmetics`.
Output: one HTML file at the config's **QA GDD path**, with every screenshot
embedded, so it opens on its own when shared.

Read `<plugin-root>/shared/conventions.md` and the repo config first.
Every path, command, port and doc named below as *config: X* comes from the
`.claude/gd-toolkit.md` field X.

The readers are QA testers. They need to know what the feature does, how to
switch it on, how to reach each state and what each screen should look like.
Use plain words and no implementation detail, apart from keys, ids and commands
QA has to type.

## Hard rules

These come from owner feedback on earlier GDDs. Check the page against them
before you report it.

1. **Way less text.** The page is mostly screenshots.
   - No paragraphs: every bullet, table cell and caption fits on one line.
   - "In short" has at most 4 bullets.
   - Captions are 2–4 words plus the screen name.
   - Say nothing twice, for example in a caption and in a table.
   - No explanations of how the code works, no history and no rationale.
2. **Every screen of the feature.** This includes every:
   - Home entry point;
   - screen, popup, sheet, notice and toast;
   - empty, locked, finished and closed state;
   - share sheet;
   - variant that a config switch produces, for example a sub-feature off;
   - Debug options section for the feature.

   Any screen missing from the grid goes under "Not captured" with a reason.
   A reason is acceptable only when no debug control could reach that screen.
3. **Real screenshots only.** Every image is a capture from the physical
   device running the real build.
   - Never use mockups, HTML or SVG renderings, composites, design art or
     edited screenshots.
   - If a state can't be reached, add a debug-only control so it can, then
     capture it.
   - If a capture needs a temporary code change, revert the change afterwards,
     and say in the report which shots used it.
4. **No emulator** unless the user asks for one.
5. **Crop personal data.** Crop contacts, account names and emails, and
   notifications from other apps, out of every shot, for example a share
   sheet's contact row. Delete the uncropped files.

**Look:** if *config: QA GDD house reference* is set, copy its CSS, layout,
Copy-button script and footer, and match its tone. Otherwise start from
`<skill-dir>/assets/qa-gdd-template.html`.

## 1. Find the feature in the code

Resolve the name to the feature's code. If it's ambiguous, ask which feature
is meant, giving the candidates you found. Then collect only facts that are in
the code:

- **Design doc:** the feature GDD (*config: Feature GDD path*) or plan, for the
  summary and intent. Link it in the footer.
- **Remote config** (*config: Remote config*):
  - the key, found the way the config says keys are declared;
  - the bundled default;
  - each field's meaning and allowed values, from its parser.
- **Ad placements** (*config: Ads*): rewarded and interstitial calls with their
  placement names, plus the config switch that gates each one.
- **Notifications** (*config: Notifications*): ids, when they fire, conditions,
  and the English title and body from *config: UI copy source*.
- **QA debug commands** (*config: QA debug commands*), plus the Debug options
  rows (*config: Debug menu*).
- **Analytics** (*config: Analytics*): list only the few main events QA would
  check.
- **Every screen and state:** walk the screen and component files (*config:
  Screens and components*). List each screen, popup, sheet, notice, toast and
  tab, each empty, error, locked, finished and closed state, the share sheet,
  the Home entry points, the feature's Debug options rows, and each variant a
  config switch produces (Hard rule 2). Cross-check this list against the
  feature GDD's `S1…Sn`. It's the shot list, and it must cover every screen.

## 2. Build the remote-config JSON

Write compact one-line JSON, exactly as it would be pasted into the
remote-config tool, in these blocks, each with a Copy button:

1. **Bundled default:** what the build does with no remote value.
2. **QA test payload:** the feature on, every sub-switch on, dates set so it's
   live today. Use today's date for any start field, and say so.
3. **Further payloads only when QA needs them:** for example ads off, a later
   phase, or a server switch on.

Under the blocks, add a table with the columns Field, Effect, Default and Ad
placement. Build each JSON with `JSON.stringify` on an object, or check it with
`node -e 'JSON.parse(...)'`, so it's always valid. Never invent a field the
parser doesn't read.

## 3. Capture every screen on the device

First read every doc in *config: Device rules docs*.

- **Build:** use *config: Build command*. It must be a standalone build with the
  code embedded, never a dev server, and with the debug surfaces armed. Check
  it with *config: Build verify command*, then install it with *config:
  Install command*. This is a QA-only build; say so in the report. Skip the
  build when the installed build already matches HEAD and no files have
  changed.
- **Device:** for `android-adb`, the first device in `adb devices`, using
  *config: adb path*. If no device is connected, ask the user to connect one
  and stop until they do.
- **Debug channel** (*config: Debug channel*): connect as the config says, list
  the commands, and use them to navigate and set state. Commands listed in
  *config: Needs approval* need the user's explicit OK.
- **Reaching states:** use the feature's QA debug commands and the Debug
  options to force the feature, move its phase and set progress. Don't play
  long stretches by hand. If a state can't be reached, add a debug-only command
  and Debug menu row rather than leaving it uncaptured. Put back every flag and
  phase you changed when you're done.
- **Capturing:** use *config: Capture command*, and respect *config: Device
  quirks*. Look at each shot, using a 450 px copy to save context, before
  keeping it. Wait for animations to settle, and retake any shot with a toast, a
  keyboard over the content, a loading spinner or the wrong state. A tap can
  miss after a notice disappears and the layout moves, so recheck the screen
  before the next tap.
- **Saving:** put the shots in *config: QA screenshots dir* as
  `NN-short-name.png`, in walkthrough order. Shrink each one to 450 px wide,
  for example with `sips --resampleWidth 450 <file>` on macOS.
- **States you can't reach:** for example server-only or real-time-only states.
  Leave them out of the grid and list them under "Not captured" with the
  reason.

## 4. Write the page

Write the file with these sections, in this order. Drop any section the
feature doesn't have.

1. **`h1` and subtitle:** `<Feature> — QA`, then version, device model and capture date.
2. **In short:** at most 4 one-line bullets saying what the player does and gets, in player terms.
3. **Remote config:** the key, the JSON blocks with Copy buttons, and the field table.
4. **How to test:** the Debug options rows QA taps that reach each state, as a table with the columns Goal and Command or steps. List the debug-channel command names on one line under the table.
5. **Ads:** placement, type, trigger and gating switch. Leave this out if it's already in the config table.
6. **Notifications:** id, when, only if, and the English title and body.
7. **Analytics:** event, when it fires, key parameters. Only the main ones.
8. **Screens:** a `.shots` grid of `<figure>` elements.
   - Each `img` points to the shot's path relative to the page.
   - Each caption is `<b>N · Screen name</b>` plus a few words on what to check.
   - Use `Nb` numbering for variants of the same screen.
9. **Not captured:** only if something is missing.
10. **Issues seen while capturing:** defects you noticed, each with the screen number. Report them to the user as well.
11. **Footer:** branch, a link to the feature GDD, and the analytics doc.

## 5. Embed and check

- Embed the images with *config: Embed images command*. If it's `bundled` or
  none, run
  `python3 "<skill-dir>/scripts/embed_images.py" <page.html>`
  (`--check` verifies that no external image is left). Also run *config: Image
  check command* if one is set.
- Validate every JSON block by parsing the `<pre>` contents.
- Check the page against the Hard rules: short text, every screen, real
  captures only.
- Open the file, or read it back, and check that every shot on the step 1 list
  is either in the grid or under "Not captured".
- Keep the PNGs in the screenshots dir as the source.

## 6. Report

Give the user:
- the file path;
- the number of screens captured, and anything not captured, with the reason;
- the test payload JSON inline.

Offer in one line to publish the page as a private Artifact for sharing. Do it
only if they say yes, because it contains internal config.

Don't commit unless asked. The repo's verification rules still apply to the
new doc; if a required reviewer is blocked, report it as blocked. If you
edited any code to reach a state, revert that edit.
