"""Regenerate the lean library from library/ida-library.csv.

Edits to wording for the 436 unauthored entries do not belong here.
Only the seven rows with a law or notes are stored in full, as voice
exemplars. Everything else becomes an index row: id, name, category,
practice, number.

Run from anywhere:

    python3 skills/ida/scripts/build_library.py
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

from common import LIBRARY

# Whole categories that are vocabulary: name the thing, don't stage a life decision.
SPOT_CATEGORIES = {
    ("axiom", "statement properties"),
    ("axiom", "logical operators"),
    ("axiom", "quantifiers"),
    ("axiom", "laws of logic"),
    ("axiom", "proof techniques"),
    ("axiom", "categorical (aristotelian) logic"),
    ("axiom", "logical paradoxes"),
}

# Single entries inside otherwise practical categories.
SPOT_IDS = {
    "ad-hoc-hypothesis",
    "non-sequitur",
    "premise-conclusion",
    "prima-facie",
    "a-priori-vs-a-posteriori",
    "analytic-vs-synthetic",
    "necessity-vs-possibility",
    "usemention-distinction",
    "null-hypothesis",
    "p-value",
    "confidence-interval",
    "error-bars",
    "statistical-significance",
    "power",
    "central-limit-theorem",
}

AUTHORED_ORDER = [
    "survivorship-bias",
    "schelling-point",
    "goodharts-law",
    "mimetic-desire",
    "inversion",
    "via-negativa",
    "gell-mann-amnesia",
]


def practice_for(row: dict) -> str:
    if row["id"] in SPOT_IDS:
        return "spot"
    if (row["phylum"], row["category"]) in SPOT_CATEGORIES:
        return "spot"
    return "decide"


def clean_prose(text: str) -> str:
    """Drop em dashes from authored prose so the voice file does not teach them.

    'and' / 'then' keep a comma. Anything else starts a new sentence.
    The stored voice stays lowercase, matching the source lines.
    """
    raw = " ".join(text.split())
    if "\u2014" not in raw and "\u2013" not in raw:
        return raw
    parts = [part.strip() for part in re.split(r"\s*[\u2014\u2013]\s*", raw) if part.strip()]
    out = parts[0]
    for part in parts[1:]:
        if part.lower().startswith(("and ", "then ")):
            out = out.rstrip() + ", " + part
        elif out.endswith("."):
            out = out + " " + part
        else:
            out = out.rstrip() + ". " + part
    return " ".join(out.split())


def clean_attribution(raw: str, year: str) -> str:
    text = raw.strip().lstrip("\u2014\u2013- ").strip()
    if year and text.endswith(year):
        text = text[: -len(year)].rstrip(" ,")
    return text


def dump(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build(csv_path: Path, out_dir: Path) -> dict:
    with csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    ids = [row["id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate ids in the csv")

    phylum_order: list[str] = []
    subtitles: dict[str, str] = {}
    for row in rows:
        if row["phylum"] not in subtitles:
            phylum_order.append(row["phylum"])
            subtitles[row["phylum"]] = row["phylum_subtitle"]

    by_phylum: OrderedDict[str, list[dict]] = OrderedDict((pid, []) for pid in phylum_order)
    authored: dict[str, dict] = {}
    for row in rows:
        practice = practice_for(row)
        entry = {
            "id": row["id"],
            "name": row["name"],
            "category": row["category"],
            "practice": practice,
            "n": int(row["entry_number"]),
        }
        by_phylum[row["phylum"]].append(entry)
        if row["law"].strip() or row["notes"].strip():
            year = row["discovered_year"].strip()
            authored[row["id"]] = {
                "id": row["id"],
                "name": row["name"],
                "phylum": row["phylum"],
                "subtitle": row["phylum_subtitle"],
                "category": row["category"],
                "practice": practice,
                "law": clean_prose(row["law"]),
                "notes": clean_prose(row["notes"]),
                "attribution": clean_attribution(row["attribution"], year),
                "year": int(year) if year else None,
            }

    missing = [eid for eid in AUTHORED_ORDER if eid not in authored]
    extra = [eid for eid in authored if eid not in AUTHORED_ORDER]
    if missing or extra:
        raise SystemExit(f"authored set changed. missing={missing} extra={extra}")

    phyla = []
    for pid in phylum_order:
        entries = sorted(by_phylum[pid], key=lambda item: item["n"])
        numbers = [item["n"] for item in entries]
        if numbers != list(range(1, len(entries) + 1)):
            raise SystemExit(f"{pid} entry numbers are not 1..{len(entries)}")
        categories: list[dict] = []
        seen: dict[str, dict] = {}
        for item in entries:
            bucket = seen.get(item["category"])
            if bucket is None:
                bucket = {"name": item["category"], "count": 0, "spot": 0, "decide": 0}
                seen[item["category"]] = bucket
                categories.append(bucket)
            bucket["count"] += 1
            bucket[item["practice"]] += 1
        for bucket in categories:
            if bucket["spot"] and bucket["decide"]:
                bucket["practice"] = "mixed"
            elif bucket["spot"]:
                bucket["practice"] = "spot"
            else:
                bucket["practice"] = "decide"
            del bucket["spot"]
            del bucket["decide"]
        phyla.append(
            {
                "id": pid,
                "subtitle": subtitles[pid],
                "count": len(entries),
                "decide": sum(1 for item in entries if item["practice"] == "decide"),
                "spot": sum(1 for item in entries if item["practice"] == "spot"),
                "categories": categories,
            }
        )
        dump(
            out_dir / "index" / f"{pid}.json",
            {"phylum": pid, "subtitle": subtitles[pid], "entries": entries},
        )

    category_names = {cat["name"] for item in phyla for cat in item["categories"]}
    placements = sum(len(item["categories"]) for item in phyla)
    dump(
        out_dir / "phyla.json",
        {
            "version": 1,
            "generated_from": "library/ida-library.csv",
            "entry_count": len(rows),
            "category_count": len(category_names),
            "placement_count": placements,
            "phyla": phyla,
        },
    )
    dump(
        out_dir / "exemplars.json",
        {
            "version": 1,
            "note": (
                "Full text for the authored entries only. "
                "Use these as the voice for scenarios and feedback. "
                "For every other id, use your own knowledge. "
                "Do not invent a quotation."
            ),
            "entries": [authored[eid] for eid in AUTHORED_ORDER],
        },
    )
    return {
        "entries": len(rows),
        "phyla": len(phyla),
        "categories": len({cat["name"] for item in phyla for cat in item["categories"]}),
        "placements": sum(len(item["categories"]) for item in phyla),
        "authored": len(authored),
        "spot": sum(item["spot"] for item in phyla),
        "decide": sum(item["decide"] for item in phyla),
    }


def main() -> None:
    csv_path = LIBRARY / "ida-library.csv"
    if len(sys.argv) > 1:
        csv_path = Path(sys.argv[1])
    out_dir = LIBRARY
    if len(sys.argv) > 2:
        out_dir = Path(sys.argv[2])
    summary = build(csv_path, out_dir)
    print(
        f"{summary['entries']} entries, {summary['phyla']} phyla, "
        f"{summary['categories']} categories ({summary['placements']} placements), {summary['authored']} authored, "
        f"{summary['decide']} decide, {summary['spot']} spot"
    )


if __name__ == "__main__":
    main()
