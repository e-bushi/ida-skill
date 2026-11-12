"""Render ida cards, bars, and the session summary at a fixed width.

The chat should print this output as-is. Padding is spaces, never tabs.
Every line of a card is CARD_WIDTH characters. Bar rows share one width.
"""

from __future__ import annotations

import argparse
import json
import sys

from common import (
    BAR_BLOCKS,
    BAR_LABEL_WIDTH,
    CARD_WIDTH,
    INNER_WIDTH,
    LIBRARY,
    PHYLUM_WIDTH,
    SUBTITLE_WIDTH,
    read_json,
)

WORDMARK = "\n".join(
    [
        "  █  █▀▄  ▄▀█",
        "  █  █▄▀  █▀█",
        "  reach for clarity",
    ]
)

MENU = "  Practice: [1] a section  [2] pick ideas  [3] random"

INTRO = "\n".join(
    [
        "  When it gets noisy, you can always reach for clarity.",
        "  The best ideas from the sharpest minds,",
        "  ready when a decision gets hard.",
        "",
        "  01 Collect the best ideas.",
        "  02 Connect them as you go.",
        "  03 Reach for them when it counts.",
        "",
        "  Before the first scenario, three quick questions.",
        "  A sentence each is enough.",
        "",
        "  1. What do you do for work?",
        "  2. What are you into besides that?",
        "  3. What decisions keep showing up for you?",
    ]
)

FOOTERS = {
    ("decide", "free"): [
        "Which way of thinking fits here?",
        "Name it and apply it in a sentence or two.",
        'Type "idk" anytime.',
    ],
    ("spot", "free"): [
        "What is this called?",
        "The name is enough. Add a few words if you want.",
        'Type "idk" anytime.',
    ],
    ("decide", "choice"): [
        "Which one fits? A number is enough.",
        "Add a sentence if you want.",
        'Type "idk" anytime.',
    ],
    ("spot", "choice"): [
        "Which name fits? A number is enough.",
        'Type "idk" anytime.',
    ],
}


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


def split_paragraphs(text: str) -> list[str]:
    chunks = []
    for part in text.replace("\r\n", "\n").split("\n\n"):
        line = " ".join(part.split())
        if line:
            chunks.append(line)
    return chunks


def frame(content: str, width: int = INNER_WIDTH) -> str:
    if len(content) > width:
        raise ValueError(f"card line is {len(content)} chars, inner width is {width}")
    return "│ " + content.ljust(width) + " │"


def top_border(number: int, phylum: str, practice: str, width: int = CARD_WIDTH) -> str:
    shown = f"{number:02d}" if number < 100 else str(number)
    left = f"┌─ scenario {shown} "
    tag = phylum if practice != "spot" else f"{phylum} / spot"
    right = f" {tag} ─┐"
    dashes = width - len(left) - len(right)
    if dashes < 2:
        right = f" {phylum} ─┐"
        dashes = width - len(left) - len(right)
    if dashes < 2:
        raise ValueError(f"title does not fit: scenario {shown} {tag}")
    line = left + ("─" * dashes) + right
    if len(line) != width:
        raise ValueError(f"top border is {len(line)} not {width}")
    return line


def bottom_border(width: int = CARD_WIDTH) -> str:
    return "└" + ("─" * (width - 2)) + "┘"


def card(
    number: int,
    phylum: str,
    practice: str,
    body: str,
    mode: str = "free",
    options: list[str] | None = None,
) -> str:
    if practice not in ("decide", "spot"):
        raise ValueError(practice)
    if mode not in ("free", "choice"):
        raise ValueError(mode)
    inner: list[str] = []
    for paragraph in split_paragraphs(body):
        inner.extend(wrap(paragraph, INNER_WIDTH))
        inner.append("")
    if options:
        while inner and inner[-1] == "":
            inner.pop()
        inner.append("")
        for index, name in enumerate(options, start=1):
            prefix = f"{index}  "
            if index > 9:
                raise ValueError("cards hold at most 9 options")
            chunks = wrap(name, INNER_WIDTH - len(prefix))
            inner.append(prefix + chunks[0])
            for extra in chunks[1:]:
                inner.append((" " * len(prefix)) + extra)
        inner.append("")
    while inner and inner[-1] == "":
        inner.pop()
    if not inner:
        raise ValueError("scenario body is empty")
    inner.append("")
    for line in FOOTERS[(practice, mode)]:
        inner.extend(wrap(line, INNER_WIDTH))
    collapsed: list[str] = []
    for line in inner:
        if line == "" and collapsed and collapsed[-1] == "":
            continue
        collapsed.append(line)
    lines = [top_border(number, phylum, practice)]
    lines.extend(frame(line) for line in collapsed)
    lines.append(bottom_border())
    for line in lines:
        if len(line) != CARD_WIDTH:
            raise ValueError(f"card line width {len(line)}: {line!r}")
    return "\n".join(lines)


def blocks(well: int, total: int) -> str:
    if total <= 0 or well <= 0:
        filled = 0
    else:
        filled = (well * BAR_BLOCKS + total // 2) // total
        if filled < 1:
            filled = 1
        if well >= total:
            filled = BAR_BLOCKS
    filled = max(0, min(BAR_BLOCKS, filled))
    return ("█" * filled) + ("░" * (BAR_BLOCKS - filled))


def phylum_label(phylum: str, subtitle: str) -> str:
    return f"{phylum.ljust(PHYLUM_WIDTH)}  {subtitle.ljust(SUBTITLE_WIDTH)}"


def bar_line(label: str, well: int, total: int) -> str:
    if len(label) > BAR_LABEL_WIDTH:
        label = label[:BAR_LABEL_WIDTH]
    left = label.ljust(BAR_LABEL_WIDTH)
    count = f"{well}/{total}".rjust(7)
    return f"{left}  {blocks(well, total)}  {count}"


def render_bars(items: list[dict]) -> str:
    lines = []
    for item in items:
        if "phylum" in item:
            label = phylum_label(item["phylum"], item["subtitle"])
        else:
            label = item["label"]
        lines.append(bar_line(label, int(item["well"]), int(item["total"])))
    width = len(lines[0]) if lines else 0
    for line in lines:
        if len(line) != width:
            raise ValueError("bar rows are not the same width")
    return "\n".join(lines)


def feedback(result: str, name: str, comments: list[str]) -> str:
    marks = {"strong": "✓", "partial": "~", "miss": "✗", "idk": "?"}
    if result not in marks:
        raise ValueError(result)
    if result == "idk":
        head = f"? {name}."
    else:
        tail = {"strong": "strong pick.", "partial": "partial.", "miss": "miss."}[result]
        head = f"{marks[result]} {name}: {tail}"
    body = " ".join(part.strip() for part in comments if part.strip())
    body = body.replace("\u2014", ". ").replace("\u2013", "-")
    lines = wrap(head, CARD_WIDTH)
    for line in wrap(body, CARD_WIDTH - 2):
        lines.append("  " + line)
    for line in lines:
        if len(line) > CARD_WIDTH:
            raise ValueError(f"feedback line is {len(line)} chars")
    return "\n".join(lines)


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
) -> str:
    if scenarios == 0:
        lines = ["No scenarios this time."]
    else:
        noun = "scenario" if scenarios == 1 else "scenarios"
        bits = [f"{strong} strong"]
        if partial:
            bits.append(f"{partial} partial")
        if miss:
            bits.append(f"{miss} miss")
        if idk:
            bits.append(f"{idk} idk")
        grade = " · ".join(bits)
        one_line = f"{scenarios} {noun} · {grade}"
        lines = [one_line] if len(one_line) <= CARD_WIDTH else [f"{scenarios} {noun}", grade]
    if unanswered:
        lines.append("Left the last scenario unanswered.")
    lines.append(f"Sharpest: {sharpest or 'none yet'}")
    lines.append(f"Revisit: {revisit or 'nothing due'}")
    lines.append(f"Next time: {next_line}")
    wrapped: list[str] = []
    for line in lines:
        wrapped.extend(wrap(line, CARD_WIDTH))
    top = "── session "
    top = top + ("─" * (CARD_WIDTH - len(top)))
    bottom = "─" * CARD_WIDTH
    output = [top, *wrapped, bottom]
    for line in (top, bottom):
        if len(line) != CARD_WIDTH:
            raise ValueError("summary rule width drifted")
    for line in wrapped:
        if len(line) > CARD_WIDTH:
            raise ValueError("summary line is wider than the card")
    return "\n".join(output)


def opening(kind: str, line: str = "") -> str:
    parts = [WORDMARK, ""]
    if kind == "new":
        parts.append(INTRO)
    elif kind == "ready":
        parts.append('  You can say "update my profile" anytime.')
        parts.append("")
        parts.append(MENU)
    elif kind in ("returning", "resume"):
        text = line.strip() or "Good to see you."
        parts.append(f"  Welcome back. {text}")
        parts.append("")
        if kind == "resume":
            parts.append("  Continue that one, or start fresh.")
            parts.append("")
        parts.append(MENU)
    else:
        raise ValueError(kind)
    return "\n".join(parts)


def sections() -> str:
    doc = read_json(LIBRARY / "phyla.json")
    lines = ["  All sections are open.", ""]
    for index, phylum in enumerate(doc["phyla"], start=1):
        lines.append(f"  {index}  {phylum['id'].ljust(PHYLUM_WIDTH)}  {phylum['subtitle']}")
    lines.append("")
    lines.append("  A category inside one of these is fine.")
    return "\n".join(lines)


def self_check() -> None:
    doc = read_json(LIBRARY / "phyla.json")
    for phylum in doc["phyla"]:
        for practice in ("decide", "spot"):
            card(4, phylum["id"], practice, "A short scene with a real stake.")
    card(
        4,
        "strategy",
        "decide",
        "Your biggest customer asks for a custom feature only they would use. They pay 40% of your revenue.",
        mode="choice",
        options=[
            "inversion",
            "second-order thinking",
            "sunk cost fallacy",
            "commutative / associative / distributive laws",
        ],
    )
    opening("new")
    opening("resume", "Last time: strategy, scenario 3.")
    sections()
    print("ok")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render ida text blocks.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    open_cmd = sub.add_parser("opening")
    open_cmd.add_argument("--kind", required=True, choices=("new", "ready", "returning", "resume"))
    open_cmd.add_argument("--line", default="")

    sub.add_parser("sections")
    sub.add_parser("self-check")

    card_cmd = sub.add_parser("card")
    card_cmd.add_argument("--number", type=int, required=True)
    card_cmd.add_argument("--phylum", required=True)
    card_cmd.add_argument("--practice", required=True, choices=("decide", "spot"))
    card_cmd.add_argument("--mode", default="free", choices=("free", "choice"))
    card_cmd.add_argument("--option", action="append", default=[])
    card_cmd.add_argument("--body", default="")

    feed = sub.add_parser("feedback")
    feed.add_argument("--result", required=True, choices=("strong", "partial", "miss", "idk"))
    feed.add_argument("--name", required=True)
    feed.add_argument("--comment", action="append", default=[])

    bars_cmd = sub.add_parser("bars")
    summ = sub.add_parser("summary")
    summ.add_argument("--scenarios", type=int, required=True)
    summ.add_argument("--strong", type=int, default=0)
    summ.add_argument("--partial", type=int, default=0)
    summ.add_argument("--miss", type=int, default=0)
    summ.add_argument("--idk", type=int, default=0)
    summ.add_argument("--sharpest", default="")
    summ.add_argument("--revisit", default="")
    summ.add_argument("--next", required=True)
    summ.add_argument("--unanswered", action="store_true")

    args = parser.parse_args()
    if args.cmd == "opening":
        print(opening(args.kind, args.line))
    elif args.cmd == "sections":
        print(sections())
    elif args.cmd == "self-check":
        self_check()
    elif args.cmd == "card":
        body = args.body or sys.stdin.read()
        print(card(args.number, args.phylum, args.practice, body, args.mode, args.option or None))
    elif args.cmd == "feedback":
        print(feedback(args.result, args.name, args.comment))
    elif args.cmd == "bars":
        print(render_bars(json.loads(sys.stdin.read())))
    elif args.cmd == "summary":
        print(
            summary_block(
                args.scenarios,
                args.strong,
                args.partial,
                args.miss,
                args.idk,
                args.sharpest,
                args.revisit,
                args.next,
                args.unanswered,
            )
        )


if __name__ == "__main__":
    main()
