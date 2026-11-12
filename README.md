# ida

When it gets noisy, you can always reach for clarity.

The best ideas from the sharpest minds, ready when a decision gets hard.

ida is a practice skill for thinking clearly. Your agent writes a realistic scenario. You name the way of thinking that fits and apply it in a sentence or two. ida tells you how that read holds up. Then you do it again.

01 Collect the best ideas.
02 Connect them as you go.
03 Reach for them when it counts.

## Install

The skill is the `skills/ida` folder. Copy that folder into a skills directory. The folder name should stay `ida`.

Claude Code, for every project on this machine:

```bash
mkdir -p ~/.claude/skills
cp -R skills/ida ~/.claude/skills/ida
```

Cursor, for every project on this machine:

```bash
mkdir -p ~/.cursor/skills
cp -R skills/ida ~/.cursor/skills/ida
```

A project-only copy works too: `.claude/skills/ida` or `.cursor/skills/ida`. Cursor also reads `.agents/skills/ida`.

Other agents that load a `SKILL.md` from a skills folder can use the same copy. Codex looks in `~/.codex/skills/`.

If your machine can read this repo:

```bash
npx skills add e-bushi/ida-skill --skill ida
```

The repo is private. Copying the folder does not need that command.

Then start a session with "practice with ida", "sharpen my thinking", or `/ida`.

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
