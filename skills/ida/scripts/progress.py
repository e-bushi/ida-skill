"""Progress operations for ~/.ida/progress.json.

These six operations are the whole memory API. A later server can replace
the file if it keeps the same inputs and outputs:

    loadProgress()
    saveProfile(fields)
    startSession(selection)
    saveSession(patch)
    recordAttempt(attempt)
    endSession()

Stdout is JSON. Errors go to stderr and the process exits 1.
Do not write the load payload back to disk. It adds welcome and bars,
which are not part of the file.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta

from catalog import load_catalog
from common import (
    DISPLAY_NAMES,
    HISTORY_CAP,
    MODES,
    PROMPT_LIMIT,
    RECENT_CAP,
    RESULTS,
    SELECTIONS,
    SUMMARY_LIMIT,
    VERSION,
    die,
    now,
    plain,
    plain_prompt,
    progress_path,
    write_json,
)


def blank_practice() -> dict:
    return {
        "streak": 0,
        "last_day": None,
        "milestones": {},
        "daily_id": None,
        "daily_day": None,
        "pending_note": None,
    }


def empty() -> dict:
    return {
        "version": VERSION,
        "profile": None,
        "session": None,
        "entries": {},
        "recent_scenarios": [],
        "history": [],
        "practice": blank_practice(),
    }


def _migrate(data: dict) -> bool:
    version = data.get("version", 1)
    if version not in (1, 2):
        die(f"progress file version {version!r} is not supported (expected {VERSION}): keep the file and update ida")
    changed = False
    if version == 1:
        data["version"] = 2
        changed = True
    practice = data.get("practice")
    if not isinstance(practice, dict):
        data["practice"] = blank_practice()
        changed = True
    else:
        base = blank_practice()
        for key, value in base.items():
            if key not in practice:
                practice[key] = value
                changed = True
    for key, default in empty().items():
        if key not in data:
            data[key] = default() if callable(default) else default
            changed = True
    return changed


def load_file(path) -> dict:
    if not path.exists():
        data = empty()
        write_json(path, data)
        return data
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        die(f"progress file is not valid json: {path}")
    if data.get("profile") is not None and not isinstance(data.get("profile"), dict):
        die("profile must be an object or null")
    if _migrate(data):
        save_file(path, data)
    return data


def save_file(path, data: dict) -> None:
    practice = data.get("practice")
    if not isinstance(practice, dict):
        practice = blank_practice()
    stored = {
        "version": VERSION,
        "profile": data.get("profile"),
        "session": data.get("session"),
        "entries": data.get("entries") or {},
        "recent_scenarios": data.get("recent_scenarios") or [],
        "history": data.get("history") or [],
        "practice": practice,
    }
    write_json(path, stored)


def blank_stats(name: str) -> dict:
    return {
        "name": name,
        "attempts": 0,
        "strong": 0,
        "partial": 0,
        "miss": 0,
        "idk": 0,
        "last_practiced": None,
        "last_result": None,
    }


def today() -> str:
    return date.today().isoformat()


def touch_streak(data: dict, day: str | None = None) -> None:
    practice = data.setdefault("practice", blank_practice())
    day = day or today()
    last = practice.get("last_day")
    if last == day:
        return
    if last:
        previous = (date.fromisoformat(day) - timedelta(days=1)).isoformat()
        practice["streak"] = int(practice.get("streak") or 0) + 1 if last == previous else 1
    else:
        practice["streak"] = 1
    practice["last_day"] = day


def note_milestone(data: dict, phylum: str, strong: int, partial: int, total: int) -> int:
    if total <= 0:
        return 0
    credit = min(total, strong + 0.5 * partial)
    percent = int(round(100 * credit / total))
    practice = data.setdefault("practice", blank_practice())
    milestones = practice.setdefault("milestones", {})
    current = int(milestones.get(phylum) or 0)
    crossed = 0
    for mark in (25, 50, 75, 100):
        if percent >= mark and current < mark:
            crossed = mark
    if crossed:
        milestones[phylum] = crossed
        practice["pending_note"] = f"{DISPLAY_NAMES.get(phylum, phylum)}|{crossed}"
    return crossed


def catalog_index():
    phyla_doc, entries = load_catalog()
    by_id = {entry["id"]: entry for entry in entries}
    return phyla_doc, entries, by_id


def phylum_bars(stats: dict, phyla_doc: dict, entries: list[dict]) -> list[dict]:
    by_phylum: dict[str, list[str]] = {}
    for entry in entries:
        by_phylum.setdefault(entry["phylum"], []).append(entry["id"])
    bars = []
    for phylum in phyla_doc["phyla"]:
        ids = by_phylum.get(phylum["id"], [])
        well = sum(1 for eid in ids if stats.get(eid, {}).get("strong", 0) >= 1)
        bars.append(
            {
                "phylum": phylum["id"],
                "subtitle": phylum["subtitle"],
                "well": well,
                "total": phylum["count"],
            }
        )
    return bars


def category_bar(stats: dict, entries: list[dict], phylum: str | None, category: str | None):
    if not phylum or not category:
        return None
    ids = [entry["id"] for entry in entries if entry["phylum"] == phylum and entry["category"] == category]
    if not ids:
        return None
    well = sum(1 for eid in ids if stats.get(eid, {}).get("strong", 0) >= 1)
    return {"label": category, "well": well, "total": len(ids)}


def section_bars(session: dict | None, stats: dict, entries: list[dict], bars: list[dict]) -> list[dict]:
    if not session:
        return []
    rows = []
    if session.get("phylum") and session.get("category"):
        cat = category_bar(stats, entries, session["phylum"], session["category"])
        if cat:
            rows.append(cat)
    live = session.get("in_progress") or {}
    phylum = live.get("phylum") or session.get("last_phylum") or session.get("phylum")
    match = next((bar for bar in bars if bar["phylum"] == phylum), None)
    if match is not None:
        rows.append(match)
    return rows


def shown_name(phylum: str | None) -> str:
    if not phylum:
        return ""
    return DISPLAY_NAMES.get(phylum, phylum)


def welcome_for(data: dict) -> dict:
    session = data.get("session")
    if session and session.get("in_progress"):
        live = session["in_progress"]
        phylum = shown_name(live.get("phylum") or session.get("phylum")) or "a mixed set"
        number = live.get("number")
        return {"kind": "resume", "line": f"Last time: {phylum}, scenario {number}."}
    if session and int(session.get("number") or 0) > 0:
        phylum = shown_name(session.get("last_phylum") or session.get("phylum"))
        number = session["number"]
        if phylum:
            line = f"Last time: {phylum}, scenario {number}."
        else:
            line = f"Last time: scenario {number}."
        return {"kind": "returning", "line": line}
    history = data.get("history") or []
    if history:
        last = history[-1]
        phylum = shown_name(last.get("phylum") or last.get("last_phylum"))
        count = last.get("scenarios") or 0
        noun = "scenario" if count == 1 else "scenarios"
        if last.get("phylum"):
            line = f"Last time: {shown_name(last['phylum'])}, {count} {noun}."
        elif phylum:
            line = f"Last time: {count} {noun}, last one in {phylum}."
        else:
            line = f"Last time: {count} {noun}."
        return {"kind": "returning", "line": line}
    if data.get("profile"):
        return {"kind": "ready", "line": ""}
    return {"kind": "new", "line": ""}


def next_number(session: dict | None) -> int:
    if not session:
        return 1
    live = session.get("in_progress")
    if live and live.get("number"):
        return int(live["number"])
    return int(session.get("number") or 0) + 1


def public_view(data: dict) -> dict:
    phyla_doc, entries, _by_id = catalog_index()
    bars = phylum_bars(data.get("entries") or {}, phyla_doc, entries)
    view = {
        "version": data["version"],
        "profile": data.get("profile"),
        "session": data.get("session"),
        "entries": data.get("entries") or {},
        "recent_scenarios": data.get("recent_scenarios") or [],
        "history": data.get("history") or [],
        "welcome": welcome_for(data),
        "next_number": next_number(data.get("session")),
        "bars": bars,
        "section_bars": section_bars(data.get("session"), data.get("entries") or {}, entries, bars),
    }
    if data.get("_last_ended"):
        view["ended"] = data["_last_ended"]
    return view


def save_profile(data: dict, role=None, interests=None, decisions=None) -> dict:
    profile = dict(data.get("profile") or {})
    if role is not None:
        profile["role"] = plain(role, 240)
    if interests is not None:
        profile["interests"] = plain(interests, 240)
    if decisions is not None:
        profile["decisions"] = plain(decisions, 400)
    for key in ("role", "interests", "decisions"):
        profile.setdefault(key, "")
    profile["updated_at"] = now()
    data["profile"] = profile
    return profile


def _canonical_place(phylum: str | None, category: str | None, entries: list[dict]):
    if phylum is not None:
        match = sorted({entry["phylum"] for entry in entries if entry["phylum"].lower() == phylum.lower()})
        if not match:
            die(f"unknown section {phylum!r}")
        phylum = match[0]
    if category is None:
        return phylum, None
    found = [
        entry
        for entry in entries
        if entry["category"].lower() == category.lower() and (phylum is None or entry["phylum"] == phylum)
    ]
    if not found:
        die(f"unknown category {category!r}")
    homes = sorted({entry["phylum"] for entry in found})
    if phylum is None and len(homes) > 1:
        die(f"category {category!r} is in more than one section. Name the section too.")
    return phylum, found[0]["category"]


def new_session(selection: str, phylum, category, mode: str) -> dict:
    stamp = now()
    return {
        "id": "s_" + stamp.replace("-", "").replace(":", ""),
        "started_at": stamp,
        "updated_at": stamp,
        "selection": selection,
        "phylum": phylum,
        "category": category,
        "mode": mode,
        "number": 0,
        "counts": {"strong": 0, "partial": 0, "miss": 0, "idk": 0},
        "queue": [],
        "in_progress": None,
        "log": [],
        "last_phylum": None,
    }


def end_session(data: dict, next_line: str | None = None) -> dict:
    session = data.get("session")
    if not session:
        die("no open session")
    counts = session.get("counts") or {}
    scenarios = sum(int(counts.get(name, 0)) for name in RESULTS)
    unanswered = bool(session.get("in_progress"))
    sharpest, revisit = _sharpest_revisit(session.get("log") or [])
    if not next_line:
        next_line = _default_next(session)
    summary = {
        "scenarios": scenarios,
        "strong": int(counts.get("strong", 0)),
        "partial": int(counts.get("partial", 0)),
        "miss": int(counts.get("miss", 0)),
        "idk": int(counts.get("idk", 0)),
        "sharpest": sharpest,
        "revisit": revisit,
        "next": next_line,
        "unanswered": unanswered,
    }
    meaningful = scenarios > 0 or unanswered
    if meaningful:
        data["history"].append(
            {
                "id": session.get("id"),
                "started_at": session.get("started_at"),
                "ended_at": now(),
                "selection": session.get("selection"),
                "phylum": session.get("phylum"),
                "category": session.get("category"),
                "last_phylum": session.get("last_phylum"),
                "mode": session.get("mode"),
                "scenarios": scenarios,
                "strong": summary["strong"],
                "partial": summary["partial"],
                "miss": summary["miss"],
                "idk": summary["idk"],
                "sharpest": sharpest,
                "revisit": revisit,
                "next": next_line,
                "unanswered": unanswered,
            }
        )
        data["history"] = data["history"][-HISTORY_CAP:]
    data["session"] = None
    return summary


def _sharpest_revisit(log: list[dict]) -> tuple[str, str]:
    strong_counts: dict[str, int] = {}
    strong_last = ""
    revisit = ""
    for event in log:
        for update in event.get("updates") or []:
            name = update.get("name") or ""
            result = update.get("result")
            if not name:
                continue
            if result == "strong":
                strong_counts[name] = strong_counts.get(name, 0) + 1
                strong_last = name
            elif result in ("miss", "partial", "idk"):
                revisit = name
    if not strong_counts:
        return "", revisit
    best = max(strong_counts.values())
    if strong_counts.get(strong_last) == best:
        return strong_last, revisit
    winners = [name for name, count in strong_counts.items() if count == best]
    return winners[-1], revisit


def _default_next(session: dict) -> str:
    if session.get("queue"):
        return "pick up the ideas you chose"
    if session.get("selection") == "random" or not session.get("phylum"):
        if session.get("selection") == "random":
            return "pick up at random"
        return "pick up wherever you like"
    if session.get("category"):
        return f"pick up in {session['category']}"
    return f"pick up in {shown_name(session.get('phylum'))}"


def start_session(data: dict, selection: str, phylum, category, mode: str, fresh: bool) -> dict:
    if selection not in SELECTIONS:
        die(f"selection must be one of {', '.join(SELECTIONS)}")
    if mode not in MODES:
        die(f"mode must be one of {', '.join(MODES)}")
    _phyla, entries, _by_id = catalog_index()
    if selection == "section" and not phylum:
        die("a section needs a phylum")
    phylum, category = _canonical_place(phylum, category, entries)
    if data.get("session") and data["session"].get("in_progress") and not fresh:
        die("a scenario is in progress. continue it, or start fresh")
    ended = None
    if fresh and data.get("session"):
        ended = end_session(data)
    if data.get("session") and not fresh:
        session = data["session"]
        session["selection"] = selection
        session["phylum"] = phylum
        session["category"] = category
        session["mode"] = mode
        session["updated_at"] = now()
        data["_last_ended"] = ended
        return session
    data["session"] = new_session(selection, phylum, category, mode)
    data["_last_ended"] = ended
    return data["session"]


def save_session(data: dict, patch: dict) -> dict:
    session = data.get("session")
    if not session:
        die("no open session")
    _phyla, entries, by_id = catalog_index()
    allowed = ("selection", "phylum", "category", "mode", "queue", "in_progress", "number")
    unknown = [key for key in patch if key not in allowed]
    if unknown:
        die(f"save cannot set {', '.join(unknown)}")
    if "mode" in patch and patch["mode"] not in MODES:
        die(f"mode must be one of {', '.join(MODES)}")
    if "selection" in patch and patch["selection"] not in SELECTIONS:
        die(f"selection must be one of {', '.join(SELECTIONS)}")
    phylum = patch["phylum"] if "phylum" in patch else session.get("phylum")
    category = patch["category"] if "category" in patch else session.get("category")
    if "phylum" in patch or "category" in patch:
        phylum, category = _canonical_place(phylum, category, entries)
        patch["phylum"] = phylum
        patch["category"] = category
    if "queue" in patch:
        queue = patch["queue"]
        if not isinstance(queue, list) or any(not isinstance(item, str) for item in queue):
            die("queue must be a list of ids")
        missing = [item for item in queue if item not in by_id]
        if missing:
            die(f"unknown ids in queue: {', '.join(missing)}")
        patch["queue"] = queue[:30]
    if "in_progress" in patch and patch["in_progress"] is not None:
        patch["in_progress"] = _clean_live(patch["in_progress"], by_id)
        session["last_phylum"] = patch["in_progress"].get("phylum")
        if patch["in_progress"].get("number"):
            session["number"] = int(patch["in_progress"]["number"])
    for key in allowed:
        if key in patch:
            session[key] = patch[key]
    session["updated_at"] = now()
    return session


def _clean_live(live: dict, by_id: dict) -> dict:
    if not isinstance(live, dict):
        die("in_progress must be an object or null")
    for key in ("number", "practice", "phylum", "entry_ids", "prompt", "mode"):
        if key not in live:
            die(f"in_progress missing {key}")
    if live["practice"] not in ("decide", "spot"):
        die("in_progress.practice must be decide or spot")
    if live["mode"] not in MODES:
        die("in_progress.mode must be free or choice")
    ids = live["entry_ids"]
    if not isinstance(ids, list) or not ids or any(item not in by_id for item in ids):
        die("in_progress.entry_ids must be library ids")
    names = [by_id[item]["name"] for item in ids]
    options = live.get("options") or []
    if options and (
        not isinstance(options, list)
        or any("id" not in item or "name" not in item for item in options)
    ):
        die("options must be a list of {id, name}")
    cleaned_options = []
    for index, item in enumerate(options[:6], start=1):
        if item["id"] not in by_id:
            die(f"unknown option {item['id']}")
        cleaned_options.append({"n": index, "id": item["id"], "name": item["name"]})
    return {
        "number": int(live["number"]),
        "practice": live["practice"],
        "phylum": live["phylum"],
        "category": live.get("category") or by_id[ids[0]]["category"],
        "entry_ids": list(ids),
        "names": names,
        "prompt": plain_prompt(str(live["prompt"]), PROMPT_LIMIT),
        "mode": live["mode"],
        "options": cleaned_options,
    }


def record_attempt(data: dict, attempt: dict) -> dict:
    session = data.get("session")
    if not session:
        die("no open session")
    result = attempt.get("session_result")
    if result not in RESULTS:
        die(f"session_result must be one of {', '.join(RESULTS)}")
    updates = attempt.get("updates")
    if not isinstance(updates, list) or not updates:
        die("updates must list the ideas this attempt touched")
    _phyla, entries, by_id = catalog_index()
    cleaned = []
    for update in updates:
        eid = update.get("id")
        grade = update.get("result")
        if eid not in by_id:
            die(f"unknown id {eid!r}")
        if grade not in RESULTS:
            die(f"update result must be one of {', '.join(RESULTS)}")
        cleaned.append({"id": eid, "name": by_id[eid]["name"], "result": grade})
        stats = data["entries"].setdefault(eid, blank_stats(by_id[eid]["name"]))
        stats["name"] = by_id[eid]["name"]
        stats["attempts"] = int(stats.get("attempts", 0)) + 1
        stats[grade] = int(stats.get(grade, 0)) + 1
        stats["last_practiced"] = now()
        stats["last_result"] = grade
    session.setdefault("counts", {name: 0 for name in RESULTS})
    session["counts"][result] = int(session["counts"].get(result, 0)) + 1
    live = session.get("in_progress") or {}
    number = int(live.get("number") or session.get("number") or 0)
    summary = plain(str(attempt.get("summary") or ""), SUMMARY_LIMIT)
    if not summary:
        die("summary is required")
    session.setdefault("log", []).append(
        {"number": number, "result": result, "updates": cleaned, "summary": summary}
    )
    planned = set(live.get("entry_ids") or [])
    if planned:
        session["queue"] = [eid for eid in session.get("queue") or [] if eid not in planned]
    entry_ids = live.get("entry_ids") or [item["id"] for item in cleaned]
    primary = by_id[entry_ids[0]]
    data["recent_scenarios"].append(
        {
            "at": now(),
            "entry_ids": entry_ids,
            "phylum": live.get("phylum") or primary["phylum"],
            "category": live.get("category") or primary["category"],
            "practice": live.get("practice") or primary["practice"],
            "summary": summary,
            "result": result,
            "mode": live.get("mode") or session.get("mode") or "free",
        }
    )
    data["recent_scenarios"] = data["recent_scenarios"][-RECENT_CAP:]
    session["in_progress"] = None
    session["number"] = number
    if live.get("phylum"):
        session["last_phylum"] = live["phylum"]
    session["updated_at"] = now()
    touch_streak(data)
    phylum = live.get("phylum") or primary["phylum"]
    strong_n = partial_n = total_n = 0
    for entry in entries:
        if entry["phylum"] != phylum:
            continue
        total_n += 1
        state = data["entries"].get(entry["id"]) or {}
        if int(state.get("strong") or 0) >= 1:
            strong_n += 1
        elif int(state.get("partial") or 0) >= 1:
            partial_n += 1
    note_milestone(data, phylum, strong_n, partial_n, total_n)
    bars = phylum_bars(data["entries"], catalog_index()[0], entries)
    return {
        "ok": True,
        "counts": session["counts"],
        "number": number,
        "next_number": number + 1,
        "section_bars": section_bars(session, data["entries"], entries, bars),
        "bars": bars,
    }


def emit(payload: dict) -> None:
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="ida progress operations")
    parser.add_argument("--path", help="progress.json path. Default ~/.ida/progress.json or $IDA_PROGRESS")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("load")

    profile = sub.add_parser("save-profile")
    profile.add_argument("--role")
    profile.add_argument("--interests")
    profile.add_argument("--decisions")

    start = sub.add_parser("start")
    start.add_argument("--selection", required=True, choices=SELECTIONS)
    start.add_argument("--phylum")
    start.add_argument("--category")
    start.add_argument("--mode", default="free", choices=MODES)
    start.add_argument("--fresh", action="store_true")

    sub.add_parser("save")
    sub.add_parser("record")
    end = sub.add_parser("end")
    end.add_argument("--next", default="")

    args = parser.parse_args()
    path = progress_path(args.path)
    try:
        data = load_file(path)
        if args.cmd == "load":
            emit(public_view(data))
            return
        if args.cmd == "save-profile":
            if args.role is None and args.interests is None and args.decisions is None:
                die("pass at least one of --role, --interests, --decisions")
            save_profile(data, args.role, args.interests, args.decisions)
        elif args.cmd == "start":
            start_session(data, args.selection, args.phylum, args.category, args.mode, args.fresh)
        elif args.cmd == "save":
            patch = json.loads(sys.stdin.read() or "{}")
            save_session(data, patch)
        elif args.cmd == "record":
            record_attempt(data, json.loads(sys.stdin.read() or "{}"))
        elif args.cmd == "end":
            summary = end_session(data, args.next or None)
            save_file(path, data)
            _phyla, entries, _by_id = catalog_index()
            bars = phylum_bars(data.get("entries") or {}, _phyla, entries)
            emit({"summary": summary, "bars": bars})
            return
        save_file(path, data)
        emit(public_view(data))
    except SystemExit as exc:
        if isinstance(exc.code, str):
            print(exc.code, file=sys.stderr)
            sys.exit(1)
        raise


if __name__ == "__main__":
    main()
