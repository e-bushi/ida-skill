# Format

Draw these screens yourself. Do not run `render.py` during a sitting. Put each screen in a `text` fence. Every line is at most 56 columns. Content lines start with a left rail (`│ `) and have no right border. Blank lines are blank. The only accent is ■. Labels are in caps. No emoji. Every screen ends with `│ ›`.

The two sign-off lines are locked. Do not rewrite them. The first run shows the first line once, as the tagline, and does not repeat a sign-off. After that, alternate them, starting with the second line on the menu.

1. When it gets noisy, you can always reach for clarity.
2. The best ideas from the sharpest minds, ready when a decision gets hard.

## Names

Say the name on the right. The id is only for `ida.py`.

| id | name |
| --- | --- |
| `axiom` | thinking clearly |
| `kanon` | knowing what's true |
| `bias` | blind spots |
| `persona` | reading people |
| `strategy` | playing to win |
| `systema` | seeing ripple effects |
| `momentum` | deciding and acting |

Drop the old subtitle. The name already says it.

## Bars

Ten cells, always. A strong idea counts as 1. A partial idea counts as half. An idk or a miss adds nothing. The score on the right is the percent of the section that credit represents, rounded. It is not a fraction like 1/81.

Each cell is one tenth of the section. Full tenths are █. Any remainder, including the first small bit of credit, is ▒. The rest are ░. One strong idea in a section of 81 is `1%` and a single half cell.

## First run

```text
│ ■ ida

│ When it gets noisy, you can always reach for clarity.

│ 01
│ What do you do for work?

│ 02
│ What are you into besides that?

│ 03
│ What decisions keep showing up for you?

│ ›
```

## Menu

Returning people see this, with no tagline. A resume uses the shorter screen under it.

```text
│ ■ ida

│ WELCOME BACK
│ Last time: playing to win, 4 scenarios.

│ PRACTICE
│ 1  THINKING CLEARLY
│ 2  KNOWING WHAT'S TRUE
│ 3  BLIND SPOTS
│ 4  READING PEOPLE
│ 5  PLAYING TO WIN
│ 6  SEEING RIPPLE EFFECTS
│ 7  DECIDING AND ACTING

│ Or name the ideas. Or say random.

│ The best ideas from the sharpest minds, ready when a
│ decision gets hard.

│ ›
```

```text
│ ■ ida

│ WELCOME BACK
│ Last time: playing to win, scenario 3.

│ Continue that one, or start fresh.

│ The best ideas from the sharpest minds, ready when a
│ decision gets hard.

│ ›
```

## Scenario

```text
│ SCENARIO 04
│ PLAYING TO WIN

│ Your biggest customer asks for a custom feature only
│ they would use. They pay 40% of your revenue.

│ Which way of thinking fits here? Name it and apply it
│ in a sentence or two. idk is fine.

│ When it gets noisy, you can always reach for clarity.

│ ›
```

A spot puts `SPOT` under the section name and asks what it is called.

## Feedback

```text
│ STRONG
│ second-order thinking

│ You saw the roadmap cost. Also consider inversion:
│ what would make losing them survivable?

│ When it gets noisy, you can always reach for clarity.

│ ›
```

`PARTIAL`, `MISS`, and `IDK` use the same shape. The label is the grade. The idea name stays lowercase.

## Progress

```text
│ PROGRESS

│ THINKING CLEARLY       ░░░░░░░░░░    0%
│ PLAYING TO WIN         ▒░░░░░░░░░    1%

│ When it gets noisy, you can always reach for clarity.

│ ›
```

## Summary

```text
│ SESSION

│ 6 scenarios
│ 4 strong · 1 partial · 1 idk

│ SHARPEST
│ inversion

│ REVISIT
│ sunk cost fallacy

│ NEXT
│ pick up in playing to win

│ When it gets noisy, you can always reach for clarity.

│ ›
```

## Machine line

`python3 "$IDA/scripts/ida.py" open` prints one line. Do not show it.

`NEW|bars|axiom:0:0:103,...` means the first run. `READY` means the profile exists. `BACK|Last time: ...|bars|...` is the menu. `RESUME|Last time: ...|bars|...` is an unfinished card.

Each bar field is `id:strong:partial:total`. Draw the bar from the rule above.
