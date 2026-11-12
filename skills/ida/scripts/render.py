"""Sheets for ida. 76 columns. Rules are 72 characters, indented 2.

Four levels: a block banner only on an idk reveal, spaced caps for
names and labels, plain sentences, and small labels joined with a dot.
The heavy rule opens and closes a screen. The light rule splits inside.
■ is the accent. These functions are what `ida.py show` prints.
"""

from __future__ import annotations

from banner import render_name, spaced_caps
from common import BAR_BLOCKS, DISPLAY_NAMES, DISPLAY_ORDER, RULE_WIDTH, SCREEN_WIDTH, SIGNOFFS, SPACER

QUESTIONS = (
    "What do you do for work?",
    "What are you into besides that?",
    "What decisions keep showing up for you?",
)


def wrap(text: str, width: int) -> list[str]:
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    current = ""
    for word in words:
        pieces = [word[i : i + width] for i in range(0, len(word), width)] if len(word) > width else [word]
        for piece in pieces:
            if not current:
                current = piece
            elif len(current) + 1 + len(piece) <= width:
                current = current + " " + piece
            else:
                lines.append(current)
                current = piece
    if current:
        lines.append(current)
    return lines


def display_name(phylum: str) -> str:
    return DISPLAY_NAMES[phylum]


def spaced(text: str) -> str:
    return spaced_caps(text)


def _check(lines: list[str]) -> str:
    for line in lines:
        if len(line) > SCREEN_WIDTH:
            raise ValueError(f"line is {len(line)} cols: {line!r}")
    return "\n".join(lines)


def spread(left: str, right: str) -> str:
    gap = SCREEN_WIDTH - len(left) - len(right)
    if gap < 1:
        gap = 1
    return left + (" " * gap) + right


def gap(count: int = 1) -> list[str]:
    return [SPACER] * count


def choices(lines: list[str], prompt: str, typed: bool) -> None:
    """A › line is only the fallback when the host has no choice tool."""
    if typed:
        lines.extend(gap(2))
        lines.append(prompt)


def heavy() -> str:
    return "  " + ("━" * RULE_WIDTH)


def thin() -> str:
    return "  " + ("─" * RULE_WIDTH)


def bar_cells(strong: int, partial: int, total: int) -> tuple[str, int]:
    """20 cells for the share of a section.

    A strong idea counts as 1. A partial idea counts as half. idk and miss
    add nothing. Full twentieths are █. A remainder is ▒, including the
    first bit of credit. The rest are ░. Percent is round(100 * credit / total).
    """
    if total <= 0 or (strong <= 0 and partial <= 0):
        return "░" * BAR_BLOCKS, 0
    credit = strong + 0.5 * partial
    if credit > total:
        credit = float(total)
    percent = int(round(100 * credit / total))
    percent = max(0, min(100, percent))
    exact = BAR_BLOCKS * credit / total
    full = min(BAR_BLOCKS, int(exact))
    remainder = exact - full
    half = 1 if full < BAR_BLOCKS and remainder > 1e-9 else 0
    if full + half > BAR_BLOCKS:
        half = 0
    empty = BAR_BLOCKS - full - half
    return ("█" * full) + ("▒" * half) + ("░" * empty), percent


def score_field(strong: int, partial: int, percent: int) -> str:
    if strong <= 0 and partial <= 0:
        return " new"
    return f"{percent}%".rjust(4)


def lane_lines(phylum: str, strong: int, partial: int, total: int, index: int | None = None, delta: str = "") -> list[str]:
    if index is None:
        index = DISPLAY_ORDER.index(phylum) + 1
    cells, percent = bar_cells(strong, partial, total)
    score = score_field(strong, partial, percent)
    bar = f"      {cells}  {score}"
    if delta:
        bar = f"{bar}  {delta}"
    return [f"  {index:02d}  {spaced(display_name(phylum))}", bar]


def bar_line(phylum: str, strong: int, partial: int, total: int, index: int | None = None, delta: str = "") -> str:
    return "\n".join(lane_lines(phylum, strong, partial, total, index, delta))


def _banner_lines(name: str) -> list[str]:
    lines = []
    for piece in render_name(name):
        lines.append(("  " + piece) if piece.strip(" \u200b") else SPACER)
    return lines


def _step_marks(step: int) -> str:
    marks = ["■" if index <= step else "□" for index in range(1, 4)]
    return "  " + " ".join(marks) + f"    {step:02d} / {len(QUESTIONS):02d}"


def opening(step: int = 1, issue: int = 1) -> str:
    del issue
    if step < 1 or step > len(QUESTIONS):
        raise ValueError(step)
    lines = _banner_lines("IDA")
    lines.extend(gap(2))
    if step == 1:
        lines.extend(
            [
                "  When it gets noisy,",
                "  you can always reach for clarity.",
            ]
        )
        lines.extend(gap(2))
    lines.append(_step_marks(step))
    lines.extend(gap(2))
    words = QUESTIONS[step - 1].rstrip("?").split()
    for index, word in enumerate(words):
        if index:
            lines.extend(gap(1))
        lines.extend(_banner_lines(word))
    return _check(lines)


def opening_new() -> str:
    return opening(1)


LANE_TRAINS = {
    "axiom": "reason without fooling yourself",
    "kanon": "weigh evidence and claims",
    "bias": "catch the biases in your own head",
    "persona": "understand what drives others",
    "strategy": "make moves when others move too",
    "systema": "spot second-order consequences",
    "momentum": "choose and follow through",
}
LANE_INTRO = (
    "Lanes are the seven kinds of thinking ida trains. "
    "Each holds ways of thinking from the sharpest minds, turned into scenes from your work and life. "
    "Practice one until it sticks, and you will reach for the right idea when it counts."
)
LANE_ASK = "Which lane do you want to start with?"


def _lightest(rows: list[dict]) -> int:
    ranked = []
    for row in rows:
        index = DISPLAY_ORDER.index(row["phylum"]) + 1
        _cells, percent = bar_cells(int(row["strong"]), int(row["partial"]), int(row["total"]))
        ranked.append((percent, index))
    _low, light_index = min(ranked, key=lambda item: (item[0], item[1]))
    return light_index


def menu_prompt(rows: list[dict] | None = None) -> tuple[str, list[str]]:
    if rows is None:
        rows = [{"phylum": phylum, "strong": 0, "partial": 0, "total": 1} for phylum in DISPLAY_ORDER]
    light = _lightest(rows)
    labels = []
    for row in rows:
        phylum = row["phylum"]
        index = DISPLAY_ORDER.index(phylum) + 1
        strong, partial, total = int(row["strong"]), int(row["partial"]), int(row["total"])
        _cells, percent = bar_cells(strong, partial, total)
        state = "new" if strong <= 0 and partial <= 0 else f"{percent}%"
        if index == light:
            state += ", suggested"
        labels.append(f"{DISPLAY_NAMES[phylum]}: {LANE_TRAINS[phylum]} ({state})")
    labels.extend(
        [
            "daily: one card picked for today",
            "spot: a quick multiple choice",
            "surprise me: ida picks the idea",
        ]
    )
    return f"{LANE_INTRO} {LANE_ASK}", labels


def menu(session: int = 1, rows: list[dict] | None = None, collected: int = 0, total: int = 443, streak: int = 0, typed: bool = False) -> str:
    if rows is None:
        rows = [{"phylum": phylum, "strong": 0, "partial": 0, "total": 1} for phylum in DISPLAY_ORDER]
    light_index = _lightest(rows)
    lines = [
        spread("  ida · practice", f"SESSION {session:02d}"),
        heavy(),
    ]
    lines.extend(gap(2))
    lines.extend("  " + piece for piece in wrap(LANE_INTRO, 72))
    lines.extend(gap(2))
    lines.append("  pick a lane")
    if collected or streak:
        streak_bit = f" · {streak} day streak" if streak else ""
        lines.extend(gap(1))
        lines.append(f"  ■ {collected} of {total} collected{streak_bit}")
    lines.extend(gap(2))
    for index, row in enumerate(rows):
        if index:
            lines.extend(gap(1))
        lines.extend(lane_lines(row["phylum"], int(row["strong"]), int(row["partial"]), int(row["total"])))
    lines.extend(gap(2))
    lines.append(f"  ■ suggested  {light_index:02d}, your lightest lane")
    choices(lines, '  › a number · daily · spot · "surprise me"', typed)
    return _check(lines)


def _card_body(body: str) -> list[str]:
    lines = ["  ┃"]
    paragraphs = [part.strip() for part in body.replace("\r\n", "\n").split("\n\n") if part.strip()]
    if not paragraphs:
        paragraphs = [" ".join(body.split())]
    for paragraph in paragraphs:
        for piece in wrap(paragraph, 68):
            lines.append("  ┃  " + piece)
        lines.append("  ┃")
    lines.append("  ┗" + ("━" * (RULE_WIDTH - 1)))
    return lines


def _blocks(done: int, total: int, cells: int) -> int:
    if cells <= 0 or total <= 0 or done <= 0:
        return 0
    if done >= total:
        return cells
    blocks = int(round(cells * done / total))
    if blocks < 1:
        blocks = 1
    if blocks > cells:
        blocks = cells
    return blocks


def _join_strip(parts: list[str], gap: int) -> str:
    kept = [part for part in parts if part]
    return (" " * gap).join(kept)


def status_strip(
    lane_done: int,
    lane_total: int,
    reached: int,
    session_total: int | None,
    streak: int,
) -> str:
    """One status line, at most 72 columns.

    The bar starts at 16 cells and shortens if a 3-digit count or a long
    session would overflow. Streak is omitted at 0.
    """
    count = f"{lane_done} / {lane_total} ways"
    streak_bit = f"streak {streak}d" if streak >= 1 else ""
    if session_total is not None and session_total >= reached:
        dots = ("●" * reached) + ("○" * (session_total - reached))
    else:
        dots = "●" * reached
    today_bits = [f"today  {dots}" if dots else "today"]
    if session_total is not None and session_total >= reached:
        numeric = f"today  {reached}/{session_total}"
    else:
        numeric = f"today  {reached}"
    for cells in (16, 12, 8, 4):
        filled = _blocks(lane_done, lane_total, cells)
        bar = ("■" * filled) + ("□" * (cells - filled))
        lane_bit = f"lane  {bar}  {count}"
        for today in (today_bits[0], numeric):
            for gap in (6, 4, 2):
                line = _join_strip([lane_bit, today, streak_bit], gap)
                if len(line) <= 72:
                    return line
    line = _join_strip([f"lane  {count}", numeric, streak_bit], 2)
    if len(line) <= 72:
        return line
    return _join_strip([f"lane  {count}", numeric], 2)


def card(
    number: int,
    phylum: str,
    body: str,
    practice: str = "decide",
    mode: str = "free",
    options: list[str] | None = None,
    total: int | None = None,
    signoff_index: int = 0,
    nudge: str = "",
    typed: bool = False,
    status: dict | None = None,
) -> str:
    del signoff_index
    lane = DISPLAY_ORDER.index(phylum) + 1
    card_label = f"CARD {number}" if total is None else f"CARD {number} / {total}"
    lines = [spread(f"  {lane:02d} · {spaced(display_name(phylum))}", card_label), heavy()]
    if status is not None:
        lines.append("  " + status_strip(
            int(status.get("lane_done") or 0),
            int(status.get("lane_total") or 0),
            int(status.get("reached") or number),
            status.get("session_total"),
            int(status.get("streak") or 0),
        ))
        lines.append(heavy())
    lines.extend(gap(2))
    lines.extend(_card_body(body))
    lines.extend(gap(2))
    lines.append("  ■ " + spaced("the question"))
    lines.extend(gap(1))
    free = mode != "choice"
    if practice == "spot" and free:
        question = "What is this called?"
    elif mode == "choice":
        question = "Which one fits?"
    else:
        question = "Which way of thinking fits here? Name it and apply it in a sentence or two."
    for piece in wrap(question, 72):
        lines.append("    " + piece)
    if options:
        lines.extend(gap(1))
        for index, name in enumerate(options, start=1):
            if index > 1:
                lines.extend(gap(1))
            for piece_index, piece in enumerate(wrap(name, 66)):
                prefix = f"    {index}  " if piece_index == 0 else "       "
                lines.append(prefix + piece)
    if nudge.strip():
        lines.extend(gap(2))
        lines.append("  ■ " + spaced("a nudge"))
        lines.extend(gap(1))
        lines.extend(_prose(nudge.strip()))
    if mode == "choice":
        choices(lines, '  › a number · "idk" · "skip"', typed)
    return _check(lines)


def _prose(text: str) -> list[str]:
    return ["  " + piece for piece in wrap(text, 72)]


def _field(label: str, text: str) -> list[str]:
    prefix = "  " + f"{label:<20}" + "  "
    room = SCREEN_WIDTH - len(prefix)
    parts = wrap(text, max(room, 16)) or [""]
    lines = [prefix + parts[0]]
    hang = " " * len(prefix)
    for extra in parts[1:]:
        lines.append(hang + extra)
    return lines


def feedback_strong(
    comment: str,
    reached: str,
    deeper: str,
    phylum: str,
    strong: int,
    partial: int,
    total: int,
    delta: str = "+1",
    typed: bool = False,
) -> str:
    lines = ["  ■■■  " + spaced("strong")]
    lines.extend(gap(1))
    lines.extend(_prose(comment))
    lines.extend(gap(2))
    lines.append(thin())
    lines.extend(gap(1))
    lines.extend(_field("you reached for", spaced(reached)))
    lines.extend(gap(1))
    lines.extend(_field("one level deeper", deeper))
    lines.extend(gap(2))
    lines.append(thin())
    lines.extend(gap(1))
    lines.extend(lane_lines(phylum, strong, partial, total, delta=delta))
    choices(lines, '  › "next" · "why" · "menu"', typed)
    return _check(lines)


def feedback_partial(
    reached: str,
    missing: str,
    try_it: str,
    phylum: str,
    strong: int,
    partial: int,
    total: int,
    delta: str = "+0.5",
    typed: bool = False,
) -> str:
    lines = ["  ■■□  " + spaced("partial")]
    lines.extend(gap(2))
    lines.append(thin())
    lines.extend(gap(1))
    lines.extend(_field("what you got", reached))
    lines.extend(gap(1))
    lines.extend(_field("what was missing", missing))
    lines.extend(gap(1))
    lines.extend(_field("try it", try_it))
    lines.extend(gap(2))
    lines.append(thin())
    lines.extend(gap(1))
    lines.extend(lane_lines(phylum, strong, partial, total, delta=delta))
    choices(lines, '  › "retry" · "next" · "show me"', typed)
    return _check(lines)


def reveal_banner(name: str) -> str:
    """The name, large enough to read, short enough to stay on screen."""
    lines = ["  □□□  not yet. here's what to reach for."]
    lines.extend(gap(2))
    for piece in render_name(name):
        lines.append(("  " + piece) if piece.strip(" \u200b") else SPACER)
    return _check(lines)


def feedback_not_yet(name: str, definition: str = "", typed: bool = False) -> str:
    """Banner, and the library definition when this idea has one.

    The scenario-specific explanation and the three steps are written in
    the reply, under this screen. They are not printed here.
    """
    lines = reveal_banner(name).split("\n")
    if definition.strip():
        lines.extend(gap(2))
        lines.extend(_prose(definition.strip()))
    choices(lines, '  › "got it" · "another like this" · "menu"', typed)
    return _check(lines)


def another_angle(definition: str, analogy: str, scene: str, typed: bool = False) -> str:
    """A fresh pass when they say the reveal did not land."""
    lines = ["  ■ " + spaced("another angle")]
    lines.extend(gap(2))
    lines.extend(_field("one line", definition))
    lines.extend(gap(1))
    lines.extend(_field("everyday", analogy))
    lines.extend(gap(1))
    lines.extend(_field("in this scene", scene))
    choices(lines, '  › "got it" · "another angle" · "next" · "menu"', typed)
    return _check(lines)


def feedback(result: str, name: str, comment, signoff_index: int = 0, phylum: str = "strategy", typed: bool = False) -> str:
    del signoff_index
    text = " ".join(comment) if isinstance(comment, list) else comment
    if result == "strong":
        return feedback_strong(text, name, text, phylum, 1, 0, 81, typed=typed)
    if result == "partial":
        return feedback_partial(name, text, text, phylum, 0, 1, 81, typed=typed)
    return feedback_not_yet(name, text or "", typed=typed)


def summary_block(
    scenarios: int,
    strong: int,
    partial: int,
    miss: int,
    idk: int,
    sharpest: str,
    revisit: str,
    next_line: str,
    unanswered: bool = False,
    signoff_index: int = 0,
    session: int = 1,
    date: str = "12 NOV 2026",
    reached: list[str] | None = None,
    carry: str = "",
    rows: list[dict] | None = None,
    typed: bool = False,
) -> str:
    del revisit
    not_yet = miss + idk
    noun = "card" if scenarios == 1 else "cards"
    lines = [
        spread(f"  ida · session {session:02d} complete", date),
        heavy(),
    ]
    lines.extend(gap(2))
    lines.append(f"  {scenarios} {noun}  ■■■ {strong} strong  ■■□ {partial} partial  □□□ {not_yet} not yet")
    lines.extend(gap(2))
    lines.append("  " + spaced("lanes"))
    lines.extend(gap(1))
    if rows is None:
        rows = [{"phylum": phylum, "strong": 0, "partial": 0, "total": 10} for phylum in DISPLAY_ORDER]
    for index, row in enumerate(rows):
        if index:
            lines.extend(gap(1))
        lines.extend(lane_lines(row["phylum"], int(row["strong"]), int(row["partial"]), int(row["total"])))
    names = reached if reached is not None else ([sharpest] if sharpest else [])
    lines.extend(gap(2))
    lines.append("  " + spaced("what you reached for"))
    lines.extend(gap(1))
    if names:
        for index, name in enumerate(names):
            if index:
                lines.extend(gap(1))
            lines.append("  ■ " + name)
    else:
        lines.append("  ■ nothing yet")
    if carry:
        carry_line = carry
    elif unanswered:
        carry_line = "One card was left open. It was not graded."
    else:
        carry_line = next_line or "Name the idea, then say what it changes here."
    lines.extend(gap(2))
    lines.append("  " + spaced("one to carry"))
    lines.extend(gap(1))
    lines.extend(_prose(carry_line))
    lines.extend(gap(2))
    lines.append(heavy())
    lines.extend(gap(1))
    lines.append("  " + SIGNOFFS[signoff_index % 2])
    choices(lines, '  › "again" · "menu" · "done"', typed)
    return _check(lines)


def bars(rows: list[dict], signoff_index: int = 0) -> str:
    del signoff_index
    lines = ["  " + spaced("lanes")]
    for row in rows:
        lines.extend(
            lane_lines(
                row["phylum"],
                int(row.get("strong", 0)),
                int(row.get("partial", 0)),
                int(row["total"]),
            )
        )
    return _check(lines)
