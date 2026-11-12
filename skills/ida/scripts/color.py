"""ANSI color for ida screens.

Truecolor is the default when color is on. 256-color is the fallback.
NO_COLOR, IDA_COLOR=plain, and TERM=dumb stay plain. A pipe is plain
unless IDA_COLOR=always, because agent hosts that actually paint ANSI
set that. NO_COLOR still wins.
"""

from __future__ import annotations

import os
import sys

BODY = (0xED, 0xEA, 0xE4)
ACCENT = (0x0A, 0x84, 0xFF)
INK = (0x11, 0x13, 0x16)
DIM = (0x8B, 0x86, 0x80)
AMBER = (0xE0, 0xA1, 0x4A)

# Closest xterm-256 matches.
BODY_256 = 255
ACCENT_256 = 33
DIM_256 = 245
AMBER_256 = 179


def color_mode(stream=None) -> str:
    if os.environ.get("NO_COLOR", "") != "":
        return "plain"
    if os.environ.get("TERM", "") == "dumb":
        return "plain"
    forced = os.environ.get("IDA_COLOR", "").strip().lower()
    if forced in ("plain", "never", "0"):
        return "plain"
    if forced == "256":
        return "256"
    if forced in ("always", "truecolor", "24bit"):
        return "truecolor"
    handle = stream if stream is not None else sys.stdout
    is_tty = False
    try:
        is_tty = bool(handle.isatty())
    except Exception:
        is_tty = False
    if not is_tty:
        return "plain"
    if os.environ.get("COLORTERM", "") in ("truecolor", "24bit"):
        return "truecolor"
    return "256"


def _fg(rgb: tuple[int, int, int], mode: str) -> str:
    if mode == "plain":
        return ""
    if mode == "256":
        table = {BODY: BODY_256, ACCENT: ACCENT_256, DIM: DIM_256, AMBER: AMBER_256}
        return f"\033[38;5;{table[rgb]}m"
    r, g, b = rgb
    return f"\033[38;2;{r};{g};{b}m"


def _bg(mode: str) -> str:
    if mode != "truecolor":
        return ""
    r, g, b = INK
    return f"\033[48;2;{r};{g};{b}m"


RESET = "\033[0m"


def paint(text: str, mode: str) -> str:
    if mode == "plain" or not text:
        return text
    body = _fg(BODY, mode)
    accent = _fg(ACCENT, mode)
    dim = _fg(DIM, mode)
    amber = _fg(AMBER, mode)
    out = []
    for line in text.split("\n"):
        if line == "":
            out.append("")
            continue
        if set(line) <= {" ", "\u200b"}:
            out.append(dim + line + RESET)
            continue
        stripped = line.lstrip()
        if set(line.strip()) and set(line.strip()) <= {"█", "░", " "}:
            out.append(_paint_banner(line, mode))
            continue
        if any(ch in line for ch in "█▒░"):
            out.append(_paint_bar(line, mode))
            continue
        if stripped.startswith("■■■"):
            out.append(accent + line + RESET)
            continue
        if stripped.startswith("■■□"):
            out.append(amber + line + RESET)
            continue
        if stripped.startswith("□□□"):
            out.append(dim + line + RESET)
            continue
        if stripped.startswith(("━", "─", "›", "ida", "type your answer")) or stripped.startswith("ida "):
            out.append(dim + line + RESET)
            continue
        if "■" in line:
            painted = []
            for ch in line:
                if ch == "■":
                    painted.append(accent + ch + body)
                else:
                    painted.append(ch)
            out.append(body + "".join(painted) + RESET)
            continue
        out.append(body + line + RESET)
    return "\n".join(out)


def _paint_bar(line: str, mode: str) -> str:
    accent = _fg(ACCENT, mode)
    dim = _fg(DIM, mode)
    amber = _fg(AMBER, mode)
    body = _fg(BODY, mode)
    parts = [body]
    for ch in line:
        if ch == "█":
            parts.append(accent + ch + body)
        elif ch == "▒":
            parts.append(amber + ch + body)
        elif ch == "░":
            parts.append(dim + ch + body)
        else:
            parts.append(ch)
    return "".join(parts) + RESET


def _paint_banner(line: str, mode: str) -> str:
    accent = _fg(ACCENT, mode)
    dim = _fg(DIM, mode)
    bg = _bg(mode)
    parts = []
    for ch in line:
        if ch == "█":
            parts.append(bg + accent + ch)
        elif ch == "░":
            parts.append(bg + dim + ch)
        elif ch == " ":
            parts.append(bg + " ")
        else:
            parts.append(_fg(BODY, mode) + ch)
    return "".join(parts) + RESET
