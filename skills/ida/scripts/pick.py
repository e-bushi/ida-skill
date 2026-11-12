"""Choose the next idea without pasting the catalog into the chat.

Reads the lean index and the progress file. Prints one JSON object:
the intended idea or ideas, and options when --choices is set.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys

from catalog import load_catalog
from common import RECENT_AVOID, die, progress_path

PAIR_CHANCE = 0.25


def squeeze(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def recent_ids(path) -> set[str]:
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    found: list[str] = []
    for item in (data.get("recent_scenarios") or [])[-RECENT_AVOID:]:
        found.extend(item.get("entry_ids") or [])
    return set(found)


def stats_for(path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data.get("entries") or {}


def resolve_one(query: str, catalog: list[dict]) -> tuple[dict | None, list[dict]]:
    sq = squeeze(query)
    if len(sq) < 2:
        return None, []

    def ranked(pool: list[dict]) -> list[dict]:
        return sorted(pool, key=lambda entry: (len(entry["name"]), entry["name"]))[:5]

    exact = [
        entry
        for entry in catalog
        if squeeze(entry["name"]) == sq or squeeze(entry["id"]) == sq
    ]
    if len(exact) == 1:
        return exact[0], []
    if len(exact) > 1:
        return None, ranked(exact)
    if len(sq) >= 4:
        starts = [
            entry
            for entry in catalog
            if squeeze(entry["name"]).startswith(sq) or squeeze(entry["id"]).startswith(sq)
        ]
        if len(starts) == 1:
            return starts[0], []
        if len(starts) > 1:
            return None, ranked(starts)
    if len(sq) >= 3:
        holds = [
            entry
            for entry in catalog
            if sq in squeeze(entry["name"]) or sq in squeeze(entry["id"])
        ]
        if len(holds) == 1:
            return holds[0], []
        if len(holds) > 1:
            return None, ranked(holds)
    return None, []


def score_entry(entry: dict, stats: dict) -> float:
    row = stats.get(entry["id"]) or {}
    attempts = int(row.get("attempts") or 0)
    strong = int(row.get("strong") or 0)
    if attempts == 0:
        base = 12.0
    elif strong == 0:
        base = 7.0
    else:
        base = 1.0
    return base


def canonical_section(catalog, phylum, category):
    if phylum:
        homes = sorted({entry["phylum"] for entry in catalog if entry["phylum"].lower() == phylum.lower()})
        if not homes:
            die(f"unknown section {phylum}")
        phylum = homes[0]
    if category:
        hits = [
            entry
            for entry in catalog
            if entry["category"].lower() == category.lower() and (phylum is None or entry["phylum"] == phylum)
        ]
        homes = sorted({entry["phylum"] for entry in hits})
        if not hits:
            die(f"unknown category {category}")
        if phylum is None and len(homes) > 1:
            die("category " + category + " is in " + ", ".join(homes) + ". Pass --phylum.")
        if phylum is None:
            phylum = homes[0]
        category = hits[0]["category"]
    return phylum, category


def choose_pool(catalog, phylum, category, avoided: set[str], practice: str | None = None) -> list[dict]:
    pool = catalog
    if phylum:
        pool = [entry for entry in pool if entry["phylum"] == phylum]
    if category:
        pool = [entry for entry in pool if entry["category"] == category]
    if practice:
        pool = [entry for entry in pool if entry["practice"] == practice]
    if not pool:
        die("nothing in that section")
    fresh = [entry for entry in pool if entry["id"] not in avoided]
    return fresh or pool


def pick_scored(pool: list[dict], stats: dict, rng: random.Random) -> dict:
    scored = sorted(((score_entry(entry, stats), entry["id"], entry) for entry in pool), reverse=True)
    best = scored[0][0]
    band = [entry for value, _eid, entry in scored if value >= best - 3]
    top = [entry for value, _eid, entry in scored if value == best]
    if len(top) >= 8:
        band = top
    return rng.choice(band)


def distractors(
    catalog: list[dict],
    intended: list[dict],
    avoided: set[str],
    rng: random.Random,
    count: int,
) -> list[dict]:
    taken = {entry["id"] for entry in intended}
    primary = intended[0]

    def rank(entry: dict) -> tuple:
        same_cat = entry["phylum"] == primary["phylum"] and entry["category"] == primary["category"]
        same_phylum = entry["phylum"] == primary["phylum"]
        same_kind = entry["practice"] == primary["practice"]
        recent_penalty = entry["id"] in avoided
        return (
            0 if same_cat else 1,
            0 if same_kind else 1,
            0 if same_phylum else 1,
            1 if recent_penalty else 0,
            entry["id"],
        )

    pool = [entry for entry in catalog if entry["id"] not in taken]
    if not pool or count <= 0:
        return []
    pool.sort(key=rank)
    best_key = rank(pool[0])[:3] if pool else None
    near = [entry for entry in pool if rank(entry)[:3] == best_key]
    if len(near) < count:
        near = pool[: max(count * 4, count)]
    if len(near) > count:
        chosen = rng.sample(near, count)
    else:
        chosen = near
    return chosen


def public_entry(entry: dict) -> dict:
    return {
        "id": entry["id"],
        "name": entry["name"],
        "phylum": entry["phylum"],
        "subtitle": entry["subtitle"],
        "category": entry["category"],
        "practice": entry["practice"],
    }


def build_options(intended: list[dict], extras: list[dict], rng: random.Random) -> list[dict]:
    rows = intended + extras
    rng.shuffle(rows)
    return [{"n": index, "id": entry["id"], "name": entry["name"]} for index, entry in enumerate(rows, start=1)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Pick the next ida idea")
    parser.add_argument("--progress")
    parser.add_argument("--random", action="store_true")
    parser.add_argument("--phylum")
    parser.add_argument("--category")
    parser.add_argument("--ids", help="comma-separated library ids to use as written")
    parser.add_argument("--name", action="append", default=[])
    parser.add_argument("--names", help="comma-separated names, only when none contain a comma")
    parser.add_argument("--choices", action="store_true")
    parser.add_argument("--pair", choices=("auto", "yes", "no"), default="auto")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--practice", choices=("spot", "decide"))
    args = parser.parse_args()

    queries = list(args.name)
    if args.names:
        queries.extend(part.strip() for part in args.names.split(",") if part.strip())
    if not args.random and not args.phylum and not args.category and not args.ids and not queries:
        die("pass --random, --phylum, --ids, or --name")

    _doc, catalog = load_catalog()
    by_id = {entry["id"]: entry for entry in catalog}
    path = progress_path(args.progress)
    avoided = recent_ids(path)
    stats = stats_for(path)
    seed = args.seed if args.seed is not None else random.SystemRandom().randrange(1, 2**31)
    rng = random.Random(seed)

    unmatched = []
    matches = []
    if queries:
        for query in queries:
            found, suggestions = resolve_one(query, catalog)
            if found is None:
                unmatched.append(
                    {"query": query, "suggestions": [entry["name"] for entry in suggestions]}
                )
            elif all(found["id"] != item["id"] for item in matches):
                matches.append(found)

    intended: list[dict] = []
    if args.ids:
        for eid in [part.strip() for part in args.ids.split(",") if part.strip()]:
            if eid not in by_id:
                die(f"unknown id {eid}")
            intended.append(by_id[eid])
    elif matches:
        intended = [matches[0]]
    elif queries:
        intended = []
    else:
        phylum, category = canonical_section(catalog, args.phylum, args.category)
        pool = choose_pool(catalog, phylum, category, avoided, args.practice)
        primary = pick_scored(pool, stats, rng)
        intended = [primary]
        want_pair = args.pair == "yes" or (args.pair == "auto" and primary["practice"] == "decide" and rng.random() < PAIR_CHANCE)
        if want_pair:
            siblings = [
                entry
                for entry in pool
                if entry["id"] != primary["id"]
                and entry["phylum"] == primary["phylum"]
                and entry["category"] == primary["category"]
            ]
            if siblings:
                intended.append(pick_scored(siblings, stats, rng))

    if not intended and unmatched:
        payload = {"seed": seed, "matches": [], "unmatched": unmatched, "queue": []}
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return
    if not intended:
        die("no idea selected")

    payload = {
        "seed": seed,
        "practice": intended[0]["practice"],
        "phylum": intended[0]["phylum"],
        "subtitle": intended[0]["subtitle"],
        "category": intended[0]["category"],
        "intended": [public_entry(entry) for entry in intended],
    }
    if queries:
        payload["matches"] = [public_entry(entry) for entry in matches]
        payload["unmatched"] = unmatched
        payload["queue"] = [entry["id"] for entry in matches]
    if args.choices:
        need = 4 - len(intended)
        extras = distractors(catalog, intended, avoided, rng, max(need, 0)) if need > 0 else []
        payload["options"] = build_options(intended, extras, rng)
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
