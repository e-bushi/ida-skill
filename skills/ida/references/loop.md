# Practice loop

Follow `SKILL.md` for the order of operations. This file is the judgment.

On screen, use the names in `references/format.md`. Never show an id (`axiom`, `strategy`, and the rest). The id is only an argument to `ida.py`.

## Profile

First run only. The opening already asks:

1. What do you do for work?
2. What are you into besides that?
3. What decisions keep showing up for you?

One message with all three is fine. Map what they said into role, interests, and decisions. If they skip one, store `""` for that field. Do not invent a job. Do not block practice on a polished profile.

`update my profile`: show the three stored lines, ask what to change, then `ida.py profile` with only the flags they changed. Return to the menu. Do not start a scenario in that turn unless they ask.

Use the profile in scenes. Work scenes draw on the role and the decisions. Other scenes draw on the interests. Across a sitting, mix the two. Do not announce the mix. If the profile is empty, write ordinary scenes and do not pretend you know their job.

## Selection

`[1]` section, `[2]` named ideas, `[3]` random. All sections are open. There is no unlocking and no mastery gate.

Section: `ida.py next --phylum <id>`. Add `--category` only when they name one. `reasoning tools` is in both axiom and momentum, so pass `--phylum` with it.

Named ideas: `ida.py next --name "<idea>"`, once per name. If the line starts with `UNMATCHED`, ask before a card. Do not show the line.

Random: `ida.py next --random`. The script prefers ideas with no attempts, then ideas never marked strong, and it skips ids from the last 8 scenarios when anything else is left.

Stay in the same selection from card to card. Ask for a new choice only when they ask to switch, or when a named list runs out. Then: "That's the list. A section, more ideas, or random?"

`next` may name two ideas, tab-separated after the first. Write one scene that honestly fits both. Do not add a hidden third target.

## Writing the card

- The first field from `next` is `decide` or `spot`. `decide` is a stake. `spot` is "what is this called?"
- Second person. A few sentences. One scene.
- Do not name the intended idea. Do not quote its law. Do not define it in the setup.
- Do not reuse a premise you already used in this sitting.
- Specific: a person, a number, a thing they could lose. No "consider a company".
- When the line contains `opts`, those names are the choices, in that order. Four lines. Do not invent a fifth.
- Draw the card from `references/format.md`. `next` already stored the idea. Do not run a second command before you show it.

Mode switches: "multiple choice", "choices", or "easier" means the next `ida.py next` gets `--choices`. "free text" or "no choices" leaves it off. If a card is on screen and they switch, draw that same scene again in the new shape.

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

One command, after the answer:

`python3 "$IDA/scripts/ida.py" save --result strong --summary "one line about the premise"`

Add `--id <id>` when they practiced a different library idea than the one `next` stored. For `idk`, or a miss that named nothing in the library, omit `--id` so the stored idea takes the grade. Do not put a miss on an idea they never mentioned.

The command prints nothing. Do not announce it.

The session summary counts scenarios. A strong idea fills a full share of its section. A partial idea fills half. A miss or an idk fills nothing. The summary still counts one scenario.

`summary` is one line about the premise, not the user's wording and not the answer. The picker uses it only as a reminder not to repeat the scene.

## After the card

Draw the feedback screen, then that section's bar if you have the counts. Then: `Another, or stop.`

Another, next, or a bare continue stays in the same selection and mode. Stop, done, enough, quit, end, or "that's it" ends the sitting. An unanswered card is not graded. Run `ida.py end` with no output, then `ida.py open` once if you need fresh bar counts, and draw the summary and the seven bars. Do not show either command.

Between scenarios, do not re-teach the whole library. Do not list sections again unless they ask.
