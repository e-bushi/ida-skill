"""Terminal screens for ida.

Every screen is at most 56 columns, with a left rail and no right border.
The only accent is ■. Labels are in caps. A › line ends every screen.
These functions are for tests and for checking the templates. During a
sitting the agent draws the same screens from references/format.md and
does not shell out to this file.
"""

from __future__ import annotations

from common import (
    BAR_BLOCKS,
    CONTENT_WIDTH,
    DISPLAY_NAMES,
    DISPLAY_ORDER,
    RAIL,
    SCREEN_WIDTH,
    SIGNOFFS,
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


def _finish(content_lines: list[str], signoff_index: int | None) -> str:
    lines: list[str] = []
    for line in content_lines:
        if line == "":
            lines.append("")
            continue
        if len(line) <= CONTENT_WIDTH:
            lines.append(RAIL + line)
            continue
        for part in wrap(line, CONTENT_WIDTH):
            lines.append(RAIL + part)
    if signoff_index is not None:
        lines.append("")
        for part in wrap(SIGNOFFS[signoff_index % 2], CONTENT_WIDTH):
            lines.append(RAIL + part)
    lines.append("")
    lines.append(RAIL + "›")
    for line in lines:
        if len(line) > SCREEN_WIDTH:
            raise ValueError(f"line is {len(line)} cols: {line!r}")
    return "\n".join(lines)


def bar_cells(strong: int, partial: int, total: int) -> tuple[str, int]:
    """10 cells for the share of a section.

    A strong idea counts as 1. A partial idea counts as half. idk and miss
    add nothing. The caller passes partial ideas that are not already strong.

    Each cell is a tenth of the section. Full tenths are █. A remainder
    shows as ▒, including the first bit of credit so one rep is visible
    without claiming a full tenth. The rest are ░. The percent is the
    honest score: round(100 * credit / total).
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


def bar_line(phylum: str, strong: int, partial: int, total: int) -> str:
    label = display_name(phylum).upper().ljust(21)
    cells, percent = bar_cells(strong, partial, total)
    score = f"{percent}%".rjust(4)
    line = f"{label}  {cells}  {score}"
    if len(line) > CONTENT_WIDTH:
        raise ValueError(f"bar line is {len(line)} cols")
    return line


def opening_new() -> str:
    return _finish(
        [
            "■ ida",
            "",
            SIGNOFFS[0],
            "",
            "01",
            "What do you do for work?",
            "",
            "02",
            "What are you into besides that?",
            "",
            "03",
            "What decisions keep showing up for you?",
        ],
        None,
    )


def menu(welcome: str = "", signoff_index: int = 1) -> str:
    lines = ["■ ida", ""]
    if welcome:
        lines.extend(["WELCOME BACK", welcome, ""])
    lines.append("PRACTICE")
    for index, phylum in enumerate(DISPLAY_ORDER, start=1):
        lines.append(f"{index}  {display_name(phylum).upper()}")
    lines.extend(["", "Or name the ideas. Or say random."])
    return _finish(lines, signoff_index)


def resume(welcome: str, signoff_index: int = 1) -> str:
    return _finish(
        [
            "■ ida",
            "",
            "WELCOME BACK",
            welcome,
            "",
            "Continue that one, or start fresh.",
        ],
        signoff_index,
    )


def card(
    number: int,
    phylum: str,
    body: str,
    practice: str = "decide",
    mode: str = "free",
    options: list[str] | None = None,
    signoff_index: int = 0,
) -> str:
    lines = [f"SCENARIO {number:02d}", display_name(phylum).upper()]
    if practice == "spot":
        lines.append("SPOT")
    lines.extend(["", body, ""])
    if options:
        for index, name in enumerate(options, start=1):
            lines.append(f"{index}  {name}")
        lines.append("")
    if practice == "spot" and mode == "choice":
        lines.append("Which name fits? A number is enough. idk is fine.")
    elif practice == "spot":
        lines.append("What is this called? The name is enough. idk is fine.")
    elif mode == "choice":
        lines.append("Which one fits? A number is enough. idk is fine.")
    else:
        lines.append("Which way of thinking fits here? Name it and apply it in a sentence or two. idk is fine.")
    return _finish(lines, signoff_index)


def feedback(result: str, name: str, comment, signoff_index: int = 0) -> str:
    heads = {"strong": "STRONG", "partial": "PARTIAL", "miss": "MISS", "idk": "IDK"}
    if result not in heads:
        raise ValueError(result)
    if isinstance(comment, list):
        comment = " ".join(part.strip() for part in comment if part.strip())
    return _finish([heads[result], name, "", comment], signoff_index)


def bars(rows: list[dict], signoff_index: int = 0) -> str:
    lines = ["PROGRESS", ""]
    rendered = [
        bar_line(row["phylum"], int(row["strong"]), int(row["partial"]), int(row["total"]))
        for row in rows
    ]
    width = len(rendered[0]) if rendered else 0
    for line in rendered:
        if len(line) != width:
            raise ValueError("bar rows are not the same width")
        lines.append(line)
    return _finish(lines, signoff_index)


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
) -> str:
    lines = ["SESSION", ""]
    if scenarios == 0:
        lines.append("No scenarios this time.")
    else:
        noun = "scenario" if scenarios == 1 else "scenarios"
        bits = [f"{strong} strong"]
        if partial:
            bits.append(f"{partial} partial")
        if miss:
            bits.append(f"{miss} miss")
        if idk:
            bits.append(f"{idk} idk")
        lines.append(f"{scenarios} {noun}")
        lines.append(" · ".join(bits))
    if unanswered:
        lines.append("Left the last scenario unanswered.")
    lines.extend(
        [
            "",
            "SHARPEST",
            sharpest or "none yet",
            "",
            "REVISIT",
            revisit or "nothing due",
            "",
            "NEXT",
            next_line,
        ]
    )
    return _finish(lines, signoff_index)


def section_rows(order=DISPLAY_ORDER) -> list[dict]:
    return [{"phylum": phylum, "strong": 0, "partial": 0, "total": 1} for phylum in order]
