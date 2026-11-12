# Library

443 ways of thinking. 7 sections (the phyla, in source order). 52 category names. `reasoning tools` is filed twice, once under axiom (inversion only) and once under momentum, so the index has 53 placements. `library/phyla.json` is the menu of ids. It is small. The spoken names are in `references/format.md`. Read `phyla.json` only when they ask which categories a section holds.

Do not open `library/ida-library.csv` during practice. Do not open every file in `library/index/`. The picker reads the index. If you cannot run it, read only `library/index/<phylum>.json` for the one section they named.

Full text exists only in `library/exemplars.json`, for the seven authored entries. Everyone else is an id, a name, a category, and a practice kind. Use your own knowledge. Do not hand-write laws for the other 436, and do not pretend the file has them.

## Practice kind

`decide`: a short scene with a stake. They name the idea and apply it.

`spot`: vocabulary. A sentence or a tiny claim. They say what it is called. The name is enough.

Spot by whole category:

- axiom / statement properties (tautology, truth value, and the rest)
- axiom / logical operators
- axiom / quantifiers
- axiom / laws of logic
- axiom / proof techniques
- axiom / categorical (aristotelian) logic
- axiom / logical paradoxes (name the paradox, including monty hall; do not turn it into a puzzle to solve)

Spot by single id, inside categories that are otherwise `decide`:

- ad-hoc-hypothesis, non-sequitur, premise-conclusion, prima-facie
- a-priori-vs-a-posteriori, analytic-vs-synthetic, necessity-vs-possibility, usemention-distinction
- null-hypothesis, p-value, confidence-interval, error-bars, statistical-significance, power, central-limit-theorem

Argument tools stay `decide`: burden of proof, hitchens's razor, occam's razor, principle of charity, sagan standard, steelman. So do counterfactual and possible worlds. False positives and false negatives stay `decide`. Fallacies stay `decide`: a person makes the move, the user names it and says what to do with it.

`library/phyla.json` marks each category `spot`, `decide`, or `mixed`.

## Regenerate

From the repo, after a change to the CSV only:

```bash
python3 skills/ida/scripts/build_library.py
```

The script is the only writer of `phyla.json`, `exemplars.json`, and `library/index/`. It keeps the source CSV intact, including punctuation in the original notes. The exemplar file drops em dashes so the voice you read does not teach them.

Ids stay in this order in the data files: axiom, kanon, bias, strategy, systema, persona, momentum. On screen the names are thinking clearly, knowing what's true, blind spots, reading people, playing to win, seeing ripple effects, and deciding and acting. The menu uses that spoken order. All of them are open from the first session.
