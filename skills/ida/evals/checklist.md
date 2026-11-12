# Eval checklist

For humans grading a session. Do not read this file during practice.

A scene should not contain the idea's name or a paraphrase of its law. Personalize it. The scenes below are the stakes to aim at, not lines to memorize. Synonyms count. A fair different idea, applied to the stake, is not a miss. Say so, and name the stronger pick when theirs is thinner.

Grade the reply ida gives the user, and the scene ida writes. `strong` fills the bar. `partial`, `miss`, and `idk` do not. `idk` is not also stored as a miss.

## 1. Survivorship bias

Scene: they are copying founders who became famous. The people who tried the same thing and disappeared are not in the room.

- Strong: survivorship bias, or "the missing failures", tied to those vanished people.
- Partial: selection bias with no picture of who is absent.
- Miss: "study the winners harder" with no missing data.

## 2. Schelling point

Scene: two people, no way to talk, and they still have to meet.

- Strong: schelling point, focal point, or "the place each expects the other to expect".
- Partial: "they should coordinate" with no focal place.
- Miss: a payoff matrix that never picks a place.

## 3. Goodhart's law

Scene: a bonus on tickets closed. The count rises. The same bugs return under new names.

- Strong: goodhart's law, the measure became the target. Campbell's law is also strong if they say the metric gets corrupted once pay depends on it, and you can name goodhart as the closer fit.
- Partial: "people game metrics" with no link to the bonus.
- Miss: "the team is lazy."

## 4. Mimetic desire

Scene: they want a role mainly because a peer they admire wants it.

- Strong: mimetic desire, borrowed wanting, caught it from the other person. They do not need Girard's name.
- Partial: "jealousy" with no sense that the want itself was copied.
- Miss: "just be more confident."

## 5. Inversion

Scene: a launch plan that only lists how to succeed.

- Strong: inversion, working backward from how the launch fails, then refusing that.
- Also strong: via negativa, if they cut the steps that would sink it and say what they are removing.
- Partial: "think about risks" with no failure path.
- Miss: a longer list of features to add.

## 6. Via negativa

Scene: a weekly report that gains a section every month. Nobody reads the new ones.

- Strong: via negativa, remove sections before adding any.
- Partial: Parkinson's law, if they only say the report expands to fill the meeting.
- Miss: "add an executive summary on top."

## 7. Gell-Mann amnesia

Scene: they catch three errors in a piece about their own field, then trust the next article, which is outside it.

- Strong: gell-mann amnesia. They do not need Crichton's name.
- Partial: confirmation bias, unless they connect it to trusting the unfamiliar page.
- Miss: "that outlet is always wrong."

## 8. Tautology (spot)

Scene: "Either the launch ships on Tuesday, or it does not."

- Strong: tautology, or "true no matter what, so it says nothing".
- Partial: law of excluded middle, if they never say the sentence is empty of news.
- Miss: contradiction.

## 9. Sunk cost fallacy

Scene: four months into an internal tool nobody uses. The question is whether to keep building.

- Strong: sunk cost fallacy. The months are spent. The question is the next month.
- Partial: loss aversion, if they only describe the pain of stopping. Name sunk cost as the stronger pick.
- Miss: "you owe it to the four months."

## 10. Modus ponens (spot)

Scene: "The build passed. If the build passes, we can ship. So we can ship."

- Strong: modus ponens.
- Partial: "a valid argument" with no name, if the gloss matches affirming the antecedent.
- Miss: modus tollens.

## Session shape

Also check:

- First run asks the three profile questions, in the 01 / 02 / 03 blocks, and does not start a card before saving them.
- Returning run goes to the menu, or to resume, with no tagline.
- Sections use the spoken names (playing to win, blind spots, and the rest), not the ids.
- Random does not repeat an id from the last few scenarios when others are available.
- Choice mode accepts a bare correct number as strong. Free text still wants a sentence on the stake for strong.
- `idk` teaches in about two sentences and does not fill the bar.
- Screens stay within 76 columns. Rules are 72 characters. Bars are 20 cells with a percent, or `new`, not a fraction like 1/81.
- After every turn, the chat reply contains the full plain screen in a text fence. For idk, that fence contains the block-letter banner of the name, the two sentences, and the three steps. A collapsed tool log ("output lines hidden") does not count.
- At most one shell command per user message, and it is `ida turn` with at most one short choice. No `--help`. No second command to inspect flags or to show the card. The JSON line is not in the reply.
- With a choice tool, the screen has no `›` line. The tool is single-select, section names are lowercase spoken names, and ida does not write "Question 1 of 1". `ida turn --typed` is the only path that prints a `›` line.
- No choice-tool call without the screen or the explanation already visible in the reply before it. No back-to-back choice calls. If they say they don't understand, the reply is the another-angle block, not a question whose only content is "Clearer now?".
- A card reply includes the scenario, `■ T H E   Q U E S T I O N`, and the question text in a text fence. A free-text card does not call the choice tool at all, not even for idk, hint, or skip. Those words are the line under the question, and the reply ends so the person can type. A multiple-choice card shows the question and the options in the fence. The tool, if used, lists only the short option labels.
- On screen the grades are STRONG, PARTIAL, and NOT YET. The session sheet rotates "Clarity is a competitive edge." and "The people who see clearly win."
- Nothing the user reads says "mental models" or uses an em dash.
- The wordmark reads as lowercase ida, marked with ■.
