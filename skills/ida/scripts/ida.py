"""The only command a sitting should run.

open prints one machine line. save, profile, and end print nothing.
Do not show this output in the chat. Draw the screen yourself.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

from catalog import load_catalog
from common import DISPLAY_NAMES, DISPLAY_ORDER, ROOT, progress_path
from progress import (
    load_file,
    record_attempt,
    save_file,
    save_profile,
    save_session,
    start_session,
    end_session,
    welcome_for,
)


def credits(stats: dict, catalog: list[dict]) -> dict:
    rows = {phylum: {"strong": 0, "partial": 0, "total": 0} for phylum in DISPLAY_ORDER}
    for entry in catalog:
        bucket = rows.get(entry["phylum"])
        if bucket is None:
            continue
        bucket["total"] += 1
        state = stats.get(entry["id"]) or {}
        if int(state.get("strong") or 0) >= 1:
            bucket["strong"] += 1
        elif int(state.get("partial") or 0) >= 1:
            bucket["partial"] += 1
    return rows


def machine_line(data: dict, catalog: list[dict]) -> str:
    welcome = welcome_for(data)
    kind = welcome["kind"]
    if kind == "resume":
        head = "RESUME|" + welcome["line"]
    elif kind == "returning":
        head = "BACK|" + welcome["line"]
    elif kind == "ready":
        head = "READY"
    else:
        head = "NEW"
    bits = []
    counted = credits(data.get("entries") or {}, catalog)
    for phylum in DISPLAY_ORDER:
        row = counted[phylum]
        bits.append(f"{phylum}:{row['strong']}:{row['partial']}:{row['total']}")
    return head + "|bars|" + ",".join(bits)


def cmd_open(path) -> None:
    data = load_file(path)
    _doc, catalog = load_catalog()
    print(machine_line(data, catalog))


def cmd_profile(path, args) -> None:
    data = load_file(path)
    save_profile(data, args.role, args.interests, args.decisions)
    save_file(path, data)


def _run_pick(path, args) -> dict:
    command = [sys.executable, str(ROOT / "scripts" / "pick.py"), "--progress", str(path), "--pair", "auto"]
    if args.random:
        command.append("--random")
    if args.phylum:
        command.extend(["--phylum", args.phylum])
    if args.category:
        command.extend(["--category", args.category])
    for name in args.name or []:
        command.extend(["--name", name])
    if args.choices:
        command.append("--choices")
    if args.seed is not None:
        command.extend(["--seed", str(args.seed)])
    proc = subprocess.run(command, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr or proc.stdout)
        raise SystemExit(1)
    return json.loads(proc.stdout)


def cmd_next(path, args) -> None:
    data = load_file(path)
    if args.name:
        selection = "pick"
    elif args.random or not args.phylum:
        selection = "random"
    else:
        selection = "section"
    mode = "choice" if args.choices else "free"
    if data.get("session") and data["session"].get("in_progress") and not args.fresh:
        sys.stderr.write("a scenario is in progress\n")
        raise SystemExit(1)
    start_session(
        data,
        selection,
        args.phylum,
        args.category,
        mode,
        bool(args.fresh),
    )
    save_file(path, data)
    picked = _run_pick(path, args)
    if picked.get("unmatched") and not picked.get("intended"):
        query = picked["unmatched"][0]["query"]
        suggestions = ",".join(picked["unmatched"][0].get("suggestions") or [])
        print(f"UNMATCHED|{query}|{suggestions}")
        return
    intended = picked["intended"]
    number = int(data["session"].get("number") or 0) + 1
    options = picked.get("options") or []
    live = {
        "number": number,
        "practice": picked["practice"],
        "phylum": picked["phylum"],
        "category": picked.get("category"),
        "entry_ids": [item["id"] for item in intended],
        "prompt": "held",
        "mode": mode,
        "options": [{"id": item["id"], "name": item["name"]} for item in options],
    }
    data = load_file(path)
    save_session(data, {"in_progress": live, "queue": picked.get("queue") or data["session"].get("queue") or []})
    save_file(path, data)
    fields = [
        picked["practice"],
        DISPLAY_NAMES[picked["phylum"]],
        intended[0]["id"],
        intended[0]["name"],
    ]
    if len(intended) > 1:
        fields.extend([intended[1]["id"], intended[1]["name"]])
    if options:
        fields.append("opts")
        fields.extend(item["name"] for item in options)
    print("\t".join(fields))


def cmd_save(path, args) -> None:
    data = load_file(path)
    session = data.get("session") or {}
    live = session.get("in_progress") or {}
    intended = live.get("entry_ids") or []
    credited = args.id or (intended[0] if intended else None)
    if not credited:
        sys.stderr.write("nothing to save\n")
        raise SystemExit(1)
    record_attempt(
        data,
        {
            "session_result": args.result,
            "updates": [{"id": credited, "result": args.result}],
            "summary": args.summary,
        },
    )
    save_file(path, data)


def cmd_end(path) -> None:
    data = load_file(path)
    if not data.get("session"):
        return
    end_session(data)
    save_file(path, data)


def main() -> None:
    parser = argparse.ArgumentParser(description="ida session memory")
    parser.add_argument("--path")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("open")
    profile = sub.add_parser("profile")
    profile.add_argument("--role")
    profile.add_argument("--interests")
    profile.add_argument("--decisions")
    nxt = sub.add_parser("next")
    nxt.add_argument("--random", action="store_true")
    nxt.add_argument("--phylum")
    nxt.add_argument("--category")
    nxt.add_argument("--name", action="append")
    nxt.add_argument("--choices", action="store_true")
    nxt.add_argument("--seed", type=int)
    nxt.add_argument("--fresh", action="store_true")
    save = sub.add_parser("save")
    save.add_argument("--result", required=True, choices=("strong", "partial", "miss", "idk"))
    save.add_argument("--id")
    save.add_argument("--summary", required=True)
    sub.add_parser("end")
    args = parser.parse_args()
    path = progress_path(args.path)
    if args.cmd == "open":
        cmd_open(path)
    elif args.cmd == "profile":
        cmd_profile(path, args)
    elif args.cmd == "next":
        cmd_next(path, args)
    elif args.cmd == "save":
        cmd_save(path, args)
    elif args.cmd == "end":
        cmd_end(path)


if __name__ == "__main__":
    main()
