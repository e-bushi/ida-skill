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

Tool output is not the screen. Warp collapses it ("output lines hidden") and the person only sees a dim last line. That last line is a spacer, so the preview is empty. Color in that log is optional extra. It is never the only copy.

The fence is plain text, with no ANSI codes. Keep every spacer line, including the last one. Keep the whole banner. Do not describe the banner. Do not shorten it. Do not restack the blocks.

Do not narrate a tool call, a path, or a command.

At the start of a sitting, read these once: `references/format.md`, `references/commands.md`, `references/loop.md`, `references/voice.md`, `library/exemplars.json`. Do not open the CSV, the examples, the evals, or every index file. Do not run `--help`. Do not run a command to discover flags. `references/commands.md` already lists them.

## One command

One shell command per user message. Never two. Never a fallback chain. Never `--help`. Never a second command to redraw the card.

Do not write a temp file. Do not use a file-edit tool. Do not use a heredoc. Do not pipe stdin. Do not chain commands. If the command needs words from you, they are quoted arguments on that one command.

The folder that contains this file is the skill directory. Write it with `~` when it sits under your home directory. For the usual install:

```bash
sh ~/.agents/skills/ida/ida turn
sh ~/.agents/skills/ida/ida turn "their answer"
sh ~/.agents/skills/ida/ida turn 1 "inversion" "the scene" "one-line summary" "short explanation. How to apply it here."
sh ~/.agents/skills/ida/ida turn idk
sh ~/.agents/skills/ida/ida turn done
```

If this file was loaded from another directory, use that directory in the same shape, still with `sh` and still one command. Do not search for a binary. Do not run this file with `python3`.

Stdout is the plain screen. Paste it. Leave `IDA_COLOR` unset. Stderr is empty, except the one reminder after `idk`. Do not paste stderr.

## idk

**When they type idk, run `sh ~/.agents/skills/ida/ida turn idk`. The reply MUST paste the full reveal screen verbatim in a `text` fence before anything else, and only then call the choice tool.**

That screen is the whole reveal: the idea name, the 3-row banner, the short explanation, and how to apply it. It was saved in `~/.ida` when you dealt the card. Do not write it again. Do not skip the banner. Do not put the reveal inside the choice tool. The choice tool, after the fence, may offer got it, another like this, and menu.

## Choices

Use a native choice tool when the host has one. Claude Code: `AskUserQuestion`. Cursor: `cursor/ask_question` when that method is available, otherwise AskQuestion if it is in your tool list. Warp: `AskUserQuestion` when the host exposes it. Use the tool's own schema.

Single select only. Do not turn a menu into checkboxes. One question, and do not write "Question 1 of 1" yourself. Put a short label in the header or title field when the tool has one (lane, card, next).

Labels are the spoken names in lowercase: thinking clearly, knowing what's true, blind spots, reading people, playing to win, seeing ripple effects, deciding and acting. Put the percent, or a one-line reason, in the description.

Use the tool for the seven lanes (plus daily, spot, and surprise me), for the short labels of a multiple-choice card, and for the actions after an answer (next, why, menu, retry, again, done). After idk, the options are got it, another like this, and menu. After a re-explain, the options are got it, another angle, next, and menu. Do not use it for a free-text card. The tool's question is a short label such as "lane" or "next", never the card's question and never "Clearer now?". On a multiple-choice card the tool's options are the short names only. The fence already showed the question and the full options.

The choice tool is not for a free-text answer. A free-text card, and a profile question, end the reply. The person types. Do not call the tool at all on that card. If they type idk, hint, or skip, treat that as the reply. Do not print a line listing those words.

If the host has no choice tool, the first command of the sitting is `sh ~/.agents/skills/ida/ida turn --typed`. ida remembers it. The screen then ends with a `›` line, and that line is the choice. Do not pass `--typed` when the tool exists.

## Session

1. `sh ~/.agents/skills/ida/ida turn` shows the first profile question, or the menu. Paste stdout. Each profile answer is `sh ~/.agents/skills/ida/ida turn "their answer"`. After the third, the menu shows.
2. Pick an idea you can teach in the lane they chose. Deal it in that same command. The quotes are the idea name, the scene, a one-line summary, and a short explanation that says how to apply it:

```bash
sh ~/.agents/skills/ida/ida turn 1 "inversion" "the scene" "one-line summary" "short explanation. How to apply it here."
```

Paste stdout, including the scene and `■ T H E   Q U E S T I O N`. The scene is already in the screen. Do not swap in a placeholder. If the card is free text, stop. If it lists options, the choice tool may follow, with the short labels only.

3. Grade with `references/loop.md`. A strong answer is `sh ~/.agents/skills/ida/ida turn "their answer"`. A thin one is `sh ~/.agents/skills/ida/ida turn partial "their answer"`. A wrong one is `sh ~/.agents/skills/ida/ida turn miss "their answer"`. For idk, the bold rule above. Paste the whole stdout.
4. `sh ~/.agents/skills/ida/ida turn next "idea" "the scene" "one-line summary" "short explanation. How to apply it here."` deals another card. `sh ~/.agents/skills/ida/ida turn done` is the summary. Paste that too.

`daily`, `spot`, and `surprise` take the same quotes when you know the idea. With no quotes, ida picks and saves a short explanation from the library. `hint` reuses the saved explanation. `retry` reuses the saved scene.

## Privacy

Progress stays in `~/.ida/progress.json`. Do not upload it, commit it, or copy the file into the chat. Deleting that file starts over.
