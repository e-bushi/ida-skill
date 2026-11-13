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

- First run asks the three profile questions, in the 01 / 02 / 03 blocks, under a block-letter ida header, and does not start a card before saving them. Work is one role plus Other. Interests is multiSelect plus Other. The question text is the line after QUESTION:.
- A question typed in Other, or a request to explain it another way, is `ida turn explain`, not a grade. The explanation is the next choice tool's question, built from the QUESTION line. It is not a separate message.
- Returning run goes to the menu, or to resume, with no tagline.
- Sections use the spoken names (playing to win, blind spots, and the rest), not the ids.
- Random does not repeat an id from the last few scenarios when others are available.
- Choice mode accepts a bare correct number as strong. Free text still wants a sentence on the stake for strong.
- `idk` shows the banner and the stored definition when there is one, and does not fill the bar. The reply under that screen says how it applies and gives three steps.
- Screens stay within 76 columns. Rules are 72 characters. Bars are 20 cells with a percent, or `new`, not a fraction like 1/81.
- A dealt card shows a status strip: lane ideas practiced out of that lane's library total, today dots for this sitting, and a streak in days from real card timestamps. `CARD N / total` only when the session length is known. `streak 1d` shows once they have practiced today. The numbers are not invented.
- After every turn, the chat reply contains the full plain screen in a text fence. For idk, that fence is the banner and the library definition when one was printed. It is pasted verbatim before anything else. Under the fence, the reply writes how the idea applies to the scene and three steps. If no definition was printed, the reply writes the definition too. The choice tool comes after that. A collapsed tool log ("output lines hidden") does not count.
- Exactly one shell command per turn, and no chained fallbacks. No `command -v`. No `&&`. No `||`. No temp file. No heredoc. No stdin pipe. No file-edit tool. No prose on the command. The command is `sh` plus the skill directory's `ida` plus `turn`, for example `sh ~/.agents/skills/ida/ida turn`. A lane is `sh ~/.agents/skills/ida/ida turn 1`. A named idea is `sh ~/.agents/skills/ida/ida turn deal inversion`. The next card is `sh ~/.agents/skills/ida/ida turn next`. A grade is `sh ~/.agents/skills/ida/ida turn strong` (or `partial`, or `miss`). idk is `sh ~/.agents/skills/ida/ida turn idk`. No `--help`. No second command to find the binary, to inspect flags, or to show the card. There is no JSON line in the reply.
- With a choice tool, the screen has no `›` line. The tool is single-select, section names are lowercase spoken names, and ida does not write "Question 1 of 1". `sh ~/.agents/skills/ida/ida turn --typed` is the only path that prints a `›` line.
- No choice-tool call without the screen or the explanation already visible in the reply before it. No back-to-back choice calls. If they say they don't understand, the reply is the another-angle block, not a question whose only content is "Clearer now?".
- A card reply includes the frame, the scene written in place of the word SCENE, `■ T H E   Q U E S T I O N`, and the question text in a text fence, and a free-text card ends there. It does not call the choice tool, and it does not print a line of idk, hint, and skip. Those words still count if the person types them. A multiple-choice card shows the question and the options in the fence. The tool, if used, lists only the short option labels.
- After idk, the reply fence is only the lines between BEGIN and END. The choice tool question is every line after QUESTION:, with the line breaks kept. The default is the framed lowercase Sora banner (`QUESTION_BANNER: block`): 5 rows when the name fits on one line, otherwise 4 rows, otherwise one word per 4-row line. Plain text is only when a single word is wider than the frame. Spaced caps are only when the output says `QUESTION_BANNER: spaced`. The scene sentence replaces `<one sentence on this scene>` and the placeholder is not left visible. Each line of that question is within 64 columns. It is not "Where do you want to go from here?". Strong, partial, and miss use their single QUESTION line, and it names the idea.
- The lane menu question is the QUESTION line: what lanes are, why they matter, then the ask, in at most three sentences before the ask. Option labels include what the lane trains and the progress, and daily, spot, and surprise me stay in the list. The pasted menu screen includes the same explanation.
- On screen the grades are STRONG, PARTIAL, and NOT YET. The session sheet rotates "Clarity is a competitive edge." and "The people who see clearly win."
- Nothing the user reads says "mental models" or uses an em dash.
- The wordmark reads as lowercase ida, marked with ■.
