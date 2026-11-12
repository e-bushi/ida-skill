# Format

Draw these screens yourself. Do not run `render.py` during a sitting. Put each screen in a `text` fence. The sheet is 54 columns. Copy the spacing, the rules, and the prompt line. Do not add a right border. No emoji.

The headline stays on the first question of a first run only:

```text
  When it gets noisy,
  you can always reach for clarity.
```

Questions 02 and 03 reuse the block. Only the counter changes. There is no letter menu. They answer in their own words.

Sign-offs are not on these screens. They rotate on the session sheet only, in this order, and the words stay exact:

1. Clarity is a competitive edge.
2. The people who see clearly win.

Session 1 uses the first. Session 2 uses the second. Then they alternate. One to carry is a sentence in ida's voice. Never attribute it to a real person.

## Names

Say the name on the right. The id is only for `ida.py`. Lane numbers follow this order.

| id | name |
| --- | --- |
| `axiom` | thinking clearly |
| `kanon` | knowing what's true |
| `bias` | blind spots |
| `persona` | reading people |
| `strategy` | playing to win |
| `systema` | seeing ripple effects |
| `momentum` | deciding and acting |

## Bars

Ten cells, always. A strong idea counts as 1. A partial idea counts as half. An idk or a miss adds nothing. The score is the percent of the section that credit represents, rounded. A lane with no credit yet says `new`, not `0%` and not `1/81`.

Each cell is one tenth of the section. Full tenths are █. Any remainder, including the first small bit of credit, is ▒. The rest are ░. One strong idea in a section of 81 is `1%` and a single half cell.

On a STRONG screen the lane line ends with `+1`. On a PARTIAL screen it ends with `+0.5`.

## First run

```text
  ida                                          NO. 001
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  When it gets noisy,
  you can always reach for clarity.


  ■ first session · 3 quick questions · about a minute

  ────────────────────────────────────────────────────
  01 / 03                      WHAT DO YOU DO FOR WORK

  › your own words
```

```text
  ida                                          NO. 001
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ────────────────────────────────────────────────────
  02 / 03               WHAT ARE YOU INTO BESIDES THAT

  › your own words
```

## Menu

```text
  ida · practice                            SESSION 04
  ────────────────────────────────────────────────────

  pick a lane


  01   thinking clearly        ░░░░░░░░░░   new
  02   knowing what's true     ░░░░░░░░░░   new
  03   blind spots             ░░░░░░░░░░   new
  04   reading people          ░░░░░░░░░░   new
  05   playing to win          ░░░░░░░░░░   new
  06   seeing ripple effects   ░░░░░░░░░░   new
  07   deciding and acting     ░░░░░░░░░░   new


  ■ suggested  01, your lightest lane

  › a number, or "surprise me"
```

`suggested` is the lightest lane, the lowest percent, earliest number on a tie.

## Card

```text
  05 · PLAYING TO WIN                          CARD 02
  ┃
  ┃  A seed-stage startup offers you a role. The
  ┃  equity is generous, the salary is 30% lower,
  ┃  and the founder says they'll raise in six
  ┃  months.
  ┃
  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ■ THE QUESTION

    Which way of thinking fits here? Name it and apply
    it in a sentence or two.


  › your answer · "hint" · "idk" · "skip"
```

A spot card asks "What is this called?" and the prompt is `› the name · "idk" · "skip"`. Choice mode numbers the options and the prompt is `› a number · "idk" · "skip"`.

## Strong

```text
  ■■■  STRONG
  ────────────────────────────────────────────────────

  You asked what happens if the raise doesn't come,
  and you priced the downside before the upside.
  That's the move.

  what you reached for    downside first, base rates
  one level deeper        most seed rounds slip, so
                          plan for 12 months, not 6

  05   playing to win          ▒░░░░░░░░░    4%   +1

  › "next" · "why" · "menu"
```

## Partial

```text
  ■■□  PARTIAL
  ────────────────────────────────────────────────────

  what you reached for    the meeting place
  what was missing        what each side expects the
                          other to expect
  try it                  Say the place, then say why
                          both would pick it.

  05   playing to win          ▒░░░░░░░░░    1%   +0.5

  › "retry" · "next" · "show me"
```

## Not yet

idk and a miss both use this header. The file still stores them apart.

```text
  □□□  NOT YET
  ────────────────────────────────────────────────────

  Saying so is the honest start. Here's one way in.

  01  name the bad case       the raise does not come
  02  price that year         salary gap times twelve
  03  then decide             only if that year is
                              survivable

  Name the failure before you admire the offer.

  › "got it" · "another like this" · "menu"
```

## Lanes

```text
  LANES
  01   thinking clearly        ░░░░░░░░░░   new
  05   playing to win          ▒░░░░░░░░░    1%
```

## Session

```text
  ida · session 04 complete                12 NOV 2026
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  5 cards     ■■■ 3     ■■□ 1     □□□ 1


  LANES
  01   thinking clearly        ▒░░░░░░░░░    1%
  02   knowing what's true     ░░░░░░░░░░   new
  03   blind spots             ▒░░░░░░░░░    1%
  04   reading people          ░░░░░░░░░░   new
  05   playing to win          ▒░░░░░░░░░    4%
  06   seeing ripple effects   ░░░░░░░░░░   new
  07   deciding and acting     ░░░░░░░░░░   new


  WHAT YOU REACHED FOR
  · downside first   · base rates


  ONE TO CARRY
  Price the bad case before you fall for the good one.


  ────────────────────────────────────────────────────
  Clarity is a competitive edge.

  › "again" · "menu" · "done"
```

The other sign-off, on the next session:

```text
  ida · session 05 complete                12 NOV 2026
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  5 cards     ■■■ 3     ■■□ 1     □□□ 1


  LANES
  01   thinking clearly        ▒░░░░░░░░░    1%
  02   knowing what's true     ░░░░░░░░░░   new
  03   blind spots             ▒░░░░░░░░░    1%
  04   reading people          ░░░░░░░░░░   new
  05   playing to win          ▒░░░░░░░░░    4%
  06   seeing ripple effects   ░░░░░░░░░░   new
  07   deciding and acting     ░░░░░░░░░░   new


  WHAT YOU REACHED FOR
  · downside first


  ONE TO CARRY
  Name the idea, then say what it changes here.


  ────────────────────────────────────────────────────
  The people who see clearly win.

  › "again" · "menu" · "done"
```

## Machine line

`python3 "$IDA/scripts/ida.py" open` prints one line. Do not show it.

`NEW|bars|axiom:0:0:103,...` means the first run. `READY` means the profile exists. `BACK|Last time: ...|bars|...` is the menu. `RESUME|Last time: ...|bars|...` is an unfinished card.

Each bar field is `id:strong:partial:total`. Draw the bar from the rule above.
