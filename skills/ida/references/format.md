# Format

`sh ~/.agents/skills/ida/ida turn` prints the screen in plain text on stdout. One command. No fallback chain. After every turn, paste that stdout verbatim into a `text` fence in the chat reply. Every time. Every host. One shell command per user message. Never `--help`. The arguments are in `references/commands.md`.

Tool output is not the screen. Warp hides it behind "output lines hidden", so an idk banner that exists only in the tool log never appears. The fence includes the full banner and every spacer line, with no ANSI codes. Do not paste stderr.

A spacer looks blank and is not an empty line. One spacer separates related lines. Two spacers separate unrelated blocks. The sheet is 76 columns. Rules are 72 characters after a 2-space indent. No emoji. After `END`, three concealed braille blanks keep Warp's preview empty. The trick is in `references/commands.md`. Do not paste those lines.

Commands stay short. No prose on the command line. `ida turn deal <id>` or `ida turn next` saves the idea. The card frame prints the word SCENE. In the reply, replace that word with the scene you write. `ida turn idk` prints the banner and the library definition when one is stored. Under that fence, write how it applies to the scene and three steps. If no definition was printed, write the definition there too. Do not write a temp file. Do not use a heredoc. Do not pipe stdin. Do not use a file-edit tool.

Levels: a block banner only when they say idk. Spaced caps for section names and labels. Plain sentences for the scene and the praise. Small labels joined with · for prompts.

The heavy rule opens and closes a screen. The light rule splits inside. ■ is the accent. A card always includes the frame, `■ T H E   Q U E S T I O N`, and the question text, and a multiple-choice card also includes the numbered options. The command leaves the word SCENE in the rail. The reply replaces SCENE with the scene and keeps the question. A free-text card ends there. It does not call the choice tool, and it does not list idk, hint, or skip. Those words are still accepted if the person types them. The tool is for menus, multiple-choice labels, and the next step after feedback. Profile questions have no `›` line. `sh ~/.agents/skills/ida/ida turn --typed` is the fallback, decided once per sitting, and only then does a `›` line appear.

The headline stays on the first question of a first run only:

```text
  When it gets noisy,
  you can always reach for clarity.
```

Questions 02 and 03 reuse the block. Only the counter changes.

Sign-offs rotate on the session sheet only, in this order, words exact:

1. Clarity is a competitive edge.
2. The people who see clearly win.

One to carry is a sentence in ida's voice. Never attribute it to a real person.

## Names

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

Twenty cells. A strong idea counts as 1. A partial counts as half. idk and miss add nothing. The score is a percent. A lane with no credit says `new`. Full twentieths are █. Any remainder is ▒. A strong card adds `+1`. A partial adds `+0.5`.

## Hosts

Claude Code, Warp, and Cursor may show command output, and they may not. Warp collapses a long block to "output lines hidden". The reply fence is still required. Paste the lines between `BEGIN` and `END`. On idk that fence comes before the three steps and before the choice tool. Leave `IDA_COLOR` unset so the screen stays plain and can be pasted. Set it only if you still paste the plain fence.

```bash
sh ~/.agents/skills/ida/ida turn idk
```

## Another angle

When the reveal did not land, this block is the reply. The choice tool comes after it, not instead of it.

```text
  ■ A N O T H E R   A N G L E
 ​
 ​
  one line              A sentence true either way says nothing.
 ​
  everyday              Like saying the bus is on time or it is not.
 ​
  in this scene         The launch line did not tell you whether to ship.
```

## Choices

If the host has a choice tool, use it for a menu, a multiple-choice answer, or the next step after feedback. Do not use it to ask a free-text question. The card's question stays in the fence. Claude Code: `AskUserQuestion`. Cursor: `cursor/ask_question` when that method is available, otherwise AskQuestion if it is in your tool list. Warp's agent: `AskUserQuestion` when the host exposes it. Single select, not checkboxes. Do not write "Question 1 of 1". Labels are lowercase spoken names, and on a multiple-choice card they are only the short option names. Put the percent, or a one-line reason, in the description. If there is no such tool, the first command is `sh ~/.agents/skills/ida/ida turn --typed` and the `›` line is the choice.

Use it for the practice menu, the seven lanes, multiple choice, and the after-answer actions (next, why, menu, retry).

## Screens

```text
  ida                                                                NO. 001
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ​
 ​
  When it gets noisy,
  you can always reach for clarity.
 ​
 ​
  ■ first session · 3 quick questions · about a minute
 ​
 ​
  ────────────────────────────────────────────────────────────────────────
  01 / 03
 ​
  W H A T   D O   Y O U   D O   F O R   W O R K
```

```text
  ida                                                                NO. 001
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ​
 ​
  ────────────────────────────────────────────────────────────────────────
  02 / 03
 ​
  W H A T   A R E   Y O U   I N T O   B E S I D E S   T H A T
```

```text
  ida · practice                                                  SESSION 04
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ​
 ​
  pick a lane
 ​
 ​
  01  T H I N K I N G   C L E A R L Y
      ░░░░░░░░░░░░░░░░░░░░   new
 ​
  02  K N O W I N G   W H A T' S   T R U E
      ░░░░░░░░░░░░░░░░░░░░   new
 ​
  03  B L I N D   S P O T S
      ░░░░░░░░░░░░░░░░░░░░   new
 ​
  04  R E A D I N G   P E O P L E
      ░░░░░░░░░░░░░░░░░░░░   new
 ​
  05  P L A Y I N G   T O   W I N
      ░░░░░░░░░░░░░░░░░░░░   new
 ​
  06  S E E I N G   R I P P L E   E F F E C T S
      ░░░░░░░░░░░░░░░░░░░░   new
 ​
  07  D E C I D I N G   A N D   A C T I N G
      ░░░░░░░░░░░░░░░░░░░░   new
 ​
 ​
  ■ suggested  01, your lightest lane
```

```text
  05 · P L A Y I N G   T O   W I N                                    CARD 2
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ​
 ​
  ┃
  ┃  A seed-stage startup offers you a role. The equity is generous, the
  ┃  salary is 30% lower, and the founder says they'll raise in six
  ┃  months.
  ┃
  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ​
 ​
  ■ T H E   Q U E S T I O N
 ​
    Which way of thinking fits here? Name it and apply it in a sentence or
    two.
```

```text
  ■■■  S T R O N G
 ​
  You asked what happens if the raise doesn't come, and you priced the
  downside before the upside. That's the move.
 ​
 ​
  ────────────────────────────────────────────────────────────────────────
 ​
  you reached for       D O W N S I D E F I R S T , B A S E R A T E S
 ​
  one level deeper      most seed rounds slip, so plan for 12 months, not 6
 ​
 ​
  ────────────────────────────────────────────────────────────────────────
 ​
  05  P L A Y I N G   T O   W I N
      ▒░░░░░░░░░░░░░░░░░░░    4%  +1
```

```text
  ■■□  P A R T I A L
 ​
 ​
  ────────────────────────────────────────────────────────────────────────
 ​
  what you got          the meeting place
 ​
  what was missing      what each side expects the other to expect
 ​
  try it                Say the place, then say why both would pick it.
 ​
 ​
  ────────────────────────────────────────────────────────────────────────
 ​
  05  P L A Y I N G   T O   W I N
      ▒░░░░░░░░░░░░░░░░░░░    1%  +0.5
```

```text
  □□□  not yet. here's what to reach for.
 ​
 ​
  ▀█▀░█▀█░█░█░█▀▀░█▀▄░▄▀▀░▀█▀░▄▀▄░█▀█░
   █░ ███░█░█░█▀░ █▀█░▀▀▄░ █░ █░█░███░
  ▄█▄░█░█░ ▀░ █▄▄░█░█░▀▄▀░▄█▄░▀▄▀░█░█░
 ​
 ​
  to master a problem, study how to fail at it, then refuse to.
```

```text
  L A N E S
  01  T H I N K I N G   C L E A R L Y
      ░░░░░░░░░░░░░░░░░░░░   new
  05  P L A Y I N G   T O   W I N
      ▒░░░░░░░░░░░░░░░░░░░    1%
```

```text
  ida · session 04 complete                                      12 NOV 2026
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ​
 ​
  5 cards  ■■■ 3 strong  ■■□ 1 partial  □□□ 1 not yet
 ​
 ​
  L A N E S
 ​
  01  T H I N K I N G   C L E A R L Y
      ▒░░░░░░░░░░░░░░░░░░░    1%
 ​
  02  K N O W I N G   W H A T' S   T R U E
      ░░░░░░░░░░░░░░░░░░░░   new
 ​
  03  B L I N D   S P O T S
      ▒░░░░░░░░░░░░░░░░░░░    1%
 ​
  04  R E A D I N G   P E O P L E
      ░░░░░░░░░░░░░░░░░░░░   new
 ​
  05  P L A Y I N G   T O   W I N
      ▒░░░░░░░░░░░░░░░░░░░    4%
 ​
  06  S E E I N G   R I P P L E   E F F E C T S
      ░░░░░░░░░░░░░░░░░░░░   new
 ​
  07  D E C I D I N G   A N D   A C T I N G
      ░░░░░░░░░░░░░░░░░░░░   new
 ​
 ​
  W H A T   Y O U   R E A C H E D   F O R
 ​
  ■ downside first
 ​
  ■ base rates
 ​
 ​
  O N E   T O   C A R R Y
 ​
  Price the bad case before you fall for the good one.
 ​
 ​
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ​
  Clarity is a competitive edge.
```

```text
  ida · session 05 complete                                      12 NOV 2026
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ​
 ​
  5 cards  ■■■ 3 strong  ■■□ 1 partial  □□□ 1 not yet
 ​
 ​
  L A N E S
 ​
  01  T H I N K I N G   C L E A R L Y
      ▒░░░░░░░░░░░░░░░░░░░    1%
 ​
  02  K N O W I N G   W H A T' S   T R U E
      ░░░░░░░░░░░░░░░░░░░░   new
 ​
  03  B L I N D   S P O T S
      ▒░░░░░░░░░░░░░░░░░░░    1%
 ​
  04  R E A D I N G   P E O P L E
      ░░░░░░░░░░░░░░░░░░░░   new
 ​
  05  P L A Y I N G   T O   W I N
      ▒░░░░░░░░░░░░░░░░░░░    4%
 ​
  06  S E E I N G   R I P P L E   E F F E C T S
      ░░░░░░░░░░░░░░░░░░░░   new
 ​
  07  D E C I D I N G   A N D   A C T I N G
      ░░░░░░░░░░░░░░░░░░░░   new
 ​
 ​
  W H A T   Y O U   R E A C H E D   F O R
 ​
  ■ downside first
 ​
 ​
  O N E   T O   C A R R Y
 ​
  Name the idea, then say what it changes here.
 ​
 ​
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ​
  The people who see clearly win.
```


## Machine line

A sitting runs `ida turn` only. `open` and `next` print one JSON line for tests, then the blank tail. Do not show that JSON.
