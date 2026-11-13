"""The only command a sitting should run is `ida turn`.

Stdout is the plain screen. Its last line is a spacer, so a collapsed
log has an empty tail. idk prints one reminder on stderr, then a spacer.
`turn` does not read stdin and does not write a temp file.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from types import SimpleNamespace

from catalog import load_catalog
from common import (
    DISPLAY_NAMES,
    DISPLAY_ORDER,
    PROMPT_LIMIT,
    RESULTS,
    ROOT,
    SPACER,
    SUMMARY_LIMIT,
    TAIL,
    progress_path,
)
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
    card_streak,
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
    write_machine(json.dumps(status_json(data, catalog), ensure_ascii=False))


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
        _err(proc.stderr or proc.stdout or "could not deal a card")
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
    if args.name or getattr(args, "ids", None):
        selection = "pick"
    elif args.random or not args.phylum:
        selection = "random"
    else:
        selection = "section"
    mode = "choice" if args.choices else "free"
    if data.get("session") and data["session"].get("in_progress") and not args.fresh:
        _err("a scenario is in progress")
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
    write_machine(json.dumps(deal(path, data, args), ensure_ascii=False))


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
        _err("nothing to save")
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
    typed = _remember_typed(data, bool(getattr(args, "typed", False)))
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
        text = render.menu(session_n, rows, collected, len(catalog), int(practice.get("streak") or 0), typed=typed)
    elif screen == "card":
        body = args.body or spec.get("body") or ""
        if not str(body).strip():
            _err("card needs a scene")
            raise SystemExit(1)
        text = render.card(
            int(spec.get("number") or args.number or 1),
            args.phylum or spec.get("phylum") or "axiom",
            str(body).strip(),
            practice=args.kind if args.kind != "decide" else spec.get("kind") or "decide",
            mode=args.mode if args.mode != "free" else spec.get("mode") or "free",
            total=args.total,
            typed=typed,
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
            typed=typed,
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
            typed=typed,
        )
    elif screen == "idk":
        text = render.feedback_not_yet(
            args.name or spec.get("name") or "the idea",
            args.explain or spec.get("explain") or spec.get("definition") or "",
            typed=typed,
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
            typed=typed,
        )
        del log
    else:
        _err("unknown screen")
        raise SystemExit(1)
    if note and screen in ("strong", "partial", "menu", "summary"):
        lane, _, mark = note.partition("|")
        text = text + "\n" + SPACER + "\n" + f"  ■ {lane} crossed {mark}%"
        practice = data.setdefault("practice", {})
        practice["pending_note"] = None
        save_file(path, data)
    elif screen == "menu":
        save_file(path, data)
    write_screen(text)


REMIND_IDK = "paste this reveal, then write how it applies in three steps, then the choice tool"
REMIND_IDK_OPEN = "no stored definition. paste the banner, write the definition and three steps, then the choice tool"
NAV = {
    "menu",
    "back to the menu",
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
    "got it",
    "another angle",
    "explain it another way",
    "explain",
    "deal",
}
NEXT_KEYS = {"next", "again", "another", "another like this", "retry", "got it"}


def write_machine(text: str) -> None:
    sys.stdout.write(text.rstrip("\n") + "\n" + TAIL)


def write_screen(text: str, reminder: str = "") -> None:
    painted = paint(text.replace("\r\n", "\n").rstrip("\n"), color_mode())
    sys.stdout.write(painted + "\n")
    if reminder:
        sys.stderr.write(reminder.rstrip("\n") + "\n" + TAIL)
        sys.stderr.flush()
    sys.stdout.write(TAIL)
    sys.stdout.flush()


def _err(message: str) -> None:
    text = (message or "").rstrip("\n")
    if text:
        sys.stderr.write(text + "\n")
    sys.stderr.write(TAIL)


def _agent_preamble(screen: str, question: str = "") -> str:
    lead = (
        "[ida -> agent] The user cannot see this output. "
        "Paste everything between the markers into your reply in a ```text fence"
    )
    if screen == "idk":
        note = lead + ", then write how it applies + 3 steps, THEN call the choice tool."
    elif screen == "card":
        note = lead + ". Replace the word SCENE with the scene. Keep the question. Do not call the choice tool on a free-text card."
    elif screen in ("menu", "strong", "partial", "why", "miss"):
        note = lead + ", THEN call the choice tool."
    elif screen == "summary":
        note = lead + "."
    elif screen == "opening":
        note = lead + ". Call the choice tool. Work is one role plus Other. Interests is multiSelect plus Other. Decisions is one pick plus Other."
    elif screen == "explain":
        note = lead + ", THEN call the choice tool. Put the explanation in that question, not in a separate message. Replace each <placeholder>."
    elif screen == "hint":
        note = lead + ", THEN call the choice tool. Put the nudge in that question, not in a separate message. Do not name the idea."
    else:
        note = lead + ". Then stop so they can type."
    if question:
        note += " The choice tool question MUST be the exact string after QUESTION:."
    return note


def _wrap_for_agent(text: str, screen: str, question: str = "") -> str:
    body = text.replace("\r\n", "\n").rstrip("\n")
    wrapped = _agent_preamble(screen, question) + "\nBEGIN\n" + body + "\nEND"
    if question:
        wrapped += "\n" + question
    return wrapped


def _called(name: str) -> str:
    name = " ".join(str(name).split()) or "the idea"
    return name[0].upper() + name[1:]


def _as_sentence(text: str) -> str:
    text = " ".join(str(text).split())
    if not text:
        return ""
    text = text[0].upper() + text[1:]
    if text[-1] not in ".!?":
        text += "."
    return text


def _banner_mode() -> str:
    mode = os.environ.get("IDA_QUESTION_BANNER", "block").strip().lower()
    return "spaced" if mode == "spaced" else "block"


def _split_name(name: str) -> tuple[str, str, str]:
    """Return the banner name, a symbol like (→), and a caps gloss if any."""
    text = " ".join(str(name).split())
    if text.endswith(")") and " (" in text:
        head, _, tail = text.rpartition(" (")
        inside = tail[:-1]
        if not head:
            return text, "", ""
        symbolic = any(not (ch.isalpha() or ch.isdigit() or ch in " ,'\"-±") for ch in inside)
        short = len(inside) <= 12 and " " not in inside.strip()
        if symbolic or short:
            return head, f"({inside})", ""
        return head, "", inside
    return text, "", ""


def _framed_name(name: str, mode: str) -> str:
    """Heavy frame around the name. Every line is at most 64 columns."""
    from banner import question_banner, spaced_caps

    bare, symbol, gloss = _split_name(name)
    if mode == "spaced":
        inner = ["  " + line for line in _wrap_plain(spaced_caps(bare), 62)]
    else:
        inner = ["  " + line for line in question_banner(bare, 62)]
    if gloss:
        inner.extend("  " + line for line in _wrap_plain(spaced_caps(gloss), 62))
    if symbol:
        inner.extend("  " + line for line in _wrap_plain(symbol, 62))
    rule = "━" * 64
    return "\n".join([rule, *inner, rule])


def _wrap_plain(text: str, width: int) -> list[str]:
    words = text.split()
    if not words:
        return []
    lines: list[str] = []
    current = ""
    for word in words:
        if not current:
            current = word
        elif len(current) + 1 + len(word) <= width:
            current = current + " " + word
        else:
            lines.append(current)
            current = word
        while len(current) > width:
            lines.append(current[:width])
            current = current[width:]
    if current:
        lines.append(current)
    return lines


def _idk_question(name: str, definition: str) -> str:
    """Framed name, definition, a scene placeholder, then the ask.

    The default is a lowercase Sora banner inside a heavy frame. A longer
    name uses the 4-row size, then one word per line. Line breaks in the
    Cursor choice box do render, so the question is multi-line. Set
    IDA_QUESTION_BANNER=spaced to use spaced caps inside the same frame.
    The agent replaces the scene placeholder. The script does not know the scene.
    """
    mode = _banner_mode()
    gloss = _as_sentence(definition) if definition.strip() else "<one-line definition you write>."
    gloss_lines = ["  " + line for line in _wrap_plain(gloss, 62)]
    scene = "  In your scene: <one sentence on this scene>."
    body = "\n".join([_framed_name(name, mode), *gloss_lines, "", scene, "", "Where to from here?"])
    return f"QUESTION_BANNER: {mode}\nQUESTION:\n{body}"


def _question_line(result: str, name: str, definition: str = "") -> str:
    called = _called(name)
    if result == "idk":
        return _idk_question(name, definition)
    if result == "strong":
        return f"QUESTION: That's {called}. Where to from here?"
    if result == "partial":
        return f"QUESTION: Close. The idea was {called}. Where to from here?"
    if result in ("miss", "menu"):
        return f"QUESTION: The idea was {called}. Where to from here?"
    return ""


def _opening_question(step: int) -> str:
    prompts = {
        1: "QUESTION: What do you do for work?",
        2: "QUESTION: What are you into besides that? Pick any that fit.",
        3: "QUESTION: What decisions keep showing up for you?",
    }
    return prompts.get(step, prompts[1])


def _explain_question(name: str, definition: str) -> str:
    plain = _as_sentence(definition) if definition.strip() else "<one-line definition>."
    sentences = [
        f"In plain words: {plain}",
        "Like <everyday comparison>.",
        "In your scene: <one sentence on this scene>.",
        "Try it: <3 short steps>.",
    ]
    lines = [_framed_name(name, _banner_mode())]
    for sentence in sentences:
        lines.extend("  " + line for line in _wrap_plain(sentence, 62))
        lines.append("")
    lines.append("Where to from here?")
    return f"QUESTION_BANNER: {_banner_mode()}\nQUESTION:\n" + "\n".join(lines)


def _is_request(text: str) -> bool:
    token = " ".join(text.lower().split())
    if not token:
        return False
    if token.endswith("?"):
        return True
    return token.startswith(
        (
            "can you",
            "could you",
            "please",
            "explain",
            "break this",
            "help me",
            "what is",
            "how do",
            "how does",
            "tell me",
            "i don't",
            "still ",
        )
    )


def _clip(text: str, limit: int) -> str:
    return " ".join(str(text).split())[:limit]


def emit(path, data, text: str, info: dict, reminder: str = "", question: str = "") -> None:
    session = data.get("session")
    if isinstance(session, dict):
        session["await"] = info.get("await")
    save_file(path, data)
    write_screen(_wrap_for_agent(text, str(info.get("screen") or ""), question), reminder)


def _is_typed(data) -> bool:
    return bool((data.get("practice") or {}).get("typed"))


def _remember_typed(data, flag: bool) -> bool:
    if flag:
        data.setdefault("practice", {})["typed"] = True
    return _is_typed(data)


def _menu_text(data, catalog) -> str:
    rows = _rows(data, catalog)
    practice = data.get("practice") or {}
    collected = sum(1 for item in (data.get("entries") or {}).values() if int(item.get("strong") or 0) >= 1)
    session_n = len(data.get("history") or []) + (1 if data.get("session") else 0)
    if session_n <= 0:
        session_n = 1
    return render.menu(session_n, rows, collected, len(catalog), int(practice.get("streak") or 0), typed=_is_typed(data))


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


def _find_entry(query: str) -> dict | None:
    token = " ".join(query.lower().split())
    if not token:
        return None
    _doc, catalog = load_catalog()
    for entry in catalog:
        if entry["name"].lower() == token or entry["id"] == token:
            return entry
    return None


def _library_definition(entry_id: str) -> str:
    """The stored one-line law, or empty when this idea has no authored text."""
    path = ROOT / "library" / "exemplars.json"
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    for entry in doc.get("entries") or []:
        if entry.get("id") == entry_id:
            return " ".join(str(entry.get("law") or "").split())
    return ""


def _parse_turn(choice: list[str]) -> tuple[str, list[str]]:
    if not choice:
        return "", []
    head = choice[0].strip()
    key = head.lower()
    if key.startswith("got it"):
        return "got it", []
    if key in NAV or key in RESULTS or _lane_phylum(head):
        return head, [part.strip() for part in choice[1:] if part.strip()]
    return "", [" ".join(part.strip() for part in choice if part.strip())]


def _held(live: dict) -> dict:
    options = live.get("options") or []
    return {
        "number": live.get("number"),
        "phylum": live.get("phylum"),
        "practice": live.get("practice"),
        "mode": live.get("mode"),
        "options": [item.get("name") for item in options],
        "id": (live.get("entry_ids") or [""])[0],
        "name": _idea_name(live, {}),
        "section": DISPLAY_NAMES.get(live.get("phylum") or "", ""),
    }


def _lane_practiced(data, catalog, phylum: str) -> tuple[int, int]:
    ids = [entry["id"] for entry in catalog if entry.get("phylum") == phylum]
    entries = data.get("entries") or {}
    done = 0
    for eid in ids:
        if int((entries.get(eid) or {}).get("attempts") or 0) >= 1:
            done += 1
    return done, len(ids)


def _card_status(data, catalog, phylum: str, number: int) -> tuple[dict, int | None]:
    session = data.get("session") or {}
    done, lane_total = _lane_practiced(data, catalog, phylum)
    reached = int(number or 0)
    length = session.get("length")
    session_total = length if isinstance(length, int) and length >= reached and length > 0 else None
    status = {
        "lane_done": done,
        "lane_total": lane_total,
        "reached": reached,
        "session_total": session_total,
        "streak": card_streak(data),
    }
    return status, session_total


def _show_card(path, data, info: dict) -> None:
    _doc, catalog = load_catalog()
    number = int(info.get("number") or 1)
    phylum = info.get("phylum") or "axiom"
    status, session_total = _card_status(data, catalog, phylum, number)
    text = render.card(
        number,
        phylum,
        "SCENE",
        practice=info.get("practice") or "decide",
        mode=info.get("mode") or "free",
        options=info.get("options") or None,
        total=session_total,
        typed=_is_typed(data),
        status=status,
    )
    emit(
        path,
        data,
        text,
        {"screen": "card", "await": "answer", "name": info.get("name"), "id": info.get("id")},
        info.get("name") or "",
    )


def _show_menu(path, data, catalog) -> None:
    rows = _rows(data, catalog)
    question, options = render.menu_prompt(rows)
    block = "QUESTION: " + question + "\nOPTIONS:\n" + "\n".join(options)
    emit(path, data, _menu_text(data, catalog), {"screen": "menu", "await": "lane"}, "", block)


def _idea_name(live: dict, payload: dict) -> str:
    if payload.get("name"):
        return str(payload["name"])
    names = [item for item in (live.get("names") or []) if item]
    if names:
        return names[0]
    for eid in live.get("entry_ids") or []:
        _doc, catalog = load_catalog()
        for entry in catalog:
            if entry["id"] == eid:
                return entry["name"]
    return ""


def _remember_card(path, info: dict) -> dict:
    data = load_file(path)
    live = (data.get("session") or {}).get("in_progress") or {}
    name = info.get("name") or ""
    if info.get("names"):
        live["names"] = info["names"]
    elif name:
        live["names"] = [name]
    live["definition"] = _library_definition(info.get("id") or "")
    live["summary"] = _clip(name or "card", SUMMARY_LIMIT)
    data["session"]["in_progress"] = live
    save_file(path, data)
    return live


def _reveal_text(name: str, definition: str, typed: bool) -> str:
    return render.feedback_not_yet(name or "the idea", definition or "", typed=typed)


def _grade(path, data, result: str, live: dict) -> None:
    intended = live.get("entry_ids") or []
    credited = intended[0] if intended else None
    if not credited:
        _doc, catalog = load_catalog()
        _show_menu(path, data, catalog)
        return
    idea = _idea_name(live, {})
    definition = _clip(live.get("definition") or "", 500)
    if not definition:
        definition = _library_definition(credited)
    summary = _clip(live.get("summary") or idea or result, SUMMARY_LIMIT) or result
    record_attempt(
        data,
        {"session_result": result, "updates": [{"id": credited, "result": result}], "summary": summary},
    )
    screen = {
        "result": result,
        "summary": summary,
        "name": idea,
        "phylum": live.get("phylum") or "",
        "definition": definition,
        "explain": definition,
        "apply": definition,
        "closing": definition,
        "reached": idea,
        "deeper": definition,
        "number": live.get("number"),
        "mode": live.get("mode") or "free",
        "kind": live.get("practice") or "decide",
        "id": credited,
    }
    data["session"]["screen"] = screen
    _doc, catalog = load_catalog()
    rows = _rows(data, catalog)
    phylum = screen["phylum"] or "axiom"
    row = next((item for item in rows if item["phylum"] == phylum), {"strong": 0, "partial": 0, "total": 1})
    deeper = definition or "Say what it changes in this scene."
    reminder = ""
    if result == "idk":
        text = _reveal_text(idea, definition, _is_typed(data))
        info = {"screen": "idk", "await": "next", "name": idea, "id": credited, "phylum": phylum}
        reminder = REMIND_IDK if definition else REMIND_IDK_OPEN
    elif result == "partial":
        text = render.feedback_partial(
            "the neighborhood",
            "the stake",
            deeper,
            phylum,
            row["strong"],
            row["partial"],
            row["total"] or 1,
            typed=_is_typed(data),
        )
        info = {"screen": "partial", "await": "next", "name": idea, "id": credited}
    elif result == "strong":
        text = render.feedback_strong(
            "That's the move.",
            idea or "the idea",
            deeper,
            phylum,
            row["strong"],
            row["partial"],
            row["total"] or 1,
            typed=_is_typed(data),
        )
        info = {"screen": "strong", "await": "next", "name": idea, "id": credited}
    else:
        text = _menu_text(data, catalog)
        info = {"screen": "menu", "await": "lane", "result": result}
    note = (data.get("practice") or {}).get("pending_note")
    if note and result in ("strong", "partial"):
        lane, _, mark = note.partition("|")
        text = text + "\n" + SPACER + "\n" + f"  ■ {lane} crossed {mark}%"
        data["practice"]["pending_note"] = None
    question = ""
    if result in ("idk", "strong", "partial", "miss"):
        question = _question_line(result, idea, definition)
    emit(path, data, text, info, reminder, question)


def _spec_for(key: str, lane: str | None, entry_id: str | None, session: dict):
    screen = session.get("screen") or {}
    if entry_id:
        spec = _pick_spec(ids=entry_id, fresh=False)
    elif key == "retry" and screen.get("id"):
        spec = _pick_spec(ids=screen["id"], fresh=False)
    elif key == "daily":
        spec = _pick_spec(daily=True, fresh=False)
    elif key == "spot":
        spec = _pick_spec(spot=True, choices=True, fresh=False)
    elif key in ("surprise", "surprise me", "random"):
        spec = _pick_spec(random=True, fresh=False)
    elif lane:
        spec = _pick_spec(phylum=lane, fresh=False)
    else:
        phylum = session.get("last_phylum") or session.get("phylum")
        spec = _pick_spec(phylum=phylum, random=not phylum, fresh=False)
    if key == "spot":
        spec.spot = True
        spec.choices = True
    return spec


def _deal_and_show(path, data, spec) -> None:
    if data.get("session") and data["session"].get("in_progress") and not getattr(spec, "fresh", False):
        data["session"]["in_progress"] = None
        save_file(path, data)
        data = load_file(path)
    info = deal(path, data, spec)
    data = load_file(path)
    if info.get("unmatched"):
        _doc, catalog = load_catalog()
        _show_menu(path, data, catalog)
        _err("no idea under that name")
        return
    _remember_card(path, info)
    data = load_file(path)
    _show_card(path, data, info)


def _show_explain(path, data, name: str, definition: str) -> None:
    text = render.feedback_not_yet(name or "the idea", definition or "", typed=_is_typed(data))
    emit(
        path,
        data,
        text,
        {"screen": "explain", "await": "next", "name": name},
        "",
        _explain_question(name or "the idea", definition or ""),
    )


def _show_hint(path, data, live: dict) -> None:
    info = _held(live)
    _doc, catalog = load_catalog()
    number = int(info.get("number") or 1)
    phylum = info.get("phylum") or "axiom"
    status, session_total = _card_status(data, catalog, phylum, number)
    text = render.card(
        number,
        phylum,
        "SCENE",
        practice=info.get("practice") or "decide",
        mode=info.get("mode") or "free",
        options=info.get("options") or None,
        total=session_total,
        typed=_is_typed(data),
        status=status,
    )
    emit(
        path,
        data,
        text,
        {"screen": "hint", "await": "answer", "name": info.get("name"), "id": info.get("id")},
        info.get("name") or "",
        "QUESTION: In plain words: <one nudge, do not name the idea>. Where to from here?",
    )


def _is_next(key: str) -> bool:
    return key in NEXT_KEYS or key.startswith("got it")


def _deal_id(texts: list[str]) -> str | None:
    if not texts:
        return None
    found = _find_entry(texts[0])
    if not found:
        return ""
    return found["id"]


def cmd_turn(path, args) -> None:
    data = load_file(path)
    touch_streak(data)
    _remember_typed(data, bool(getattr(args, "typed", False)))
    action, texts = _parse_turn(list(args.choice or []))
    key = action.lower()
    _doc, catalog = load_catalog()
    if not data.get("profile"):
        practice = data.setdefault("practice", {})
        draft = practice.setdefault("draft", {"step": 1})
        step = int(draft.get("step") or 1)
        fields = ("role", "interests", "decisions")
        spoken = " ".join(args.choice or []).strip()
        if spoken and step <= 3:
            draft[fields[step - 1]] = _clip(spoken, 80)
            step += 1
            draft["step"] = step
        if step > 3:
            save_profile(data, draft.get("role", ""), draft.get("interests", ""), draft.get("decisions", ""))
            practice.pop("draft", None)
            _show_menu(path, data, catalog)
            return
        save_file(path, data)
        emit(
            path,
            data,
            render.opening(step),
            {"screen": "opening", "await": "profile", "beat": step},
            question=_opening_question(step),
        )
        return
    session = data.get("session") or {}
    live = session.get("in_progress") or {}
    if key in ("done", "stop"):
        if data.get("session"):
            log = data["session"].get("log") or []
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
                carry=(session.get("screen") or {}).get("definition") or "Name the idea, then say what it changes here.",
                signoff_index=(session_n - 1) % 2,
                rows=_rows(data, catalog),
                typed=_is_typed(data),
            )
            emit(path, data, text, {"screen": "summary", "await": "done"})
            return
        _show_menu(path, data, catalog)
        return
    if key in ("menu", "back to the menu"):
        _show_menu(path, data, catalog)
        return
    screen_saved = session.get("screen") or {}
    asked = " ".join(texts).strip() if texts else ""
    explain_name = _idea_name(live, {}) if live else (screen_saved.get("name") or "")
    explain_def = ""
    if live:
        explain_def = live.get("definition") or ""
    else:
        explain_def = screen_saved.get("definition") or screen_saved.get("explain") or ""
    if key in ("explain", "another angle", "explain it a different way") or (
        explain_name and not live and key not in NAV and _is_request(asked or action)
    ):
        if not explain_name:
            _show_menu(path, data, catalog)
            return
        _show_explain(path, data, explain_name, explain_def)
        return
    if key in ("why", "show me"):
        screen = session.get("screen") or {}
        phylum = screen.get("phylum") or "axiom"
        row = next(item for item in _rows(data, catalog) if item["phylum"] == phylum)
        text = render.feedback_strong(
            "One more pass at the same stake.",
            screen.get("reached") or screen.get("name") or "the idea",
            screen.get("definition") or screen.get("deeper") or "Say what it changes here.",
            phylum,
            row["strong"],
            row["partial"],
            row["total"] or 1,
            typed=_is_typed(data),
        )
        emit(path, data, text, {"screen": "why", "await": "next", "name": screen.get("name")})
        return
    result = key if key in RESULTS else ""
    if key == "skip":
        result = "miss"
    if key == "idk" and not live:
        screen = session.get("screen") or {}
        if screen.get("name"):
            definition = screen.get("definition") or screen.get("explain") or ""
            text = _reveal_text(screen.get("name") or "", definition, _is_typed(data))
            reminder = REMIND_IDK if definition else REMIND_IDK_OPEN
            question = _question_line("idk", screen.get("name") or "", definition)
            emit(path, data, text, {"screen": "idk", "await": "next", "name": screen.get("name")}, reminder, question)
            return
        _show_menu(path, data, catalog)
        return
    if live and key.isdigit() and (live.get("options") or []):
        options = live.get("options") or []
        number = int(key)
        chosen = None
        for index, item in enumerate(options, start=1):
            if int(item.get("n") or index) == number:
                chosen = item
                break
        result = "strong" if chosen and chosen.get("id") in (live.get("entry_ids") or []) else "miss"
        _grade(path, data, result, live)
        return
    if live and result:
        _grade(path, data, result, live)
        return
    if live and (key == "hint" or _is_request(asked or action)):
        _show_hint(path, data, live)
        return
    if live and key not in NAV and not _is_next(key):
        _show_card(path, data, _held(live))
        if key or texts:
            _err("use strong partial miss or idk")
        return
    entry_id = None
    if key == "deal":
        entry_id = _deal_id(texts)
        if entry_id is None or entry_id == "":
            _show_menu(path, data, catalog)
            _err("no idea under that name" if entry_id == "" else "need an idea id")
            return
    lane = _lane_phylum(action) if action and key != "deal" else None
    if key == "deal" or _is_next(key) or key in ("daily", "spot", "surprise", "surprise me", "random") or lane:
        spec = _spec_for(key if key != "deal" else "next", lane, entry_id, session)
        _deal_and_show(path, data, spec)
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
    _err("commands are in references/commands.md")
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
    turn.add_argument("--typed", action="store_true")
    show.add_argument("--typed", action="store_true")
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
