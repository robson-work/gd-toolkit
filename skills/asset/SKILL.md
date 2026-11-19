---
name: asset
description: 'Generate final in-game image assets (icons, items, backgrounds, characters, store art) with OpenAI''s newest GPT Image model, version 2 or later, matched to the game''s existing art. On first use in a project it explains how to set up an OpenAI API key, and lets the user opt the project out. Use when the user runs /gd:asset, asks for final art, icons or sprites, or when another gd command needs a final image asset. Not for GDD mockups, which stay HTML and CSS.'
argument-hint: '<asset description or list> [--fast]'
---

# Final image assets

`<skill-dir>` is the folder that holds this SKILL.md, and `<plugin-root>` is two folders above it. Replace them with real paths in commands. (In Claude Code they are `${CLAUDE_SKILL_DIR}` and `${CLAUDE_PLUGIN_ROOT}`.)

Input: one asset or a list, such as "streak freeze icon" or "the 6 reward
icons in the daily-quests GDD". Output: PNGs at the game's assets path, each
logged with its prompt and model.

Read `<plugin-root>/shared/conventions.md` and the repo config
(**Art** section) first.

```sh
GI="<skill-dir>/scripts/gen_image.py"   # Python 3 only; never prints the key
python3 "$GI" check                              # key + model that would be used, no cost (run from the game repo)
python3 "$GI" generate --prompt "…" --out <file.png> [--size WxH] [--background transparent] [--ref <art.png> …] [--log <log.jsonl>]
```

## 0. Is image generation on for this project?

Read *config: Image generation*:

- **`on`**: go to step 1.
- **`off`**: don't generate. Use existing art or the repo's placeholder
  pattern, and list the assets still needed (name, size, use) in the report.
  Don't ask again.
- **`not set` or missing**: this is the first image for this project. Run
  `check`, then ask with the question tool:
  - If **no key was found**, the question says that final assets default to
    OpenAI's GPT Image (the newest version, 2 or later) and that an API key is
    needed. The options are:
    1. **Set up a key now (Recommended):** show the setup steps below and wait
       until the user says it's done. Then run `check` again. When it's ready,
       write `on`.
    2. **Not for this project:** write `off (opted out <YYYY-MM-DD>)` and
       continue without generated art.
    3. **Not now:** skip images this time, leave the field `not set`, and
       ask again next time.
  - If **a key was found** (in the repo's `.env`, the environment, or set up
    for another project), the question names where it was found and the model
    `check` picked. If `check` says the `.env` file is tracked by git, warn
    that the key is committed and should be rotated, and recommend moving it
    out of git. The options are: use it for this project
    (Recommended, then write `on`), not for this project (`off`), and not now.

### API key setup (show this to the user)

1. Go to **platform.openai.com → API keys → Create new secret key**. A
   project-scoped key is best.
2. Make sure **Billing** has credit. GPT Image models may also ask you to
   **verify your organization** (Settings → Organization → General). Access can
   take a few minutes to turn on after verification.
3. Save the key on this machine. **Never paste it into the chat.**
   - **macOS (recommended):** run this in Terminal. It asks for the key without
     showing it, and stores it in the Keychain:
     `security add-generic-password -U -a "$USER" -s gd-toolkit-openai -w`
   - **This project only:** add `OPENAI_API_KEY=…` to the repo's `.env` or
     `.env.local`. Check that the file is in `.gitignore` first.
   - **Anywhere:** add `export OPENAI_API_KEY=…` to your shell profile, such as
     `~/.zshrc`, then open a new terminal.
   - **Or** use a file readable only by you: `~/.config/gd-toolkit/openai_api_key`
     (`chmod 600`).
4. Tell me when it's done, and I'll check it. That check costs nothing.

A key in the Keychain, the shell or the config file works for every project;
a `.env` key works for its repo and wins over the Keychain. The on/off choice
is made per project.

## 1. Plan the assets

- **Style:** read *config: Art style* and look at the reference art it lists.
  Pass 1–4 of the closest existing assets as `--ref`, so new art matches the
  game. Describe the style in every prompt in the same words: palette, line
  weight, shading, camera angle and material.
- **Specs:** for each asset, its final size, its format, whether it needs
  transparency, its file name and its path (*config: Assets dir*, plus the
  repo's naming pattern).
- Show the list, with its total count and model, and generate once the user
  OKs it. One confirmation covers the batch.

## 2. Generate

- **Model:** `--model auto` (the default) uses the newest gpt-image model,
  version 2 or later, that the key can use, preferring the detailed variant
  for final art. `--fast` (passed as `--prefer fast`) is for drafts only. If
  *config: Image model* names a model, pass it with `--model`.
- **Size:** generate at the model's largest square or nearest aspect, then
  scale down to the final sizes (`sips -Z <px>` on macOS). Never scale up.
- **Transparency:** icons, items and sprites need `--background transparent`.
  If the output notes that the model rejected it, the image was made opaque:
  regenerate with a flat, plain background color named in the prompt, remove
  that color, and say so in the report.
- **Prompt:** describe the subject, then the style block, then the
  composition (centered, padding, no text unless asked). Ask for no words,
  logos or watermarks unless the asset needs text.
- Log every generation to *config: Art log* (`--log`). Never put metadata files
  next to the shipped assets.

## 3. Check each image

Look at every image before keeping it, using a small copy to save context.
Regenerate it, at most 3 times, if it doesn't match the style references, has
stray text or artifacts, is cropped wrongly, or is unreadable at its smallest
in-game size. If it still fails, keep the best one and flag it.

## 4. Report

List each asset with its path, sizes, model and any flags. Also give the
assets still needed (if generation is `off` or skipped), and the log path.
Say that the images are AI-generated, so the owner can decide where that
needs disclosing, such as on store listings.
