# ida

When it gets noisy, you can always reach for clarity.

The best ideas from the sharpest minds, ready when a decision gets hard.

ida is a practice skill for thinking clearly. Your agent writes a realistic scenario. You name the way of thinking that fits and apply it in a sentence or two. ida tells you how that read holds up. Then you do it again.

01 Collect the best ideas.
02 Connect them as you go.
03 Reach for them when it counts.

## Install

### Claude Code

In a session:

```text
/plugin marketplace add e-bushi/ida-skill
/plugin install ida@ida-skill
```

`/plugin install` opens the plugin panel so you can confirm. From a shell, the same names are `claude plugin marketplace add e-bushi/ida-skill` and `claude plugin install ida@ida-skill`.

One line, on Claude Code 2.1.275 or later:

```text
/plugin install ida --marketplace e-bushi/ida-skill
```

The shell form of that line needs 2.1.292 or later: `claude plugin install ida --marketplace e-bushi/ida-skill`.

### Cursor and other agents

```bash
npx skills add e-bushi/ida-skill
```

Add `-g` to install it for every project. The skills CLI finds `skills/ida`.

### Copy the folder

```bash
git clone https://github.com/e-bushi/ida-skill.git
mkdir -p ~/.claude/skills ~/.cursor/skills
cp -R ida-skill/skills/ida ~/.claude/skills/ida
cp -R ida-skill/skills/ida ~/.cursor/skills/ida
```

One of those copies is enough.

### Download a release

On the Releases page, download Source code (zip), unzip it, and copy `skills/ida` the same way as above.

## Start

Say "practice with ida".

`/ida` is the command for a copied folder and for `npx skills`. The Claude Code plugin command is `/ida:ida`.

Progress stays in `~/.ida/progress.json` on your machine.

A first run looks like this:

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

## A session

The first time, ida asks what you do, what you are into, and what decisions keep showing up. After that it remembers. Say "update my profile" when that changes.

You can practice a section, name the ideas you want, or let ida choose. Random leans toward ideas you have missed or have not practiced in a while. Every section is open from the start.

You answer in your own words. "idk" is always fine: ida teaches the idea and counts the rep. You can switch to multiple choice when you want an easier rep, and switch back.

Say stop when you are done. ida shows how the sitting went.

## Privacy

Progress stays in `~/.ida/progress.json` on your machine. ida does not upload it. Delete that file to start over.

## Library

443 ways of thinking, 7 sections, 52 categories. Seven entries ship with full text, and they set the voice. The rest use the agent's own knowledge, on purpose.

Regenerate the index after an edit to the source CSV:

```bash
python3 skills/ida/scripts/build_library.py
```

The scripts use the Python standard library only. Check them with:

```bash
python3 skills/ida/scripts/test_ida.py
```

## For reviewers

Example sessions: `skills/ida/examples/transcripts.md`

Grading checklist: `skills/ida/evals/checklist.md`

How a sitting is stored: `skills/ida/references/progress.md`

## Type and color

If you ever skin a page: dark `#111316`, warm white `#EDEAE4`, accent `#0A84FF`. Sora for text. Martian Mono for the wordmark and the cards.
