# Format

`render.py` is the source of truth. Use it. The rules below are for a sitting where Python cannot run. Count characters before you send. Padding is spaces, never tabs. Treat each character as width 1, including the blocks.

If the chat uses a proportional font, wrap the block in a fence tagged `text`. In a terminal, print it raw. Do not reflow a rendered block.

## Wordmark

```
  █  █▀▄  ▄▀█
  █  █▄▀  █▀█
  reach for clarity
```

The opening kinds:

- `new`: wordmark, blank line, then the intro (tagline, subhead, the three steps, the three questions). No practice menu yet.
- `ready`: wordmark, the profile line, the menu.
- `returning`: wordmark, `Welcome back.` plus the welcome line, the menu.
- `resume`: same as returning, plus `Continue that one, or start fresh.`

Menu, exact:

```
  Practice: [1] a section  [2] pick ideas  [3] random
```

Section list: `All sections are open.` Then `  N  ` + phylum padded to 8 + two spaces + subtitle. Phylum ids stay lowercase.

## Cards

Width 44, counting the borders. Inner width 40.

```
│ <40 characters, space-padded> │
```

That is: `│`, space, 40 characters, space, `│`.

Top, for a decide card:

```
┌─ scenario NN <dashes> <phylum> ─┐
```

`NN` is two digits under 100. The dashes are `─` and the whole line is 44. A spot card puts `<phylum> / spot` in that same slot. If the tag does not fit, drop ` / spot` and put `spot` on the first inner line.

Bottom is `└` + 42 `─` + `┘`.

Wrap the scene on spaces to 40. A single token longer than 40 is cut into 40-character pieces. Blank line between paragraphs, collapsed so you never get two blank lines. One blank line, then the footer. No blank line above the first sentence. No blank line under the footer.

Footer, each sentence wrapped on its own:

- decide, free: `Which way of thinking fits here?` / `Name it and apply it in a sentence or two.` / `Type "idk" anytime.`
- spot, free: `What is this called?` / `The name is enough. Add a few words if you want.` / `Type "idk" anytime.`
- decide, choice: `Which one fits? A number is enough.` / `Add a sentence if you want.` / `Type "idk" anytime.`
- spot, choice: `Which name fits? A number is enough.` / `Type "idk" anytime.`

Options go after the scene, before the footer, with a blank line on each side. `1  ` then the name. Continuation lines indent three spaces. At most 9 options. This skill uses 4.

Sample decide card:

```
┌─ scenario 04 ───────────────── strategy ─┐
│ Your biggest customer asks for a custom  │
│ feature only they would use. They pay    │
│ 40% of your revenue.                     │
│                                          │
│ Which way of thinking fits here?         │
│ Name it and apply it in a sentence or    │
│ two.                                     │
│ Type "idk" anytime.                      │
└──────────────────────────────────────────┘
```

## Feedback

Not a box. No line longer than 44.

- strong: `✓ <name>: strong pick.`
- partial: `~ <name>: partial.`
- miss: `✗ <name>: miss.`
- idk: `? <name>.`

Names stay in library lowercase. Comment lines are the rest of the feedback, wrapped to 42 and indented two spaces.

```
✓ second-order thinking: strong pick.
  You saw the roadmap cost. Also consider
  inversion: what would make losing them
  survivable?
```

## Bars

One width for every row. Label column 41, two spaces, 10 blocks, two spaces, the count right-aligned in 7 (`8/103`, `24/81`).

A phylum label is the id padded to 8, two spaces, the subtitle padded to 31. A category label is the category name padded to 41. Blocks are `█` and `░`. Filled count is `(well * 10 + total // 2) // total`. If they have at least one strong and that rounds to 0, show one block. If every idea in the slice has a strong, show ten.

`well` is how many ideas in that slice have been strong at least once. `total` is how many ideas the slice has. Partials, misses, and idk do not fill a block.

```
axiom     how to think clearly             ░░░░░░░░░░    0/103
strategy  how to win when others play too  ███░░░░░░░    24/81
```

After a card, show the active slice only. At the end of a sitting, show all seven sections.

## Summary

Rules are width 44. The top is `── session ` filled with `─`. The bottom is 44 `─`. Content lines wrap at 44 and are not padded.

Put the counts on one line when they fit: `6 scenarios · 4 strong · 1 partial · 1 idk`. Always include strong. Omit a grade that is zero, except strong. One scenario uses the singular. Zero scenarios is `No scenarios this time.`

```
── session ─────────────────────────────────
6 scenarios · 4 strong · 1 partial · 1 idk
Sharpest: inversion
Revisit: sunk cost fallacy
Next time: pick up in strategy
────────────────────────────────────────────
```

Sharpest is the idea they hit strong most often this sitting, else `none yet`. Revisit is the latest idea that was partial, miss, or idk, else `nothing due`. Next time is `pick up in <section or category>`, `pick up at random`, or `pick up the ideas you chose`.
