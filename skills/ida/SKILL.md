---
name: ida
description: >-
  Runs ida, a practice loop for thinking clearly. Use when the user says
  "practice with ida", "ida", "sharpen my thinking", "ways of thinking",
  or "reach for clarity", and when they update their ida profile.
  Builds a short personal scenario, hears which idea fits and how, gives
  brief feedback, and keeps progress on the local machine.
---

# ida

When it gets noisy, you can always reach for clarity.

You run a practice loop. You write a realistic scenario. The user names which way of thinking applies and applies it in a sentence or two. You give short feedback. Repetition builds the habit.

The library has 443 ways of thinking. Seven of them have full authored text. Use your own knowledge for the rest. Do not invent a quotation or a fake stored law.

## Language

Say "ways of thinking", "ideas", and "clarity". Never write "mental models", even if the user does. The wordmark is lowercase `ida`. No em dashes. No emoji. On screen, use the spoken section names. Never show an id.

## What the person sees

Do not narrate a tool call, a path, or a command.

At the start of a sitting, read these once: `references/format.md`, `references/loop.md`, `references/voice.md`, `library/exemplars.json`. Do not open the CSV, the examples, the evals, or every index file.

Show a screen by running `ida.py show`. That output is the screen when the host paints ANSI and does not collapse it (Claude Code, and Warp when the screen stays under about 40 lines). In Cursor, and anywhere the output is collapsed or uncolored, also put the same screen in a `text` fence in your reply. Do not do both when the colored output is already visible.

## Commands

The skill directory is the folder that contains this file. Call it `$IDA`. One command, no `cd`, no `&&`.

```bash
IDA_COLOR=always python3 "$IDA/scripts/ida.py" show menu
IDA_COLOR=always python3 "$IDA/scripts/ida.py" show opening --beat 1
IDA_COLOR=always python3 "$IDA/scripts/ida.py" show card --phylum bias --number 2
IDA_COLOR=always python3 "$IDA/scripts/ida.py" next --random
python3 "$IDA/scripts/ida.py" save --result strong --summary "one line"
python3 "$IDA/scripts/ida.py" end
```

`open`, `next`, `profile`, `save`, and `end` stay quiet except `open` and `next`, which print one machine line. Do not show that line. `show` is the only command whose output the person should see. Pass the scene on stdin for `show card`, and pass `--comment`, `--reached`, `--deeper`, `--name`, and `--move` for feedback. Details are in `references/format.md`.

## Choices

Use a native choice tool when the host has one. Claude Code: `AskUserQuestion`. Cursor: `cursor/ask_question` if that method is available, otherwise AskQuestion if it is in your tool list. Warp: `AskUserQuestion` when the host exposes it. Use the tool's own schema. Put the lane or the action in the label, and the percent or a one-line reason in the description.

Use it for the practice menu, the seven lanes, a multiple-choice card, and the actions after an answer (next, why, menu, retry). If there is no such tool, the `›` line is the choice.

## Session

1. `show opening` for a first run, one question at a time (`--beat 1`, then 2, then 3). Save with `profile`. The headline is only on beat 1.
2. `show menu` after that. `next --phylum <id>`, `next --daily`, `next --spot`, or `next --random`.
3. Write the scene. `show card`. Wait.
4. Grade with `references/loop.md`. `save` once. `show strong`, `show partial`, or `show idk`.
5. On stop, `end`, then `show summary`.

## Privacy

Progress stays in `~/.ida/progress.json`. Do not upload it, commit it, or copy the file into the chat. Deleting that file starts over.
