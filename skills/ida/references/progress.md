# Progress

Version 1. Path: `~/.ida/progress.json`. The directory is created on the first load. Override with `--path` or `IDA_PROGRESS` (tests do this). Do not commit the file.

These operations are the memory API. The script is the file adapter. A later server should accept the same inputs and return the same outputs. Practice code calls the operations. It does not invent a second writer, and this version does not call a network.

A sitting does not call this script. It calls `sh ~/.agents/skills/ida/ida turn`, which uses these operations. `open` prints one line. `save`, `profile`, and `end` print nothing. Version 1 files load unchanged. Nothing is dropped. Welcome lines use the spoken section names. The stored ids do not change.

| Operation | Command |
| --- | --- |
| loadProgress | `progress.py load` |
| saveProfile | `progress.py save-profile` |
| startSession | `progress.py start` |
| saveSession | `progress.py save` (JSON on stdin) |
| recordAttempt | `progress.py record` (JSON on stdin) |
| endSession | `progress.py end` |

Stdout is JSON. Errors are plain text on stderr and exit 1. `load`, `save-profile`, `start`, `save`, and `record` print the same view: the file plus `welcome`, `next_number`, `bars`, and `section_bars`. Those four keys are not part of the file. Do not write the view back to disk. `end` prints `{ "summary", "bars" }` instead.

Writes are atomic: a temp file in the same directory, then replace. There is no file lock in v1.

If `version` is missing or is not `1`, stop. Do not guess a migration.

## File

```json
{
  "version": 1,
  "profile": {
    "role": "product designer",
    "interests": "climbing, cooking",
    "decisions": "what to ship, and whether to move",
    "updated_at": "2026-11-12T01:42:00Z"
  },
  "session": null,
  "entries": {
    "schelling-point": {
      "name": "schelling point",
      "attempts": 1,
      "strong": 1,
      "partial": 0,
      "miss": 0,
      "idk": 0,
      "last_practiced": "2026-11-12T01:42:00Z",
      "last_result": "strong"
    }
  },
  "recent_scenarios": [],
  "history": []
}
```

`profile` is null until the first save. The three text fields are strings, not lists. Empty string means they skipped.

`entries` only appears for ids that have been practiced. `strong >= 1` is "practiced well" and is the only thing that fills a bar.

`idk` is stored on its own. It does not increment `miss`. It also does not fill a bar. The product line "idk counts as a miss" means: teach it, and do not treat it as a success. The summary shows `idk` separately, which is why the file does not fold it into `miss`.

## Session

`start` opens a session. Selection is `section`, `pick`, or `random`. Mode is `free` or `choice` (the default is `free`). A section requires a phylum. Category is optional. Names are matched without case sensitivity. An unknown section is an error.

If a card is `in_progress`, `start` refuses unless `--fresh`. Fresh ends the current sitting first (and returns it as `ended` on the payload) and then opens a new one. An empty sitting with no card is dropped instead of being written to history.

While a session is open, `save` may set only: `selection`, `phylum`, `category`, `mode`, `queue`, `in_progress`, `number`. It cannot set `counts` or `log`. `queue` is a list of library ids, capped at 30.

`in_progress` is the card on screen:

```json
{
  "number": 4,
  "practice": "decide",
  "phylum": "strategy",
  "category": "game theory",
  "entry_ids": ["schelling-point"],
  "prompt": "Phones are dead. You and a friend still have to meet.",
  "mode": "free",
  "options": []
}
```

`options` is a list of `{ "id", "name" }` in display order, used for choice mode. The script numbers them. The prompt cap is 2000 characters. Em dashes in the prompt or the summary are removed on the way in.

`number` on the session is the last card you showed or finished. `next_number` in the load payload is the number to use for a new card.

## record

```json
{
  "session_result": "strong",
  "updates": [
    {"id": "schelling-point", "result": "strong"}
  ],
  "summary": "meet with phones dead"
}
```

`session_result` is one of `strong`, `partial`, `miss`, `idk`. It increments the session counters once.

Each update increments that id's `attempts` and that result. See `references/loop.md` for which ids belong in `updates`. The summary cap is 280 characters.

Recording clears `in_progress`, appends `recent_scenarios`, and drops any queued ids that were the card's `entry_ids`. Recent scenarios are capped at 24. The picker skips ids from the last 8.

A recent row:

```json
{
  "at": "2026-11-12T01:42:00Z",
  "entry_ids": ["schelling-point"],
  "phylum": "strategy",
  "category": "game theory",
  "practice": "decide",
  "summary": "meet with phones dead",
  "result": "strong",
  "mode": "free"
}
```

## end

Closes the session. History keeps the derived totals, not the full log. History is capped at 40. The payload is `{ "summary": { ... }, "bars": [ ... ] }`. Render both.

Summary fields: `scenarios`, `strong`, `partial`, `miss`, `idk`, `sharpest`, `revisit`, `next`, `unanswered`.

`sharpest` is the name most often marked strong this sitting. Ties go to the later one. `revisit` is the latest name marked partial, miss, or idk. `next` defaults from the selection: the category if they narrowed, otherwise the phylum, `pick up at random` for random, `pick up the ideas you chose` if the queue still has ids. Pass `--next` only to override that sentence (without the `Next time:` prefix).

`unanswered` is true when a card was still on screen. That card is not graded.

A sitting with zero cards and nothing unanswered is not written to history.

## Bars

`bars` is one row per phylum: `{ "phylum", "subtitle", "well", "total" }`. `well` counts ids in that phylum with `strong >= 1`. `section_bars` is the category row (only when the sitting has a category) plus the active phylum row. Render `section_bars` after a card. Render `bars` at the end.

## Welcome

`welcome.kind`:

| kind | when |
| --- | --- |
| new | no profile |
| ready | profile saved, no sitting and no history |
| resume | a card is in progress. `line` is `Last time: <phylum>, scenario <n>.` |
| returning | a finished sitting, or a sitting between cards. `line` names the phylum and either the scenario number or how many scenarios |

One scenario uses the singular.

## Hand write

Only when Python cannot run. Same schema, same caps, same atomic replace. Strip `welcome`, `bars`, `section_bars`, and `next_number` before writing. Keep `version` at 1.
