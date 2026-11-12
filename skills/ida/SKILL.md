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

Every turn that needs a command: run that one command, then write the screen in the reply. A card is always that reply. Paste the scenario and `■ T H E   Q U E S T I O N` and the question text in a `text` fence. For a multiple-choice card, the numbered options are in that fence too. Do not leave the question only in a tool.

The choice tool is not for a free-text answer. A free-text card, and a profile question, end the reply. The person types. Do not call the tool at all on that card. If they type idk, hint, or skip, treat that as the reply. Do not print a line listing those words.

Call the choice tool only for a menu, a multiple-choice answer, or the next step after feedback or a re-explain. It comes after the fence, never before, and never twice with nothing written between the calls. Its labels are short. The question text and the scenario stay in the fence. A re-explanation is a `text` fence headed `■ A N O T H E R   A N G L E`, not a sentence inside the tool. If a host shows text poorly after a tool call, the text still goes before the call.

Do not narrate a tool call, a path, or a command.

At the start of a sitting, read these once: `references/format.md`, `references/commands.md`, `references/loop.md`, `references/voice.md`, `library/exemplars.json`. Do not open the CSV, the examples, the evals, or every index file. Do not run `--help`. Do not run a command to discover flags. `references/commands.md` already lists them.

## One command

One shell command per user message. Never two. Never a fallback chain. Never `--help`. Never `next` and then `show`.

The folder that contains this file is the skill directory. Write it with `~` when it sits under your home directory. For the usual install the only command is:

```bash
sh ~/.agents/skills/ida/ida turn
sh ~/.agents/skills/ida/ida turn 3
sh ~/.agents/skills/ida/ida turn idk
sh ~/.agents/skills/ida/ida turn next
sh ~/.agents/skills/ida/ida turn done
```

If this file was loaded from another directory, use that directory in the same shape, still with `sh` and still one command. Do not search for a binary. Do not chain a second command. Do not run this file with `python3`.

Stdout is the plain screen. Paste it. Stderr is one JSON line for you: the idea, the section, the options. Do not paste stderr. Do not quote it. Do not narrate the command.

Leave `IDA_COLOR` unset. Do not put a sentence, a scene, or an explanation on the command line. Write `/tmp/ida-screen.json` with the file tool, then `sh ~/.agents/skills/ida/ida turn idk < /tmp/ida-screen.json`. No heredoc.

If the card rail contains `SCENE`, replace that word in the fence with the scene you write. That is not a second command.

## Choices

Use a native choice tool when the host has one. Claude Code: `AskUserQuestion`. Cursor: `cursor/ask_question` when that method is available, otherwise AskQuestion if it is in your tool list. Warp: `AskUserQuestion` when the host exposes it. Use the tool's own schema.

Single select only. Do not turn a menu into checkboxes. One question, and do not write "Question 1 of 1" yourself. Put a short label in the header or title field when the tool has one (lane, card, next).

Labels are the spoken names in lowercase: thinking clearly, knowing what's true, blind spots, reading people, playing to win, seeing ripple effects, deciding and acting. Put the percent, or a one-line reason, in the description.

Use the tool for the seven lanes (plus daily, spot, and surprise me), for the short labels of a multiple-choice card, and for the actions after an answer (next, why, menu, retry, again, done). After a re-explain, the options are got it, another angle, next, and menu. Do not use it for a free-text card. The tool's question is a short label such as "lane" or "next", never the card's question and never "Clearer now?". On a multiple-choice card the tool's options are the short names only. The fence already showed the question and the full options.

If the host has no choice tool, the first command of the sitting is `sh ~/.agents/skills/ida/ida turn --typed`. ida remembers it. The screen then ends with a `›` line, and that line is the choice. Do not pass `--typed` when the tool exists.

## Session

1. `sh ~/.agents/skills/ida/ida turn` shows the first profile question, or the menu. Paste stdout.
2. Each profile answer is that same command with `{"answer":"..."}` in the JSON file. After the third, the menu shows.
3. `sh ~/.agents/skills/ida/ida turn 3` (or `daily`, `spot`, `surprise`) saves nothing and deals a card. Paste stdout, including `■ T H E   Q U E S T I O N`. Fill `SCENE` in the fence. If the card is free text, stop. If it lists options, the choice tool may follow, with the short labels only.
4. Grade with `references/loop.md`. `sh ~/.agents/skills/ida/ida turn idk`, or the same command with `"result":"strong"` or `"result":"partial"` in the JSON file. Paste the whole stdout. The idk reply includes the banner.
5. `sh ~/.agents/skills/ida/ida turn next` deals another card. `sh ~/.agents/skills/ida/ida turn done` is the summary. Paste that too.

## Privacy

Progress stays in `~/.ida/progress.json`. Do not upload it, commit it, or copy the file into the chat. Deleting that file starts over.
