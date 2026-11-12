# Practice loop

Follow `SKILL.md` for the order of operations. This file is the judgment.

## Profile

First run only. The opening already asks:

1. What do you do for work?
2. What are you into besides that?
3. What decisions keep showing up for you?

One message with all three is fine. Map what they said into role, interests, and decisions. If they skip one, store `""` for that field. Do not invent a job. Do not block practice on a polished profile.

`update my profile`: show the three stored lines, ask what to change, then `save-profile` with only the flags they changed. Return to the menu. Do not start a scenario in that turn unless they ask.

Use the profile in scenes. Work scenes draw on the role and the decisions. Other scenes draw on the interests. Across a sitting, mix the two. Do not announce the mix. If the profile is empty, write ordinary scenes and do not pretend you know their job.

## Selection

`[1]` section, `[2]` named ideas, `[3]` random. All sections are open. There is no unlocking and no mastery gate.

Section: `start --selection section --phylum <id>`. Add `--category` only when they name one. Category names must match the library. `reasoning tools` is in both axiom and momentum, so pass `--phylum` with it. Show `render.py sections` when they want the list. The line under the menu says a category is fine.

Named ideas: one `pick.py --name` per idea. If `unmatched` is not empty, show the suggestions and wait. Do not start a card in that turn. Save `queue` to the ids in `queue`. Each card takes the next id with `--ids`.

Random: `pick.py --random`. The script prefers ideas with no attempts, then ideas never marked strong, and it skips ids from the last 8 scenarios when anything else is left. Do not reimplement that by reading every index file.

Stay in the same selection from card to card. Ask for a new choice only when they ask to switch, or when a named list runs out. Then: "That's the list. A section, more ideas, or random?"

`pick.py` may return two `intended` ids. Write one scene that honestly fits both. Do not add a hidden third target.

## Writing the card

- `practice` from the pick is the card's practice. `decide` is a stake. `spot` is "what is this called?"
- Second person. A few sentences. One scene.
- Do not name the intended idea. Do not quote its law. Do not define it in the setup.
- Read `recent_scenarios` from the load. Do not reuse one of those premises.
- Specific: a person, a number, a thing they could lose. No "consider a company".
- Options, when `mode` is `choice`: use the `options` array in that order. Four lines. Do not invent a fifth.
- Save `in_progress` before you show the card. Store the scene text (not the footer), the entry ids, the phylum, the practice, the mode, the number, and the options if any.
- Then render. `next_number` from the load is the number, unless you are resuming. On resume, render the stored prompt and the stored options. Do not call `pick.py` again.

Mode switches: "multiple choice", "choices", or "easier" sets `choice`. "free text" or "no choices" sets `free`. Save the mode. If a card is on screen and they switch to choices, re-render that same scene with `--ids` of the stored entry ids and `--choices`. If they switch to free text, re-render without options.

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

`session_result` is the grade you showed. One per scenario.

`updates` are the library ids their answer actually used:

- strong, partial, or miss on those ids
- for `idk`, or a miss that named nothing in the library: one update on the primary intended id
- do not put a miss on an intended id they never mentioned

The session summary counts scenarios. The bars count ideas with at least one strong. A partial, a miss, or an idk does not fill a bar. Two updates in one scenario can move two bars. The summary still counts one scenario.

`summary` is one line about the premise, not the user's wording and not the answer. The picker uses it only as a reminder not to repeat the scene.

## After the card

Render feedback, then `section_bars` (the category bar only when this sitting is narrowed to a category, then the section bar). Then: `Another, or stop.`

Another, next, or a bare continue stays in the same selection and mode. Stop, done, enough, quit, end, or "that's it" ends the sitting. An unanswered card is not graded. `end` reports it as unanswered. Render `summary`, then the full `bars`.

Between scenarios, do not re-teach the whole library. Do not list sections again unless they ask.
