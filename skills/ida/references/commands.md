# Commands

Read this instead of `--help`. `--help` is refused on purpose. One shell command per user message. No fallback chain. No second command.

The shim is `ida` next to this skill. Run it with `sh`. The usual install:

```bash
sh ~/.agents/skills/ida/ida turn
sh ~/.agents/skills/ida/ida turn 1
sh ~/.agents/skills/ida/ida turn next
sh ~/.agents/skills/ida/ida turn deal inversion
sh ~/.agents/skills/ida/ida turn idk
sh ~/.agents/skills/ida/ida turn strong
sh ~/.agents/skills/ida/ida turn done
```

If SKILL.md was loaded from another directory, use that directory, still with `sh`, still one command. Do not search for a binary. Do not pass `--help`. Do not explore flags.

Do not write a temp file. Do not use a file-edit tool. Do not use a heredoc. Do not pipe stdin. Do not chain commands. Do not put prose on a command. No scene, no summary, no explanation, no answer sentence. A command is a few words, short enough to stay on one line.

Stdout starts with one line for you, then `BEGIN`, then the screen, then `END`. Paste only the lines between `BEGIN` and `END` into a `text` fence. Do not paste the `[ida -> agent]` line. Do not paste the lines after `END`.

On a card, stderr is one line, the idea name, then the same blank tail. Do not paste stderr. Do not show the name. On `idk`, stderr is one reminder, then the blank tail. Do not paste that either. There is no JSON line.

## Collapsed tail

Warp hides a command behind "output lines hidden" and then previews the last line that is not only whitespace or zero-width. A space plus a zero-width space is skipped, so the preview was the last real line of the screen (the question, or a row of the banner).

The last three lines of stdout are braille blanks (U+2800). That character is not whitespace, so Warp keeps the line, and it draws nothing. Each of those lines is wrapped in ANSI conceal (`\033[8m` ... `\033[0m`). If a host strips the conceal codes, the braille blanks are still there and still have no ink. The three lines are the same bytes whether or not `IDA_COLOR` is set. They are written after the screen is painted, so color never changes them. The only thing under the command is "output lines hidden". The lines after `END` are that tail. Do not paste them. The same tail follows any stderr line, so a name or a reminder cannot become the preview either.

The card frame contains the word SCENE. Replace that word in the fence with the scene you write. Keep `■ T H E   Q U E S T I O N` and the question text.

## ida turn

| Argument | Meaning |
| --- | --- |
| (none) | First run: the next profile question. Otherwise the menu. |
| a few words | A profile answer, only before the profile is saved. Keep it short. |
| `1` to `7` | Deal a card in that lane. ida picks the idea. 1 thinking clearly, 2 knowing what's true, 3 blind spots, 4 reading people, 5 playing to win, 6 seeing ripple effects, 7 deciding and acting. |
| a spoken lane name | Same as the number. |
| `deal <id>` | Deal that library id. Example: `deal inversion`. The id is short. Not a sentence. |
| `next` | The next card in the same lane. ida picks. |
| `retry` | The same idea again. You write a new scene in the reply. |
| `daily` | One card chosen for today. |
| `spot` | A quick multiple-choice card. |
| `surprise` | A random card. |
| `strong` | Save strong and show that screen. No answer text on the command. |
| `partial` | Save partial. |
| `miss` | Save a miss and return to the menu. |
| `idk` | Save idk. Print the banner and the library definition when this idea has one. No other arguments. |
| `hint` | The card frame again. Write one nudge in the reply. Do not name the idea. |
| `skip` | Save a miss and return to the menu. |
| `why` | The last feedback, one level down. |
| `menu` | The seven lanes. |
| `done` | End the sitting and show the summary. |
| `--typed` | No choice tool on this host. Remember it. Screens then end with a `›` line. Pass it once, on the first turn. |
| a number during a choice card | That option. A correct option is strong. |

`ida turn idk` reads the pick saved in `~/.ida`. It does not take a definition from you. Seven ideas have a stored definition. The other ideas print the banner only, and you write the definition in the reply under the fence, then how it applies and three steps.

A card has the word SCENE in the rail. The scene is not an argument.

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
