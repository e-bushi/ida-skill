"""Shared paths and small helpers for the ida skill scripts.

The progress file is a stand-in for a later memory service. These helpers
are the file adapter. Practice code should call the operations in
progress.py, not invent a second writer.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIBRARY = ROOT / "library"
VERSION = 2
RESULTS = ("strong", "partial", "miss", "idk")
MODES = ("free", "choice")
SELECTIONS = ("section", "pick", "random")
RECENT_CAP = 24
RECENT_AVOID = 8
HISTORY_CAP = 40
SUMMARY_LIMIT = 280
PROMPT_LIMIT = 2000

# Page is 76 columns. Rules are 72 characters after a 2-space indent.
SCREEN_WIDTH = 76
RULE_WIDTH = 72
BAR_BLOCKS = 20
# A blank line that is not empty. A space keeps the gap. The zero-width
# space keeps the line when a host drops lines that are only whitespace.
SPACER = " \u200b"

# User-facing section names. Ids stay in the library and the progress file.
DISPLAY_ORDER = (
    "axiom",
    "kanon",
    "bias",
    "persona",
    "strategy",
    "systema",
    "momentum",
)
DISPLAY_NAMES = {
    "axiom": "thinking clearly",
    "kanon": "knowing what's true",
    "bias": "blind spots",
    "persona": "reading people",
    "strategy": "playing to win",
    "systema": "seeing ripple effects",
    "momentum": "deciding and acting",
}

# Locked. They rotate on the end-of-session screen only.
SIGNOFFS = (
    "Clarity is a competitive edge.",
    "The people who see clearly win.",
)


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def progress_path(explicit: str | None = None) -> Path:
    if explicit:
        return Path(explicit).expanduser()
    env = os.environ.get("IDA_PROGRESS")
    if env:
        return Path(env).expanduser()
    return Path.home() / ".ida" / "progress.json"


def die(message: str) -> None:
    raise SystemExit(message)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=".ida-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def plain(text: str, limit: int) -> str:
    """Single-line text for stored summaries. Drops em dashes."""
    cleaned = text.replace("\u2014", ", ").replace("\u2013", "-")
    cleaned = " ".join(cleaned.split())
    return cleaned[:limit]


def plain_prompt(text: str, limit: int) -> str:
    """Scenario body. Keeps paragraph breaks, drops em dashes."""
    cleaned = text.replace("\u2014", ". ").replace("\u2013", "-").replace("\r\n", "\n")
    lines = [" ".join(line.split()) for line in cleaned.split("\n")]
    kept: list[str] = []
    blank = False
    for line in lines:
        if not line:
            if kept and not blank:
                kept.append("")
            blank = True
            continue
        kept.append(line)
        blank = False
    return "\n".join(kept).strip()[:limit]
