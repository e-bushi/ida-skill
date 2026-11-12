"""Terminal screens for ida.

The sheet is 54 columns. Rules, the card rail, and the prompt match the
reference layouts. These functions check the templates. During a sitting
the agent draws the same screens from references/format.md.
"""

from __future__ import annotations

from common import BAR_BLOCKS, DISPLAY_NAMES, DISPLAY_ORDER, SCREEN_WIDTH, SIGNOFFS

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


def rule(char: str) -> str:
    return "  " + (char * (SCREEN_WIDTH - 2))


def heavy() -> str:
    return rule("━")


def thin() -> str:
    return rule("─")


def bar_cells(strong: int, partial: int, total: int) -> tuple[str, int]:
    """10 cells for the share of a section.

    A strong idea counts as 1. A partial idea counts as half. idk and miss
    add nothing. The caller passes partial ideas that are not already strong.

    Each cell is a tenth of the section. Full tenths are █. A remainder
    shows as ▒, including the first bit of credit so one rep is visible
    without claiming a full tenth. The rest are ░. The percent is
    round(100 * credit / total).
    """
    if total <= 0 or (strong <= 0 and partial <= 0):
        return "░" * BAR_BLOCKS, 0
    credit = strong + 0.5 * partial
    if credit > total:
        credit = float(total)
    percent = int(round(100 * credit / total))
    percent = max(0, min(100, percent))
    exact = BAR_BLOCKS * credit / total
    full = int(exact)
    if full > BAR_BLOCKS:
        full = BAR_BLOCKS
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


def bar_line(phylum: str, strong: int, partial: int, total: int, index: int | None = None) -> str:
    if index is None:
        index = DISPLAY_ORDER.index(phylum) + 1
    cells, percent = bar_cells(strong, partial, total)
    name = display_name(phylum).ljust(22)
    score = score_field(strong, partial, percent)
    return f"  {index:02d}   {name}  {cells}  {score}"


def opening(step: int = 1, issue: int = 1) -> str:
    if step < 1 or step > len(QUESTIONS):
        raise ValueError(step)
    lines = [
        spread("  ida", f"NO. {issue:03d}"),
        heavy(),
        "",
    ]
    if step == 1:
        lines.extend(
            [
                "  When it gets noisy,",
                "  you can always reach for clarity.",
                "",
                "",
                "  ■ first session · 3 quick questions · about a minute",
                "",
            ]
        )
    lines.extend(
        [
            thin(),
            spread(f"  {step:02d} / {len(QUESTIONS):02d}", QUESTIONS[step - 1].upper().rstrip("?")),
            "",
            "  › your own words",
        ]
    )
    return _check(lines)


def opening_new() -> str:
    return opening(1)


def menu(session: int = 1, rows: list[dict] | None = None) -> str:
    if rows is None:
        rows = [{"phylum": phylum, "strong": 0, "partial": 0, "total": 1} for phylum in DISPLAY_ORDER]
    ranked = []
    for row in rows:
        index = DISPLAY_ORDER.index(row["phylum"]) + 1
        _cells, percent = bar_cells(int(row["strong"]), int(row["partial"]), int(row["total"]))
        ranked.append((percent, index))
    _light_percent, light_index = min(ranked, key=lambda item: (item[0], item[1]))
    lines = [
        spread("  ida · practice", f"SESSION {session:02d}"),
        thin(),
        "",
        "  pick a lane",
        "",
        "",
    ]
    for row in rows:
        lines.append(bar_line(row["phylum"], int(row["strong"]), int(row["partial"]), int(row["total"])))
    lines.extend(
        [
            "",
            "",
            f"  ■ suggested  {light_index:02d}, your lightest lane",
            "",
            '  › a number, or "surprise me"',
        ]
    )
    return _check(lines)


def _card_body(body: str) -> list[str]:
    lines = ["  ┃"]
    paragraphs = [part.strip() for part in body.replace("\r\n", "\n").split("\n\n") if part.strip()]
    if not paragraphs:
        paragraphs = [" ".join(body.split())]
    for paragraph in paragraphs:
        for piece in wrap(paragraph, 46):
            lines.append("  ┃  " + piece)
        lines.append("  ┃")
    lines.append("  ┗" + ("━" * (SCREEN_WIDTH - 3)))
    return lines


def card(
    number: int,
    phylum: str,
    body: str,
    practice: str = "decide",
    mode: str = "free",
    options: list[str] | None = None,
    signoff_index: int = 0,
) -> str:
    del signoff_index  # sign-offs belong on the session end only
    title = display_name(phylum).upper()
    lane = DISPLAY_ORDER.index(phylum) + 1
    lines = [spread(f"  {lane:02d} · {title}", f"CARD {number:02d}")]
    lines.extend(_card_body(body))
    lines.extend(["", "  ■ THE QUESTION", ""])
    if practice == "spot":
        question = "What is this called?"
    elif mode == "choice":
        question = "Which one fits?"
    else:
        question = "Which way of thinking fits here? Name it and apply it in a sentence or two."
    for piece in wrap(question, SCREEN_WIDTH - 4):
        lines.append("    " + piece)
    if options:
        lines.append("")
        for index, name in enumerate(options, start=1):
            lines.append(f"    {index}  {name}")
    lines.extend(["", ""])
    if mode == "choice":
        lines.append('  › a number · "idk" · "skip"')
    elif practice == "spot":
        lines.append('  › the name · "idk" · "skip"')
    else:
        lines.append('  › your answer · "hint" · "idk" · "skip"')
    return _check(lines)


def _prose(text: str) -> list[str]:
    return ["  " + piece for piece in wrap(text, SCREEN_WIDTH - 2)]


def _field(label: str, text: str) -> list[str]:
    prefix = "  " + f"{label:<20}" + "    "
    room = SCREEN_WIDTH - len(prefix)
    parts = wrap(text, room) or [""]
    lines = [prefix + parts[0]]
    hang = " " * len(prefix)
    for extra in parts[1:]:
        lines.append(hang + extra)
    return lines


def _status(phylum: str, strong: int, partial: int, total: int, delta: str) -> str:
    base = bar_line(phylum, strong, partial, total)
    if not delta:
        return base
    return base + "   " + delta


def feedback_strong(
    comment: str,
    reached: str,
    deeper: str,
    phylum: str,
    strong: int,
    partial: int,
    total: int,
    delta: str = "+1",
) -> str:
    lines = ["  ■■■  STRONG", thin(), ""]
    lines.extend(_prose(comment))
    lines.append("")
    lines.extend(_field("what you reached for", reached))
    lines.extend(_field("one level deeper", deeper))
    lines.extend(["", _status(phylum, strong, partial, total, delta), "", '  › "next" · "why" · "menu"'])
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
) -> str:
    lines = ["  ■■□  PARTIAL", thin(), ""]
    lines.extend(_field("what you reached for", reached))
    lines.extend(_field("what was missing", missing))
    lines.extend(_field("try it", try_it))
    lines.extend(["", _status(phylum, strong, partial, total, delta), "", '  › "retry" · "next" · "show me"'])
    return _check(lines)


def _step(index: int, title: str, detail: str) -> list[str]:
    prefix = f"  {index:02d}  {title}".ljust(30)
    room = SCREEN_WIDTH - len(prefix)
    parts = wrap(detail, max(room, 12)) or [""]
    lines = [prefix + parts[0]]
    hang = " " * len(prefix)
    for extra in parts[1:]:
        lines.append(hang + extra)
    return lines


def feedback_not_yet(lead: str, steps: list[tuple[str, str]], closing: str) -> str:
    lines = ["  □□□  NOT YET", thin(), ""]
    lines.extend(_prose(lead))
    lines.append("")
    for index, (title, detail) in enumerate(steps, start=1):
        lines.extend(_step(index, title, detail))
    lines.extend(["", *_prose(closing), "", '  › "got it" · "another like this" · "menu"'])
    return _check(lines)


def feedback(result: str, name: str, comment, signoff_index: int = 0, phylum: str = "strategy") -> str:
    """A short form used when a caller only has a grade and a comment."""
    del signoff_index
    text = " ".join(comment) if isinstance(comment, list) else comment
    if result == "strong":
        return feedback_strong(text, name, text, phylum, 1, 0, 81)
    if result == "partial":
        return feedback_partial(name, text, text, phylum, 0, 1, 81)
    return feedback_not_yet(
        "Saying so is the honest start. Here's one way in.",
        [("name it", name), ("apply it", text), ("keep it", "one sentence on the stake")],
        text,
    )


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
) -> str:
    not_yet = miss + idk
    noun = "card" if scenarios == 1 else "cards"
    lines = [
        spread(f"  ida · session {session:02d} complete", date),
        heavy(),
        "",
        f"  {scenarios} {noun}     ■■■ {strong}     ■■□ {partial}     □□□ {not_yet}",
        "",
        "",
        "  LANES",
    ]
    if rows is None:
        rows = [{"phylum": phylum, "strong": 0, "partial": 0, "total": 10} for phylum in DISPLAY_ORDER]
    for row in rows:
        lines.append(bar_line(row["phylum"], int(row["strong"]), int(row["partial"]), int(row["total"])))
    names = reached or ([sharpest] if sharpest else [])
    lines.extend(["", "", "  WHAT YOU REACHED FOR"])
    if names:
        lines.append("  · " + "   · ".join(names))
    else:
        lines.append("  · nothing yet")
    if carry:
        carry_line = carry
    elif unanswered:
        carry_line = "One card was left open. It was not graded."
    else:
        carry_line = next_line or "Name the idea, then say what it changes here."
    del revisit
    lines.extend(["", "", "  ONE TO CARRY"])
    lines.extend(_prose(carry_line))
    lines.extend(
        [
            "",
            "",
            thin(),
            "  " + SIGNOFFS[signoff_index % 2],
            "",
            '  › "again" · "menu" · "done"',
        ]
    )
    return _check(lines)


def bars(rows: list[dict], signoff_index: int = 0) -> str:
    del signoff_index
    lines = ["  LANES"]
    for row in rows:
        lines.append(
            bar_line(
                row["phylum"],
                int(row.get("strong", 0)),
                int(row.get("partial", 0)),
                int(row["total"]),
            )
        )
    return _check(lines)
