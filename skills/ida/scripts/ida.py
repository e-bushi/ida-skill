"""The only command a sitting should run.

open prints one machine line. save, profile, and end print nothing.
Do not show this output in the chat. Draw the screen yourself.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from types import SimpleNamespace

from catalog import load_catalog
from common import DISPLAY_NAMES, DISPLAY_ORDER, RESULTS, ROOT, progress_path
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


def status_json(data: dict, catalog: list[dict]) -> dict:
    welcome = welcome_for(data)
    counted = credits(data.get("entries") or {}, catalog)
    return {
        "kind": welcome["kind"],
        "line": welcome["line"],
        "bars": {
            phylum: [counted[phylum]["strong"], counted[phylum]["partial"], counted[phylum]["total"]]
            for phylum in DISPLAY_ORDER
        },
    }


def cmd_open(path) -> None:
    data = load_file(path)
    touch_streak(data)
    save_file(path, data)
    _doc, catalog = load_catalog()
    sys.stdout.write(json.dumps(status_json(data, catalog), ensure_ascii=False) + "\n")


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


def deal(path, data, args) -> dict:
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
        suggestions = picked["unmatched"][0].get("suggestions") or []
        return {"unmatched": query, "suggestions": suggestions}
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
    info = {
        "practice": picked["practice"],
        "section": DISPLAY_NAMES[picked["phylum"]],
        "phylum": picked["phylum"],
        "id": intended[0]["id"],
        "name": intended[0]["name"],
        "ids": [item["id"] for item in intended],
        "names": [item["name"] for item in intended],
        "number": number,
        "mode": mode,
        "options": [item["name"] for item in options],
    }
    return info


def cmd_next(path, args) -> None:
    data = load_file(path)
    sys.stdout.write(json.dumps(deal(path, data, args), ensure_ascii=False) + "\n")


def read_stdin_payload() -> dict:
    """JSON on stdin, or plain text treated as a card scene. A tty is empty."""
    if sys.stdin is None or sys.stdin.isatty():
        return {}
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {"body": raw}
    if not isinstance(data, dict):
        return {"body": raw}
    return data


def _moves(spec: dict, flagged: list[str]) -> list[tuple[str, str]]:
    moves: list[tuple[str, str]] = []
    raw = spec.get("moves") if spec.get("moves") is not None else spec.get("move")
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, str):
                title, _, detail = item.partition("|")
                moves.append((title or "step", detail or title))
            elif isinstance(item, (list, tuple)) and item:
                title = str(item[0])
                detail = str(item[1]) if len(item) > 1 else title
                moves.append((title, detail))
            elif isinstance(item, dict):
                title = str(item.get("title") or "step")
                detail = str(item.get("detail") or item.get("note") or "")
                moves.append((title, detail or title))
    if not moves:
        for item in flagged or []:
            title, _, detail = item.partition("|")
            moves.append((title or "step", detail or title))
    return moves


def cmd_save(path, args) -> None:
    data = load_file(path)
    payload = read_stdin_payload()
    session = data.get("session") or {}
    live = session.get("in_progress") or {}
    intended = live.get("entry_ids") or []
    credited = args.id or payload.get("id") or (intended[0] if intended else None)
    if not credited:
        sys.stderr.write("nothing to save\n")
        raise SystemExit(1)
    summary = args.summary or str(payload.get("summary") or "")
    record_attempt(
        data,
        {
            "session_result": args.result,
            "updates": [{"id": credited, "result": args.result}],
            "summary": summary,
        },
    )
    names = live.get("names") or []
    data["session"]["screen"] = {
        "result": args.result,
        "summary": summary,
        "name": payload.get("name") or (names[0] if names else ""),
        "phylum": payload.get("phylum") or live.get("phylum") or "",
        "explain": payload.get("explain") or "",
        "moves": _moves(payload, []),
        "closing": payload.get("closing") or "",
        "comment": payload.get("comment") or "",
        "reached": payload.get("reached") or "",
        "deeper": payload.get("deeper") or "",
        "got": payload.get("got") or "",
        "missing": payload.get("missing") or "",
        "try": payload.get("try") or "",
        "carry": payload.get("carry") or "",
        "body": payload.get("body") or "",
        "number": live.get("number"),
        "mode": payload.get("mode") or live.get("mode") or "free",
        "kind": payload.get("kind") or live.get("practice") or "decide",
    }
    save_file(path, data)


def _rows(data, catalog) -> list[dict]:
    counted = credits(data.get("entries") or {}, catalog)
    return [
        {"phylum": phylum, "strong": counted[phylum]["strong"], "partial": counted[phylum]["partial"], "total": counted[phylum]["total"]}
        for phylum in DISPLAY_ORDER
    ]


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
    payload = read_stdin_payload()
    stored = (data.get("session") or {}).get("screen") or {}
    spec = {**stored, **{key: value for key, value in payload.items() if value not in ("", None, [])}}
    if screen == "opening":
        text = render.opening(args.beat or 1)
    elif screen == "menu":
        text = render.menu(session_n, rows, collected, len(catalog), int(practice.get("streak") or 0))
    elif screen == "card":
        body = args.body or spec.get("body") or ""
        if not str(body).strip():
            sys.stderr.write("card needs a scene\n")
            raise SystemExit(1)
        text = render.card(
            int(spec.get("number") or args.number or 1),
            args.phylum or spec.get("phylum") or "axiom",
            str(body).strip(),
            practice=args.kind if args.kind != "decide" else spec.get("kind") or "decide",
            mode=args.mode if args.mode != "free" else spec.get("mode") or "free",
            total=args.total,
        )
    elif screen == "strong":
        phylum = args.phylum or spec.get("phylum") or "axiom"
        row = next(item for item in rows if item["phylum"] == phylum)
        text = render.feedback_strong(
            args.comment or spec.get("comment") or "That's the move.",
            args.reached or spec.get("reached") or spec.get("name") or "the idea",
            args.deeper or spec.get("deeper") or "Say what it changes in this scene.",
            phylum,
            row["strong"],
            row["partial"],
            row["total"] or 1,
        )
    elif screen == "partial":
        phylum = args.phylum or spec.get("phylum") or "axiom"
        row = next(item for item in rows if item["phylum"] == phylum)
        text = render.feedback_partial(
            args.got or spec.get("got") or "the neighborhood",
            args.missing or spec.get("missing") or "the stake",
            args.try_it or spec.get("try") or "Name it, then say what it changes.",
            phylum,
            row["strong"],
            row["partial"],
            row["total"] or 1,
        )
    elif screen == "idk":
        moves = _moves(spec, args.move or [])
        while len(moves) < 3:
            moves.append(("keep going", "one concrete note"))
        text = render.feedback_not_yet(
            args.name or spec.get("name") or "the idea",
            args.explain or spec.get("explain") or "Saying so is the honest start. Here's one way in.",
            moves[:3],
            args.closing or spec.get("closing") or "Name the idea, then say what it changes here.",
        )
    elif screen == "summary":
        reached_raw = args.reached or spec.get("reached") or ""
        if isinstance(reached_raw, list):
            reached = [str(part).strip() for part in reached_raw if str(part).strip()]
        else:
            reached = [part.strip() for part in str(reached_raw).split(",") if part.strip()]
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
            carry=args.carry or spec.get("carry") or "Name the idea, then say what it changes here.",
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


def emit(path, data, text: str, info: dict) -> None:
    session = data.get("session")
    if isinstance(session, dict):
        session["await"] = info.get("await")
    save_file(path, data)
    sys.stderr.write(json.dumps(info, ensure_ascii=False, separators=(",", ":")) + "\n")
    sys.stdout.write(paint(text, color_mode()) + "\n")


def _menu_text(data, catalog) -> str:
    rows = _rows(data, catalog)
    practice = data.get("practice") or {}
    collected = sum(1 for item in (data.get("entries") or {}).values() if int(item.get("strong") or 0) >= 1)
    session_n = len(data.get("history") or []) + (1 if data.get("session") else 0)
    if session_n <= 0:
        session_n = 1
    return render.menu(session_n, rows, collected, len(catalog), int(practice.get("streak") or 0))


def _pick_spec(**kwargs):
    base = dict(
        random=False,
        phylum=None,
        category=None,
        name=None,
        choices=False,
        seed=None,
        fresh=False,
        spot=False,
        daily=False,
        ids=None,
    )
    base.update(kwargs)
    return SimpleNamespace(**base)


def _lane_phylum(choice: str) -> str | None:
    token = choice.strip().lower()
    if token.isdigit():
        index = int(token)
        if 1 <= index <= len(DISPLAY_ORDER):
            return DISPLAY_ORDER[index - 1]
        return None
    for phylum, name in DISPLAY_NAMES.items():
        if token == phylum or token == name:
            return phylum
    return None


def _render_card(info: dict, body: str) -> str:
    options = info.get("options") or None
    return render.card(
        int(info.get("number") or 1),
        info.get("phylum") or "axiom",
        body,
        practice=info.get("practice") or "decide",
        mode=info.get("mode") or "free",
        options=options,
    )


def _show_card(path, data, info: dict, body: str) -> None:
    scene = (body or "").strip()
    text = _render_card(info, scene or "SCENE")
    payload = {
        "screen": "card",
        "await": "answer",
        "id": info.get("id"),
        "name": info.get("name"),
        "section": info.get("section"),
        "phylum": info.get("phylum"),
        "practice": info.get("practice"),
        "mode": info.get("mode"),
        "number": info.get("number"),
        "options": info.get("options") or [],
    }
    if not scene:
        payload["fill"] = "SCENE"
    emit(path, data, text, payload)


def _show_menu(path, data, catalog) -> None:
    emit(path, data, _menu_text(data, catalog), {"screen": "menu", "await": "lane"})


def _grade(path, data, result: str, payload: dict, live: dict) -> None:
    intended = live.get("entry_ids") or []
    credited = payload.get("id") or (intended[0] if intended else None)
    if not credited:
        _doc, catalog = load_catalog()
        _show_menu(path, data, catalog)
        return
    summary = str(payload.get("summary") or payload.get("answer") or result)
    record_attempt(
        data,
        {"session_result": result, "updates": [{"id": credited, "result": result}], "summary": summary},
    )
    names = live.get("names") or []
    screen = {
        "result": result,
        "summary": summary,
        "name": payload.get("name") or (names[0] if names else ""),
        "phylum": payload.get("phylum") or live.get("phylum") or "",
        "explain": payload.get("explain") or "",
        "moves": [list(pair) for pair in _moves(payload, [])],
        "closing": payload.get("closing") or "",
        "comment": payload.get("comment") or "",
        "reached": payload.get("reached") or (names[0] if names else ""),
        "deeper": payload.get("deeper") or "",
        "got": payload.get("got") or "",
        "missing": payload.get("missing") or "",
        "try": payload.get("try") or "",
        "carry": payload.get("carry") or "",
        "body": payload.get("body") or "",
        "number": live.get("number"),
        "mode": live.get("mode") or "free",
        "kind": live.get("practice") or "decide",
        "id": credited,
    }
    data["session"]["screen"] = screen
    _doc, catalog = load_catalog()
    rows = _rows(data, catalog)
    phylum = screen["phylum"] or "axiom"
    row = next(item for item in rows if item["phylum"] == phylum)
    if result == "idk":
        moves = _moves(screen, [])
        while len(moves) < 3:
            moves.append(("keep going", "one concrete note"))
        text = render.feedback_not_yet(
            screen["name"] or "the idea",
            screen["explain"] or "Saying so is the honest start. Here's one way in.",
            moves[:3],
            screen["closing"] or "Name the idea, then say what it changes here.",
        )
        info = {"screen": "idk", "await": "next", "name": screen["name"], "id": credited}
    elif result == "partial":
        text = render.feedback_partial(
            screen["got"] or "the neighborhood",
            screen["missing"] or "the stake",
            screen["try"] or "Name it, then say what it changes.",
            phylum,
            row["strong"],
            row["partial"],
            row["total"] or 1,
        )
        info = {"screen": "partial", "await": "next", "name": screen["name"], "id": credited}
    elif result == "strong":
        text = render.feedback_strong(
            screen["comment"] or "That's the move.",
            screen["reached"] or screen["name"] or "the idea",
            screen["deeper"] or "Say what it changes in this scene.",
            phylum,
            row["strong"],
            row["partial"],
            row["total"] or 1,
        )
        info = {"screen": "strong", "await": "next", "name": screen["name"], "id": credited}
    else:
        text = _menu_text(data, catalog)
        info = {"screen": "menu", "await": "lane", "result": result}
    note = (data.get("practice") or {}).get("pending_note")
    if note and result in ("strong", "partial"):
        lane, _, mark = note.partition("|")
        text = text + f"\n\n  ■ {lane} crossed {mark}%"
        data["practice"]["pending_note"] = None
    emit(path, data, text, info)


def _deal_and_show(path, data, spec, body: str) -> None:
    info = deal(path, data, spec)
    data = load_file(path)
    if info.get("unmatched"):
        _doc, catalog = load_catalog()
        emit(
            path,
            data,
            _menu_text(data, catalog),
            {"screen": "menu", "await": "lane", "unmatched": info["unmatched"], "suggestions": info.get("suggestions") or []},
        )
        return
    _show_card(path, data, info, body)


def cmd_turn(path, args) -> None:
    data = load_file(path)
    touch_streak(data)
    payload = read_stdin_payload()
    choice = " ".join(args.choice or []).strip()
    if not choice:
        choice = str(payload.get("choice") or payload.get("answer") or "").strip()
    _doc, catalog = load_catalog()
    key = choice.lower()
    profile = data.get("profile")
    if not profile:
        practice = data.setdefault("practice", {})
        draft = practice.setdefault("draft", {"step": 1})
        step = int(draft.get("step") or 1)
        fields = ("role", "interests", "decisions")
        if choice and step <= 3:
            draft[fields[step - 1]] = choice
            step += 1
            draft["step"] = step
        if step > 3:
            save_profile(data, draft.get("role", ""), draft.get("interests", ""), draft.get("decisions", ""))
            practice.pop("draft", None)
            _show_menu(path, data, catalog)
            return
        save_file(path, data)
        emit(path, data, render.opening(step), {"screen": "opening", "await": "profile", "beat": step})
        return
    session = data.get("session") or {}
    live = session.get("in_progress") or {}
    awaiting = "card" if live else (session.get("await") or "lane")
    if key in ("done", "stop"):
        if data.get("session"):
            log = (data["session"].get("log") or [])
            reached = []
            for event in log:
                for update in event.get("updates") or []:
                    if update.get("result") == "strong" and update.get("name"):
                        reached.append(update["name"])
            counts = data["session"].get("counts") or {}
            end_session(data)
            session_n = len(data.get("history") or [])
            text = render.summary_block(
                int(counts.get("strong", 0)) + int(counts.get("partial", 0)) + int(counts.get("miss", 0)) + int(counts.get("idk", 0)),
                int(counts.get("strong", 0)),
                int(counts.get("partial", 0)),
                int(counts.get("miss", 0)),
                int(counts.get("idk", 0)),
                reached[0] if reached else "",
                "",
                "",
                session=session_n or 1,
                reached=reached,
                carry=str(payload.get("carry") or "Name the idea, then say what it changes here."),
                signoff_index=(session_n - 1) % 2,
                rows=_rows(data, catalog),
            )
            emit(path, data, text, {"screen": "summary", "await": "done"})
            return
        _show_menu(path, data, catalog)
        return
    if key == "menu":
        _show_menu(path, data, catalog)
        return
    if key == "why" or key == "show me":
        screen = session.get("screen") or {}
        phylum = screen.get("phylum") or "axiom"
        row = next(item for item in _rows(data, catalog) if item["phylum"] == phylum)
        text = render.feedback_strong(
            screen.get("comment") or screen.get("explain") or "One more pass at the same stake.",
            screen.get("reached") or screen.get("name") or "the idea",
            screen.get("deeper") or "Say what it changes here.",
            phylum,
            row["strong"],
            row["partial"],
            row["total"] or 1,
        )
        emit(path, data, text, {"screen": "why", "await": "next", "name": screen.get("name")})
        return
    result = str(payload.get("result") or "")
    if key in RESULTS:
        result = key
    if key == "skip":
        result = "miss"
        payload.setdefault("summary", "skipped")
    if live and choice and not result and key not in (
        "menu",
        "done",
        "stop",
        "next",
        "again",
        "another",
        "another like this",
        "retry",
        "why",
        "show me",
        "hint",
        "skip",
        "daily",
        "spot",
        "surprise",
        "surprise me",
        "random",
    ):
        options = live.get("options") or []
        if key.isdigit() and options:
            number = int(key)
            chosen = None
            for index, item in enumerate(options, start=1):
                if int(item.get("n") or index) == number:
                    chosen = item
                    break
            correct = bool(chosen and chosen.get("id") in (live.get("entry_ids") or []))
            result = "strong" if correct else "miss"
            payload.setdefault("summary", (chosen or {}).get("name") or choice)
        else:
            held = {
                "number": live.get("number"),
                "phylum": live.get("phylum"),
                "practice": live.get("practice"),
                "mode": live.get("mode"),
                "options": [item.get("name") for item in options],
                "id": (live.get("entry_ids") or [""])[0],
                "name": (live.get("names") or [""])[0],
                "section": DISPLAY_NAMES.get(live.get("phylum") or "", ""),
            }
            emit(
                path,
                data,
                _render_card(held, str(payload.get("body") or "SCENE")),
                {"screen": "card", "await": "answer", "error": "result required", "name": held["name"], "id": held["id"]},
            )
            return
    if live and result:
        _grade(path, data, result, payload, live)
        return
    if live and key == "hint":
        _show_card(
            path,
            data,
            {
                "number": live.get("number"),
                "phylum": live.get("phylum"),
                "practice": live.get("practice"),
                "mode": live.get("mode"),
                "options": [item.get("name") for item in (live.get("options") or [])],
                "id": (live.get("entry_ids") or [""])[0],
                "name": (live.get("names") or [""])[0],
                "section": DISPLAY_NAMES.get(live.get("phylum") or "", ""),
            },
            str(payload.get("body") or ""),
        )
        return
    if key in ("next", "again", "another", "another like this", "retry") or (not live and result):
        screen = session.get("screen") or {}
        if key == "retry" and screen.get("id"):
            spec = _pick_spec(ids=screen["id"], fresh=False)
        elif key == "daily" or False:
            spec = _pick_spec(daily=True)
        else:
            phylum = session.get("last_phylum") or session.get("phylum")
            spec = _pick_spec(phylum=phylum, random=not phylum, fresh=False)
        if data.get("session") and data["session"].get("in_progress"):
            data["session"]["in_progress"] = None
            save_file(path, data)
            data = load_file(path)
        _deal_and_show(path, data, spec, str(payload.get("body") or ""))
        return
    lane = _lane_phylum(choice) if choice else None
    if key in ("daily", "spot", "surprise", "surprise me", "random") or lane or (choice and awaiting == "lane"):
        if key == "daily":
            spec = _pick_spec(daily=True, fresh=False)
        elif key == "spot":
            spec = _pick_spec(spot=True, fresh=False)
        elif key in ("surprise", "surprise me", "random"):
            spec = _pick_spec(random=True, fresh=False)
        elif lane:
            spec = _pick_spec(phylum=lane, fresh=False)
        else:
            spec = _pick_spec(random=True, fresh=False)
        if data.get("session") and data["session"].get("in_progress"):
            data["session"]["in_progress"] = None
            save_file(path, data)
            data = load_file(path)
        _deal_and_show(path, data, spec, str(payload.get("body") or ""))
        return
    _show_menu(path, data, catalog)


def cmd_end(path) -> None:
    data = load_file(path)
    if not data.get("session"):
        return
    end_session(data)
    save_file(path, data)


def _refuse_help(message: str) -> None:
    del message
    sys.stderr.write("commands are in references/commands.md\n")
    raise SystemExit(2)


def main() -> None:
    if any(arg in ("-h", "--help") for arg in sys.argv[1:]):
        _refuse_help("help")
    parser = argparse.ArgumentParser(add_help=False, description="ida session memory")
    parser.error = _refuse_help
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
    save.add_argument("--summary", default="")
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
    turn = sub.add_parser("turn")
    turn.add_argument("choice", nargs="*")
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
    elif args.cmd == "turn":
        cmd_turn(path, args)


if __name__ == "__main__":
    main()
