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

Say "ways of thinking", "ideas", and "clarity". Never write "mental models", even if the user does. The wordmark is lowercase `ida`. No em dashes in anything the user reads.

## Files

The skill directory is the folder that contains this file. Call it `$IDA`. In Claude Code that path is `${CLAUDE_SKILL_DIR}`. Anywhere else, use the directory of the `SKILL.md` you just read. Do not pass an unexpanded variable to a command.

Read a file only when a step tells you to. Do not open `library/ida-library.csv`, `examples/`, or `evals/` during practice. Do not open every index file. Do not paste `~/.ida/progress.json` into the chat.

| When | Read or run |
| --- | --- |
| Every session start | `python3 $IDA/scripts/progress.py load` |
| First scenario of the sitting | `references/voice.md`, then `library/exemplars.json` |
| Picking the next idea | `python3 $IDA/scripts/pick.py` |
| Showing a block | `python3 $IDA/scripts/render.py` |
| The loop is unclear | `references/loop.md` |
| You cannot run Python | `references/format.md` and `references/progress.md` |
| They ask what a section contains | `library/phyla.json` or `references/library.md` |

## Commands

```bash
python3 $IDA/scripts/progress.py load
python3 $IDA/scripts/progress.py save-profile --role "..." --interests "..." --decisions "..."
python3 $IDA/scripts/progress.py start --selection section --phylum strategy --mode free
python3 $IDA/scripts/progress.py save
python3 $IDA/scripts/pick.py --random
python3 $IDA/scripts/render.py opening --kind returning --line "Last time: strategy, scenario 3."
python3 $IDA/scripts/render.py card --number 1 --phylum strategy --practice decide --mode free
python3 $IDA/scripts/progress.py record
python3 $IDA/scripts/progress.py end
```

`save` and `record` read a JSON object from stdin. The shapes are in `references/progress.md`. `card` reads the scene from stdin when `--body` is omitted.

Print renderer output as-is. In a terminal, print it raw. In a chat with a proportional font, wrap that block in a `text` fence so the padding holds. Do not reflow a card after rendering.

## Session

1. Load progress. The load command creates `~/.ida/progress.json` if it is missing.
2. Render the opening from `welcome.kind` and `welcome.line`. Kind `new` means there is no profile: show the intro and wait. Do not start a scenario yet.
3. On the first answers, save the profile. A sentence each is enough. If they skip a question, store an empty string and go on. Then show the practice menu (`opening --kind ready`).
4. If `welcome.kind` is `resume`, show the stored scenario again and wait. Do not write a new one unless they want to start fresh (`start --fresh`, and if the payload includes `ended`, render that summary first).
5. Practice is `[1]` a section (a phylum, plus a category if they name one), `[2]` ideas they name, or `[3]` random. All sections are open. There is no unlocking.
6. Pick with `pick.py`. Write the scene for those ids only, in this person's life. Save `in_progress` before you show the card. `next_number` is the card number.
7. Wait. `idk` is always allowed. Grade the reasoning, render feedback, `record`, render `section_bars`, then one line: `Another, or stop.`
8. On stop, run `end` and render the summary and the full bars.

Grading, personalization, modes, and what to write are in `references/loop.md`. Follow them.

## Privacy

Progress stays in `~/.ida/progress.json` on this machine. Do not upload it, commit it, or copy the file into the chat. Deleting that file starts over. The operations above are the memory API. If a memory service is ever wired in place of the file, call the same operations. Do not invent a network call in this version.
