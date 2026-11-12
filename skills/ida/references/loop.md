# Practice loop

Follow `SKILL.md` for the order of operations. This file is the judgment.

On screen, use the names in `references/format.md`. Never show an id (`axiom`, `strategy`, and the rest). The id is only an argument to `ida.py`.

## Profile

First run only. The opening already asks:

1. What do you do for work?
2. What are you into besides that?
3. What decisions keep showing up for you?

One message with all three is fine. Map what they said into role, interests, and decisions. If they skip one, store `""` for that field. Do not invent a job. Do not block practice on a polished profile.

`update my profile`: show the three stored lines, ask what to change, then one quiet `profile` command with only the flags they changed. Do not start a scenario in that turn unless they ask. The next `ida turn` shows the menu.

Use the profile in scenes. Work scenes draw on the role and the decisions. Other scenes draw on the interests. Across a sitting, mix the two. Do not announce the mix. If the profile is empty, write ordinary scenes and do not pretend you know their job.

## Selection

`[1]` section, `[2]` named ideas, `[3]` random. All sections are open. There is no unlocking and no mastery gate.

Section: `sh ~/.agents/skills/ida/ida turn 1` (or 2 through 7). ida picks the idea in that lane. `reasoning tools` sits in both thinking clearly and deciding and acting, so the lane number picks the home.

Named ideas: `sh ~/.agents/skills/ida/ida turn deal <id>`, one short id, one idea. If the reply is the menu and stderr says there is no idea under that name, ask before you invent a card. Do not show that line.

`sh ~/.agents/skills/ida/ida turn next` deals the next card in the same lane. `daily`, `spot`, and `surprise` let ida pick. It prefers ideas with no attempts, then ideas never marked strong, and it skips ideas from the last 8 scenarios when anything else is left.

Stay in the same lane from card to card. Ask for a new choice only when they ask to switch, or when a named list runs out. Then: "That's the list. A section, more ideas, or random?"

Write one scene for the idea stderr names. Do not add a hidden second target. Do not put the scene on the command.

## Writing the card

- A lane card is a stake. `spot` is "what is this called?"
- Second person. A few sentences. One scene.
- Do not name the intended idea in the scene. Do not quote its law. Do not define it in the setup.
- Do not reuse a premise you already used in this sitting.
- Specific: a person, a number, a thing they could lose. No "consider a company".
- A multiple-choice card lists the names ida printed. Do not invent another.
- The command prints the frame with the word SCENE. Paste the frame and replace SCENE with the scene. Keep the question. Do not run a second command.

Mode switches: "multiple choice", "choices", or "easier" means the next deal is `spot`. "free text" or "no choices" leaves spot off. If a card is on screen and they switch, `retry` uses the saved scene.

## Grading

Judge the reasoning. Do not require the exact library string. A clear synonym is the idea.

Grades:

| Grade | When |
| --- | --- |
| strong | They have the idea, and the sentence touches the stake in this scene. |
| partial | Right neighborhood, thin application, or a weaker idea that only half fits. |
| miss | The idea does not fit, or the application contradicts it. |
| idk | They say idk, don't know, no idea, pass, or skip. |

`idk` is its own grade. Do not also record a miss. Then teach: two sentences, the spare voice, tied to this scene.

Decide, free text: name plus application is the strong bar. The right name with no stake is partial.

Decide, multiple choice: the prompt says a number is enough. The right option alone is strong. If they add a sentence that misses the stake, drop it to partial. A wrong option is a miss. A fair other option, with a reason that holds, can be strong. Say which option was the stronger intended one, and why.

Spot: the right name is strong. A clear gloss with no jargon is strong when the jargon is fussy ("a sentence that is true no matter what" for tautology). A neighboring term is a miss (contradiction for a tautology). The right idea under the wrong label is partial.

Fair alternatives: if the reasoning holds for a different library idea, that can be strong. Name the stronger intended pick in the same breath when theirs is thinner. Do not fail them for missing a hidden id.

Synonyms you should accept without fuss:

- working backward, study the failure: inversion
- the measure became the target: goodhart's law
- the missing failures, the planes that came home: survivorship bias
- the place each side expects the other to pick: schelling point
- borrowed wanting, caught the desire: mimetic desire
- remove rather than add: via negativa
- trusting the page outside your field: gell-mann amnesia

Prefer a neighbor that is actually in the library when you say "also consider". You can name an idea outside the library if it is the honest stronger pick. Do not record a stat for an id that is not in the library.

## What to record

One short command, after the answer. No prose on the command. Do not write a file. Do not pipe stdin.

`sh ~/.agents/skills/ida/ida turn strong`

A thin answer is `sh ~/.agents/skills/ida/ida turn partial`. A wrong one is `sh ~/.agents/skills/ida/ida turn miss`. For idk, `sh ~/.agents/skills/ida/ida turn idk`. That prints the banner and the library definition when one is stored. Under the pasted screen, write how it applies to this scene and three steps. If no definition was printed, write the definition there too. Then the choice tool.

The dealt idea takes the grade. If they reached for a fair different idea, say so in the reply after the screen. Do not put a miss on an idea they never mentioned.

The command prints the screen. Paste it. Do not announce the command.

The session summary counts scenarios. A strong idea fills a full share of its section. A partial idea fills half. A miss or an idk fills nothing. The summary still counts one scenario.

`summary` is one line about the premise, not the user's wording and not the answer. The picker uses it only as a reminder not to repeat the scene.

## When they don't understand

"I don't get it", "still fuzzy", "explain differently", or an Other line that says they are not sure they understand is not a new card and not a grade. Do not ask "Clearer now?" as the thing they see.

Write one fresh angle in the reply, before any choice tool. Do not repeat the reveal you already showed. Three parts, in the block from `references/format.md`:

- one line: a plain definition, one sentence.
- everyday: an analogy from ordinary life, not this scene.
- in this scene: the same scenario, read through the idea.

A second request gets a different analogy. No command is required. Do not hide the block in tool output, and do not paste it into the tool's question or options.

The choice tool comes after the block is in the reply. Single select. Short labels only: got it, another angle, next, menu.

## After the card

When the screen ends in a `›` line, that line is the prompt. Honor it. A free-text card has no choice tool and no hint line. The fence ends at the question, and the reply ends so they can type. idk, hint, and skip are still valid typed replies. The choice tool is only a menu, a multiple-choice answer, or the next step after feedback. It is never a substitute for `■ T H E   Q U E S T I O N`.

- "hint" before an answer: `sh ~/.agents/skills/ida/ida turn hint`. Write one nudge in the reply. Do not name the idea. No new grade.
- "idk": `sh ~/.agents/skills/ida/ida turn idk`. Paste the banner and the definition. Under that fence, write how it applies and three steps. Then the choice tool.
- "skip": `sh ~/.agents/skills/ida/ida turn skip`. A miss, then the menu.
- a thin answer: `sh ~/.agents/skills/ida/ida turn partial`. A wrong one: `sh ~/.agents/skills/ida/ida turn miss`. A strong one: `sh ~/.agents/skills/ida/ida turn strong`.
- "why" or "show me": one more sentence in ida's voice. No new card. Do not attribute it to a real person.
- "next", "got it", "another like this", or "retry": another card, same selection. "retry" repeats the same scene.
- "menu": the practice menu.
- "again": a new sitting. "done", stop, or "that's it": end.

On the screen the grades are only STRONG, PARTIAL, and NOT YET. idk and miss both use NOT YET. The file still stores them apart, and neither fills the bar.

`sh ~/.agents/skills/ida/ida turn done` is the summary. Paste it. The sign-off rotates: session 1 uses "Clarity is a competitive edge.", session 2 uses "The people who see clearly win.", then back. Do not show the command. Do not run a second command.

Between scenarios, do not re-teach the whole library. Do not list lanes again unless they ask.
