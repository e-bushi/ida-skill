# Commands

Read this instead of `--help`. `--help` is refused on purpose. One shell command per user message. No fallback chain. No second command.

The shim is `ida` next to this skill. Run it with `sh`. The usual install:

```bash
sh ~/.agents/skills/ida/ida turn
sh ~/.agents/skills/ida/ida turn "their answer"
sh ~/.agents/skills/ida/ida turn 1 "inversion" "the scene" "one-line summary" "short explanation. How to apply it here."
sh ~/.agents/skills/ida/ida turn idk
sh ~/.agents/skills/ida/ida turn next "next idea" "the scene" "one-line summary" "short explanation. How to apply it here."
sh ~/.agents/skills/ida/ida turn done
```

If SKILL.md was loaded from another directory, use that directory, still with `sh`, still one command. Do not search for a binary. Do not pass `--help`. Do not explore flags.

Do not write a temp file. Do not use a file-edit tool. Do not use a heredoc. Do not pipe stdin. Do not chain commands. The words the command needs are quoted arguments on that one command.

Stdout is the plain screen. Paste it into a `text` fence. Its last line is a spacer, so a collapsed tail is empty. Keep that spacer in the fence.

Stderr stays empty, except after `ida turn idk`, which prints one reminder and then a spacer. Do not paste stderr. Do not quote it. There is no JSON line.

## ida turn

| Argument | Meaning |
| --- | --- |
| (none) | First run: the next profile question. Otherwise the menu. |
| `1` to `7`, then quotes | Deal a card in that lane. 1 thinking clearly, 2 knowing what's true, 3 blind spots, 4 reading people, 5 playing to win, 6 seeing ripple effects, 7 deciding and acting. |
| a spoken lane name, then quotes | Same as the number. |
| `"idea"` | First quote. A library name. ida deals that idea. |
| `"scenario"` | Second quote. The scene the person reads. Saved in `~/.ida`. |
| `"summary"` | Third quote. One line about the premise. Saved. |
| `"explanation"` | Fourth quote. One or two sentences: the idea, then how to apply it. Saved. `idk` and `hint` reuse it. |
| `daily`, `spot`, `surprise` | Same quotes when you already know the idea. With no quotes, ida picks and saves a short explanation from the library. |
| `next` | The next card. Pass a new idea and the same three quotes. |
| `retry` | The same idea again. The saved scene is reused when you pass no quotes. |
| `"their answer"` | A free-text answer while a card is open. One quoted argument. Recorded as strong. |
| `partial "their answer"` | A thin answer. |
| `miss "their answer"` | A wrong answer. Returns to the menu. |
| `idk` | Save idk and print the full reveal from the saved card: the name, the 3-row banner, the short explanation, how to apply it. No other arguments. |
| `hint` | The card again, plus one nudge from the saved explanation. No banner. |
| `skip` | Save a miss and return to the menu. |
| `why` | The last feedback, one level down. |
| `menu` | The seven lanes. |
| `done` | End the sitting and show the summary. |
| `--typed` | No choice tool on this host. Remember it for the sitting. Screens then end with a `›` line. Pass it once, on the first turn. |
| a number during a choice card | That option. A correct option is strong. |

`ida turn idk` does not take the explanation again. If you did not pass one when you dealt the card, ida uses the library line it saved at deal time.

A card has no `SCENE` token. The scene you quoted is already on the screen.

## Other commands

These are for tests and for `ida turn` itself. A sitting does not call them.

| Command | Arguments | What it prints |
| --- | --- | --- |
| `open` | `--path` | One JSON line, then a spacer. |
| `profile` | `--role`, `--interests`, `--decisions` | Nothing. |
| `next` | `--random`, `--phylum`, `--category`, `--name` (repeatable), `--choices`, `--seed`, `--fresh`, `--daily`, `--spot` | One JSON line, then a spacer. |
| `save` | `--result` (`strong`, `partial`, `miss`, `idk`), `--id`, `--summary` | Nothing. |
| `show` | `opening`, `menu`, `card`, `strong`, `partial`, `idk`, `summary`. Optional `--beat`, `--phylum`, `--number`, `--total`, `--body`, `--kind`, `--mode`, `--comment`, `--reached`, `--deeper`, `--got`, `--missing`, `--try`, `--name`, `--explain`, `--closing`, `--carry` | The plain screen on stdout, then a spacer. |
| `end` | none | Nothing. Closes the sitting. |

`--path` on any command chooses the progress file. The default is `~/.ida/progress.json`.

`IDA_COLOR=always` colors stdout. Leave it unset. `NO_COLOR` and `TERM=dumb` stay plain.
