# Commands

Read this instead of `--help`. `--help` is refused on purpose. One shell command per user message, and that command is `ida turn`.

The shim is `ida` next to this skill. From a sitting, the visible line is:

```bash
ida turn
ida turn 3
ida turn idk
ida turn next
ida turn done
```

If `ida` is not on the path, the same command is `python3 "$IDA/ida" turn`. Do not call `scripts/ida.py` directly. Do not pass `--help`. Do not explore flags.

Stdout is the plain screen. Paste it into a `text` fence. Stderr is one JSON line for you. Never paste stderr. Never quote it. Never narrate the command.

A long answer, a scene, or an idk reveal does not go on the command line. Write `/tmp/ida-screen.json` with the file tool, then:

```bash
ida turn idk < /tmp/ida-screen.json
```

That is still one command. No heredoc.

## ida turn

| Argument | Meaning |
| --- | --- |
| (none) | First run: the next profile question. Otherwise the menu, or the open card again. |
| `1` to `7` | A lane, when the menu is waiting. 1 thinking clearly, 2 knowing what's true, 3 blind spots, 4 reading people, 5 playing to win, 6 seeing ripple effects, 7 deciding and acting. |
| a spoken lane name | Same as the number. |
| `daily` | One card chosen for today. |
| `spot` | A quick multiple-choice card. |
| `surprise` | A random card. |
| `next` | The next card after feedback. |
| `retry` | The same idea again. |
| `why` | The last feedback, one level down. |
| `menu` | The seven lanes. |
| `done` | End the sitting and show the summary. |
| `--typed` | No choice tool on this host. Remember it for the sitting. Screens then end with a `›` line. Pass it once, on the first turn. |
| `idk` | Save idk and show the banner. The JSON carries `explain`, `moves`, and `closing`. |
| `skip` | Save a miss and return to the menu. |
| a number during a choice card | That option. A correct option is strong. |

Stdin JSON keys, all optional: `answer`, `choice`, `result` (`strong`, `partial`, `miss`, `idk`), `summary`, `explain`, `moves` (list of `[title, detail]`), `closing`, `comment`, `reached`, `deeper`, `got`, `missing`, `try`, `carry`, `body`, `name`, `id`.

If the card rail contains the word `SCENE`, replace that word in the fence with the scene. Do not run a second command to redraw it.

Stderr JSON keys: `screen`, `await`, `id`, `name`, `section`, `phylum`, `practice`, `mode`, `number`, `options`, `fill`, `error`.

## Other commands

These are for tests and for `ida turn` itself. A sitting does not call them.

| Command | Arguments | What it prints |
| --- | --- | --- |
| `open` | `--path` | One JSON line: `kind`, `line`, `bars`. |
| `profile` | `--role`, `--interests`, `--decisions` | Nothing. |
| `next` | `--random`, `--phylum`, `--category`, `--name` (repeatable), `--choices`, `--seed`, `--fresh`, `--daily`, `--spot` | One JSON line: `id`, `name`, `section`, `phylum`, `practice`, `mode`, `number`, `options`. |
| `save` | `--result` (`strong`, `partial`, `miss`, `idk`), `--id`, `--summary`. The same JSON keys as `turn` may arrive on stdin. | Nothing. Stores the reveal for `show`. |
| `show` | `opening`, `menu`, `card`, `strong`, `partial`, `idk`, `summary`. Optional `--beat`, `--phylum`, `--number`, `--total`, `--body`, `--kind`, `--mode`, `--comment`, `--reached`, `--deeper`, `--got`, `--missing`, `--try`, `--name`, `--explain`, `--closing`, `--carry`, `--move`. Prefer stdin JSON. | The plain screen on stdout. |
| `end` | none | Nothing. Closes the sitting. |

`--path` on any command chooses the progress file. The default is `~/.ida/progress.json`.

`IDA_COLOR=always` colors stdout. Leave it unset. `NO_COLOR` and `TERM=dumb` stay plain.
