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
from color import color_mode, paint
from progress import (
    end_session,
    load_file,
    record_attempt,
    save_file,
    save_profile,
    save_session,
    start_session,
    today,
    touch_streak,
    welcome_for,
)
import render


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
    touch_streak(data)
    save_file(path, data)
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
    if getattr(args, "spot", False):
        command.extend(["--practice", "spot", "--choices"])
    if getattr(args, "ids", None):
        command.extend(["--ids", args.ids])
    proc = subprocess.run(command, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr or proc.stdout)
        raise SystemExit(1)
    return json.loads(proc.stdout)


def cmd_next(path, args) -> None:
    data = load_file(path)
    if args.daily:
        practice = data.setdefault("practice", {})
        day = today()
        if practice.get("daily_day") == day and practice.get("daily_id"):
            args.ids = practice["daily_id"]
        else:
            args.random = True
            args.seed = int(day.replace("-", "")) % (2**31 - 1)
            args.store_daily = day
    if args.spot:
        args.choices = True
        if not args.phylum and not args.name and not getattr(args, "ids", None):
            args.random = True
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
    if getattr(args, "store_daily", None):
        data["practice"]["daily_day"] = args.store_daily
    save_file(path, data)
    picked = _run_pick(path, args)
    if getattr(args, "store_daily", None) and picked.get("intended"):
        data = load_file(path)
        data["practice"]["daily_id"] = picked["intended"][0]["id"]
        data["practice"]["daily_day"] = args.store_daily
        save_file(path, data)
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


def _rows(data, catalog) -> list[dict]:
    counted = credits(data.get("entries") or {}, catalog)
    return [
        {"phylum": phylum, "strong": counted[phylum]["strong"], "partial": counted[phylum]["partial"], "total": counted[phylum]["total"]}
        for phylum in DISPLAY_ORDER
    ]


def _read_text(args, field: str) -> str:
    value = getattr(args, field, "") or ""
    if value:
        return value
    if sys.stdin is not None and not sys.stdin.isatty():
        return sys.stdin.read()
    return ""


def cmd_show(path, args) -> None:
    data = load_file(path)
    touch_streak(data)
    save_file(path, data)
    _doc, catalog = load_catalog()
    rows = _rows(data, catalog)
    practice = data.get("practice") or {}
    collected = sum(1 for item in (data.get("entries") or {}).values() if int(item.get("strong") or 0) >= 1)
    session_n = len(data.get("history") or []) + (1 if data.get("session") else 0)
    if session_n <= 0:
        session_n = 1
    screen = args.screen
    note = practice.get("pending_note")
    if screen == "opening":
        text = render.opening(args.beat or 1)
    elif screen == "menu":
        text = render.menu(session_n, rows, collected, len(catalog), int(practice.get("streak") or 0))
    elif screen == "card":
        body = _read_text(args, "body")
        if not body.strip():
            sys.stderr.write("card needs a scene\n")
            raise SystemExit(1)
        text = render.card(
            args.number or 1,
            args.phylum or "axiom",
            body.strip(),
            practice=args.kind or "decide",
            mode=args.mode or "free",
            total=args.total,
        )
    elif screen == "strong":
        phylum = args.phylum or "axiom"
        row = next(item for item in rows if item["phylum"] == phylum)
        text = render.feedback_strong(
                args.comment or "That's the move.",
                args.reached or "the idea",
                args.deeper or "Say what it changes in this scene.",
                phylum,
                row["strong"],
                row["partial"],
                row["total"] or 1,
            )
    elif screen == "partial":
        phylum = args.phylum or "axiom"
        row = next(item for item in rows if item["phylum"] == phylum)
        text = render.feedback_partial(
            args.got or "the neighborhood",
            args.missing or "the stake",
            args.try_it or "Name it, then say what it changes.",
            phylum,
            row["strong"],
            row["partial"],
            row["total"] or 1,
        )
    elif screen == "idk":
        moves = []
        for raw in args.move or []:
            title, _, detail = raw.partition("|")
            moves.append((title or "step", detail or title))
        while len(moves) < 3:
            moves.append(("keep going", "one concrete note"))
        text = render.feedback_not_yet(
            args.name or "the idea",
            args.explain or "Saying so is the honest start. Here's one way in.",
            moves[:3],
            args.closing or "Name the idea, then say what it changes here.",
        )
    elif screen == "summary":
        reached = [part.strip() for part in (args.reached or "").split(",") if part.strip()]
        log = ((data.get("session") or {}).get("log")) or []
        strong = partial = miss = idk = 0
        if data.get("session"):
            counts = data["session"].get("counts") or {}
            strong = int(counts.get("strong") or 0)
            partial = int(counts.get("partial") or 0)
            miss = int(counts.get("miss") or 0)
            idk = int(counts.get("idk") or 0)
        elif data.get("history"):
            last = data["history"][-1]
            strong = int(last.get("strong") or 0)
            partial = int(last.get("partial") or 0)
            miss = int(last.get("miss") or 0)
            idk = int(last.get("idk") or 0)
        scenarios = strong + partial + miss + idk
        text = render.summary_block(
            scenarios,
            strong,
            partial,
            miss,
            idk,
            reached[0] if reached else "",
            "",
            "",
            session=session_n,
            date=today().split("-")[2].lstrip("0") + " " + __import__("datetime").date.today().strftime("%b").upper() + " " + today()[:4],
            reached=reached,
            carry=args.carry or "Name the idea, then say what it changes here.",
            signoff_index=(session_n - 1) % 2,
            rows=rows,
        )
        del log
    else:
        sys.stderr.write("unknown screen\n")
        raise SystemExit(1)
    if note and screen in ("strong", "partial", "menu", "summary"):
        lane, _, mark = note.partition("|")
        text = text + f"\n\n  ■ {lane} crossed {mark}%"
        practice = data.setdefault("practice", {})
        practice["pending_note"] = None
        save_file(path, data)
    elif screen == "menu":
        save_file(path, data)
    sys.stdout.write(paint(text, color_mode()) + "\n")


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
    nxt.add_argument("--daily", action="store_true")
    nxt.add_argument("--spot", action="store_true")
    save = sub.add_parser("save")
    save.add_argument("--result", required=True, choices=("strong", "partial", "miss", "idk"))
    save.add_argument("--id")
    save.add_argument("--summary", required=True)
    sub.add_parser("end")
    show = sub.add_parser("show")
    show.add_argument("screen", choices=("opening", "menu", "card", "strong", "partial", "idk", "summary"))
    show.add_argument("--beat", type=int, default=1)
    show.add_argument("--phylum")
    show.add_argument("--number", type=int, default=1)
    show.add_argument("--total", type=int)
    show.add_argument("--body", default="")
    show.add_argument("--kind", default="decide")
    show.add_argument("--mode", default="free")
    show.add_argument("--comment", default="")
    show.add_argument("--reached", default="")
    show.add_argument("--deeper", default="")
    show.add_argument("--got", default="")
    show.add_argument("--missing", default="")
    show.add_argument("--try", dest="try_it", default="")
    show.add_argument("--name", default="")
    show.add_argument("--explain", default="")
    show.add_argument("--closing", default="")
    show.add_argument("--carry", default="")
    show.add_argument("--move", action="append", default=[])
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
    elif args.cmd == "show":
        cmd_show(path, args)


if __name__ == "__main__":
    main()
