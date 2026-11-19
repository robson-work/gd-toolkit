# Playtest the build

Play the game yourself, on an attached phone or a web build, to check the
system as it really runs. A playtest shows things the code and the data
don't: the values the build actually uses, the real time between rewards,
and exploits that only appear in play.

## When

Do it on every run where a playable build exists (*config: Build command*
or *config: Web build* isn't `none`) and the system can be reached in play.
Otherwise, say in the report why there was no playtest.

## 1. Ask first

Building and installing replaces the app on the phone, and its local
progress may be lost, so never start without asking. First check what's
available: `adb devices` (*config: adb path*), an iOS device if *config:
Capture platform* is `ios-device`, and *config: Web build*. Then ask with
the question tool, recommending the option that's ready now:

- **Attached phone** (name the model found): build, install and play it.
- **Web build:** serve it and play it in the host's browser tool.
- **Use the installed build as it is:** play without rebuilding, which
  works when it already matches HEAD.
- **Skip the playtest this run:** the checks it would cover are marked
  `not played`.

In the question, say what you'll do: the build, the install, about how
many minutes you'll play, and which debug controls you'll use.

## 2. Set up

Read every doc in *config: Device rules docs*. For the build, the install,
the device and the debug channel, follow `<plugin-root>/skills/gdd/SKILL.md`
§3:

- a standalone build with the debug surfaces armed, never a dev server;
- skip the build when the installed one already matches HEAD;
- commands under *config: Needs approval* need the user's explicit OK.

**Web:** run *config: Web build* and open its URL with the browser tool
the host has. Read the game's state through the debug channel or the page
console, not only from the pixels.

## 3. Write a test plan before playing

Pick each measurement from the checks this run needs, and list them:

| Check | What to do in the build | Debug control needed |
|---|---|---|

Typical measurements:

- **Live values:** read the costs, rewards, timers, caps and clock speed the
  build actually uses, and compare them with the live baseline. Where the
  build differs from the code or the workbook, that's a finding.
- **Real time:** the seconds to the first win, the first reward and the
  first upgrade; then, at sample points such as day 1, 3 and 7 or level 10,
  30 and 60, the time to the next upgrade or level. Use debug controls to
  jump to each point instead of playing to it.
- **Edge cases:** the non-payer path, the 10x failer (fail one level on
  purpose), the hoarder (grant currency and check the caps), and the
  exploits from check 3 (stacked multipliers, repeatable rewards, ad caps).
- **Feedback:** whether the player can see what an action earned quickly
  enough to learn from it. One line per screen where they can't.
- **After a sync** (step 8): replay the changed values to confirm the
  build uses them.

## 4. Debug controls

Check *config: QA debug commands* and *config: Debug menu* against the
"Debug control needed" column. The controls balance usually needs are:

- read the economy state as JSON: currencies, level, owned items, timers;
- set a currency, or grant an item;
- set the level or the day, or skip ahead in time, or set the time scale;
- win or fail the current level;
- reset progress (it usually needs approval).

If any are missing, ask with the question tool:

- **I add them** (Recommended): debug-only, behind the build's debug flag,
  with a row in the Debug menu, following the repo's change gates. They
  stay in the code for the next run, and the report lists them.
- **You add them:** I write their spec, and carry on with what I can test
  now.
- **Play without them:** I play by hand as far as one session allows, and
  mark the rest `not played`.

## 5. Record

- Write each measurement into `Targets.actual` through `apply`, with the
  source `Measured (agent playtest <date>, build <version>, <device>)`.
- **What a playtest can and can't show:** it is one tester who knows the
  system, not a player. Use it for mechanics, live values, timing and
  exploits. Never use it for player behaviour, such as retention, choices,
  spend or difficulty felt: those come from data or benchmarks.
- A difference between the build and the simulation is a model bug until
  shown otherwise: fix the simulation (core principle), then re-run.
- In the report's Evidence section, add a Measured row with the build, the
  device, the minutes played and what was covered. A card may embed one or
  two small screenshots as data URIs when they show the problem.

## 6. Clean up

Put back every flag, phase and debug value you changed. Revert any
temporary code change. Leave the build installed, and say so.
