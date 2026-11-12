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

## The screen is the reply

After every `ida turn`, paste its plain stdout into a `text` fence in the chat reply. Every time. Every host. Warp, Cursor, and Claude Code.

Tool output is not the screen. Warp collapses it ("19 output lines hidden · ctrl+o to expand") and the person only sees the last prompt. Color in that log is optional extra. It is never the only copy.

The fence is plain text, with no ANSI codes. Keep every spacer line. Keep the whole banner. Do not describe the banner. Do not shorten it. Do not restack the blocks.

The idk reveal is the case that fails if you skip this. The reply contains the block letters of the name, the two sentences, the three steps, and the prompt. A collapsed tool log does not.

Do not narrate a tool call, a path, or a command.

At the start of a sitting, read these once: `references/format.md`, `references/commands.md`, `references/loop.md`, `references/voice.md`, `library/exemplars.json`. Do not open the CSV, the examples, the evals, or every index file. Do not run `--help`. Do not run a command to discover flags. `references/commands.md` already lists them.

## One command

One shell command per user message. Never two. Never `--help`. Never `next` and then `show`.

The command is `ida turn`, plus at most one short choice:

```bash
ida turn
ida turn 3
ida turn idk
ida turn next
ida turn done
```

If `ida` is not on the path, use `python3 "$IDA/ida" turn` and the same choice. `$IDA` is the folder that contains this file. Do not call `scripts/ida.py`.

Stdout is the plain screen. Paste it. Stderr is one JSON line for you: the idea, the section, the options. Do not paste stderr. Do not quote it. Do not narrate the command.

Leave `IDA_COLOR` unset. Do not put a sentence, a scene, or an explanation on the command line. Write `/tmp/ida-screen.json` with the file tool, then `ida turn idk < /tmp/ida-screen.json`. No heredoc.

If the card rail contains `SCENE`, replace that word in the fence with the scene you write. That is not a second command.

## Choices

Use a native choice tool when the host has one. Claude Code: `AskUserQuestion`. Cursor: `cursor/ask_question` if that method is available, otherwise AskQuestion if it is in your tool list. Warp: `AskUserQuestion` when the host exposes it. Use the tool's own schema. Put the lane or the action in the label, and the percent or a one-line reason in the description.

Use it for the practice menu, the seven lanes, a multiple-choice card, and the actions after an answer (next, why, menu, retry). If there is no such tool, the `›` line is the choice.

## Session

1. `ida turn` shows the first profile question, or the menu. Paste stdout.
2. Each profile answer is `ida turn` with `{"answer":"..."}` in the JSON file. After the third, the same command shows the menu.
3. `ida turn 3` (or `daily`, `spot`, `surprise`) saves nothing and deals a card. Paste stdout. Fill `SCENE` in the fence.
4. Grade with `references/loop.md`. `ida turn idk`, `ida turn` with `"result":"strong"`, or `ida turn` with `"result":"partial"`, and the words in the JSON file. Paste the whole stdout. The idk reply includes the banner.
5. `ida turn next` deals another card. `ida turn done` is the summary. Paste that too.

## Privacy

Progress stays in `~/.ida/progress.json`. Do not upload it, commit it, or copy the file into the chat. Deleting that file starts over.
