"""Checks for the ida library, renderer, and progress file.

    python3 skills/ida/scripts/test_ida.py
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import build_library  # noqa: E402
import render  # noqa: E402
from catalog import load_catalog  # noqa: E402
from common import LIBRARY, ROOT, TAIL_LINE, TAIL_LINES

_ANSI = re.compile(r"\x1b\[[0-9;]*m")


def visible_glyphs(line: str) -> str:
    """Glyphs a terminal would draw. Conceal codes, blanks, and whitespace do not count."""
    cleaned = _ANSI.sub("", line)
    kept = []
    for ch in cleaned:
        if ch == "\u2800":
            continue
        if unicodedata.category(ch)[0] in ("C", "Z"):
            continue
        kept.append(ch)
    return "".join(kept)


def assert_blank_tail(test: unittest.TestCase, text: str) -> None:
    lines = text.splitlines()
    test.assertGreaterEqual(len(lines), TAIL_LINES)
    for line in lines[-TAIL_LINES:]:
        test.assertEqual(line, TAIL_LINE)
        test.assertEqual(visible_glyphs(line), "")
        test.assertIn("\u2800", line)


def screen_body(stdout: str) -> str:
    start = stdout.index("BEGIN\n") + len("BEGIN\n")
    end = stdout.index("\nEND")
    return stdout[start:end]  # noqa: E402

REPO = ROOT.parents[1]
EM = "\u2014"
PY = sys.executable


def run(script: str, args: list[str], path: Path, stdin: str | None = None, env=None):
    merged = os.environ.copy()
    merged["IDA_PROGRESS"] = str(path)
    if env:
        merged.update(env)
    return subprocess.run(
        [PY, str(SCRIPTS / script), "--path", str(path), *args] if script == "progress.py" else [PY, str(SCRIPTS / script), *args],
        input=stdin,
        text=True,
        capture_output=True,
        env=merged,
        check=False,
    )


class LibraryTests(unittest.TestCase):
    def test_rebuild_matches_committed_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            summary = build_library.build(LIBRARY / "ida-library.csv", out)
            self.assertEqual(summary["entries"], 443)
            self.assertEqual(summary["phyla"], 7)
            self.assertEqual(summary["categories"], 52)
            self.assertEqual(summary["placements"], 53)
            self.assertEqual(summary["authored"], 7)
            for name in ("phyla.json", "exemplars.json"):
                self.assertEqual((out / name).read_text(encoding="utf-8"), (LIBRARY / name).read_text(encoding="utf-8"))
            for path in sorted((LIBRARY / "index").glob("*.json")):
                self.assertEqual((out / "index" / path.name).read_text(encoding="utf-8"), path.read_text(encoding="utf-8"))

    def test_practice_flags_and_exemplars(self):
        _doc, catalog = load_catalog()
        by_id = {entry["id"]: entry for entry in catalog}
        self.assertEqual(by_id["tautology"]["practice"], "spot")
        self.assertEqual(by_id["conjunction"]["practice"], "spot")
        self.assertEqual(by_id["false-positive"]["practice"], "decide")
        self.assertEqual(by_id["central-limit-theorem"]["practice"], "spot")
        self.assertEqual(by_id["occams-razor"]["practice"], "decide")
        self.assertEqual(by_id["inversion"]["practice"], "decide")
        self.assertEqual(by_id["monty-hall-problem"]["practice"], "spot")
        exemplars = json.loads((LIBRARY / "exemplars.json").read_text(encoding="utf-8"))
        ids = [entry["id"] for entry in exemplars["entries"]]
        self.assertEqual(ids, build_library.AUTHORED_ORDER)
        for entry in exemplars["entries"]:
            self.assertTrue(entry["law"])
            self.assertTrue(entry["notes"])
            self.assertNotIn(EM, entry["law"] + entry["notes"] + entry["attribution"])
        inversion = next(entry for entry in exemplars["entries"] if entry["id"] == "inversion")
        self.assertIn("fail at it, then refuse", inversion["law"])
        raw = (LIBRARY / "ida-library.csv").read_text(encoding="utf-8")
        self.assertIn(EM, raw)
        index = json.loads((LIBRARY / "index" / "axiom.json").read_text(encoding="utf-8"))
        self.assertNotIn("law", index["entries"][0])
        phyla = json.loads((LIBRARY / "phyla.json").read_text(encoding="utf-8"))
        homes = [item["id"] for item in phyla["phyla"] for cat in item["categories"] if cat["name"] == "reasoning tools"]
        self.assertEqual(homes, ["axiom", "momentum"])


class RenderTests(unittest.TestCase):
    def test_cards_stay_within_54_and_end_on_a_prompt(self):
        for phylum in render.DISPLAY_ORDER:
            for practice in ("decide", "spot"):
                text = render.card(4, phylum, "A short scene with a real stake.", practice=practice)
                self.assertTrue(all(len(line) <= 76 for line in text.splitlines()), text)
                self.assertNotIn("›", text)
                self.assertNotIn("type your answer", text)
                self.assertIn("T H E   Q U E S T I O N", text)
                typed = render.card(4, phylum, "A short scene with a real stake.", practice=practice, typed=True)
                self.assertNotIn("›", typed)
                self.assertNotIn("type your answer", typed)
                self.assertNotIn("✓", text)
                self.assertIn(render.spaced(render.display_name(phylum)), text)
                self.assertIn("┃", text)
        long_name = "commutative / associative / distributive laws"
        text = render.card(
            8,
            "axiom",
            "A long label has to wrap inside the card.",
            practice="spot",
            mode="choice",
            options=[long_name, "tautology", "contradiction", "validity"],
        )
        self.assertTrue(all(len(line) <= 76 for line in text.splitlines()))
        self.assertIn("commutative", text)
        self.assertIn("T H E   Q U E S T I O N", text)
        self.assertIn("Which one fits?", text)
        self.assertNotIn("Clarity is a competitive edge.", text)

    def test_card_includes_the_question(self):
        free = render.card(2, "strategy", "A seed-stage startup offers you a role.")
        self.assertIn("T H E   Q U E S T I O N", free)
        self.assertIn("Which way of thinking fits here?", free)
        self.assertNotIn("type your answer", free)
        self.assertNotIn("›", free)
        self.assertTrue(free.strip().endswith("two."))
        self.assertIn("A seed-stage startup offers you a role.", free)
        choice = render.card(
            1,
            "bias",
            "They quote the customers who stayed.",
            mode="choice",
            options=["survivorship bias", "confirmation bias", "sunk cost", "anchoring"],
        )
        self.assertIn("T H E   Q U E S T I O N", choice)
        self.assertIn("Which one fits?", choice)
        for name in ("survivorship bias", "confirmation bias", "sunk cost", "anchoring"):
            self.assertIn(name, choice)
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("A free-text card, and a profile question, end the reply.", skill)
        self.assertNotIn("idk / hint / skip on a free-text card", skill)

    def test_bars_are_ten_cells_and_partials_are_half(self):
        empty, pct = render.bar_cells(0, 0, 81)
        self.assertEqual(empty, "░" * 20)
        self.assertEqual(pct, 0)
        full, pct = render.bar_cells(81, 0, 81)
        self.assertEqual(full, "█" * 20)
        self.assertEqual(pct, 100)
        one, pct = render.bar_cells(1, 0, 81)
        self.assertEqual(len(one), 20)
        self.assertEqual(one, "▒" + "░" * 19)
        self.assertEqual(pct, 1)
        half, pct = render.bar_cells(0, 1, 81)
        self.assertEqual(half[0], "▒")
        self.assertNotIn("█", half)
        self.assertEqual(pct, 1)
        mixed, pct = render.bar_cells(8, 1, 10)
        self.assertEqual(mixed, "█" * 17 + "░" * 3)
        self.assertEqual(pct, 85)
        untouched, pct = render.bar_cells(0, 0, 62)
        self.assertEqual(set(untouched), {"░"})
        self.assertEqual(pct, 0)
        lines = [render.lane_lines(phylum, 8, 0, 40)[1] for phylum in render.DISPLAY_ORDER]
        self.assertEqual(len({len(line) for line in lines}), 1)
        self.assertEqual(len({line.index("█") for line in lines}), 1)
        self.assertTrue(all(len(line) <= 76 for line in lines))
        fresh = [render.bar_line(phylum, 0, 0, 10) for phylum in render.DISPLAY_ORDER]
        self.assertTrue(all(line.splitlines()[-1].endswith(" new") for line in fresh))
        self.assertEqual(len({line.splitlines()[-1].index("░") for line in fresh}), 1)
        one = render.bar_line("strategy", 1, 0, 81)
        self.assertIn("1%", one)
        self.assertIn("▒", one)
        self.assertNotIn("1/81", one)
        screen = render.bars(
            [{"phylum": phylum, "strong": 1, "partial": 0, "total": 81} for phylum in render.DISPLAY_ORDER]
        )
        self.assertTrue(all(len(line) <= 76 for line in screen.splitlines()))
        self.assertNotIn("1/81", screen)
        self.assertNotIn("axiom", screen)
        self.assertIn("1%", screen)

    def test_section_names(self):
        self.assertEqual(
            [render.display_name(phylum) for phylum in render.DISPLAY_ORDER],
            [
                "thinking clearly",
                "knowing what's true",
                "blind spots",
                "reading people",
                "playing to win",
                "seeing ripple effects",
                "deciding and acting",
            ],
        )
        menu = render.menu(4)
        self.assertIn("P L A Y I N G   T O   W I N", menu)
        self.assertNotIn("PLAYING TO WIN", menu)
        self.assertNotIn("how to win", menu)
        self.assertNotIn("axiom", menu)
        self.assertNotIn("When it gets noisy", menu)
        self.assertNotIn("Clarity is a competitive edge.", menu)
        opening = render.opening_new()
        self.assertIn("When it gets noisy,", opening)
        self.assertIn("you can always reach for clarity.", opening)
        self.assertIn("01 / 03", opening)
        self.assertIn("█", opening)
        self.assertNotIn("NO. 001", opening)
        self.assertNotIn("Clarity is a competitive edge.", opening)
        self.assertNotIn("The people who see clearly win.", opening)
        later = render.opening(3)
        self.assertIn("03 / 03", later)
        self.assertNotIn("When it gets noisy,", later)
        self.assertEqual(
            render.SIGNOFFS if hasattr(render, "SIGNOFFS") else __import__("common").SIGNOFFS,
            (
                "Clarity is a competitive edge.",
                "The people who see clearly win.",
            ),
        )

    def test_samples_live_in_the_docs(self):
        card = render.card(
            2,
            "strategy",
            "A seed-stage startup offers you a role. The equity is generous, the salary is 30% lower, and the founder says they'll raise in six months.",
        )
        strong = render.feedback_strong(
            "You asked what happens if the raise doesn't come, and you priced the downside before the upside. That's the move.",
            "downside first, base rates",
            "most seed rounds slip, so plan for 12 months, not 6",
            "strategy",
            3,
            1,
            81,
        )
        partial = render.feedback_partial(
            "the meeting place",
            "what each side expects the other to expect",
            "Say the place, then say why both would pick it.",
            "strategy",
            0,
            1,
            81,
        )
        not_yet = render.feedback_not_yet(
            "inversion",
            "to master a problem, study how to fail at it, then refuse to.",
        )
        bars = render.bars(
            [
                {"phylum": "axiom", "strong": 0, "partial": 0, "total": 103},
                {"phylum": "strategy", "strong": 1, "partial": 0, "total": 81},
            ]
        )
        rows = [
            {"phylum": "axiom", "strong": 1, "partial": 0, "total": 103},
            {"phylum": "kanon", "strong": 0, "partial": 0, "total": 31},
            {"phylum": "bias", "strong": 0, "partial": 1, "total": 62},
            {"phylum": "persona", "strong": 0, "partial": 0, "total": 71},
            {"phylum": "strategy", "strong": 3, "partial": 1, "total": 81},
            {"phylum": "systema", "strong": 0, "partial": 0, "total": 53},
            {"phylum": "momentum", "strong": 0, "partial": 0, "total": 42},
        ]
        summary = render.summary_block(
            5,
            3,
            1,
            0,
            1,
            "downside first",
            "",
            "",
            session=4,
            date="12 NOV 2026",
            reached=["downside first", "base rates"],
            carry="Price the bad case before you fall for the good one.",
            signoff_index=0,
            rows=rows,
        )
        other = render.summary_block(
            5,
            3,
            1,
            0,
            1,
            "downside first",
            "",
            "",
            session=5,
            date="12 NOV 2026",
            reached=["downside first"],
            carry="Name the idea, then say what it changes here.",
            signoff_index=1,
            rows=rows,
        )
        guide = (ROOT / "references" / "format.md").read_text(encoding="utf-8")
        for block in (card, strong, partial, not_yet, bars, summary, other, render.opening(1), render.opening(2), render.menu(4)):
            self.assertIn(block, guide)
        for phylum, name in render.DISPLAY_NAMES.items():
            self.assertIn(name, guide)
            self.assertIn(phylum, guide)
        self.assertIn("Clarity is a competitive edge.", summary)
        self.assertIn("The people who see clearly win.", other)
        transcripts = (ROOT / "examples" / "transcripts.md").read_text(encoding="utf-8")
        for block in (render.opening(1), render.opening(2), render.menu(4), card, strong, partial, not_yet, summary):
            self.assertIn(block, transcripts)
        self.assertIn(render.opening(1), (REPO / "README.md").read_text(encoding="utf-8"))

    def test_opening_and_summary_edges(self):
        opening = render.opening_new()
        self.assertNotIn("pick a lane", opening)
        self.assertLessEqual(max(len(line) for line in opening.splitlines()), 76)
        quiet = render.summary_block(0, 0, 0, 0, 0, "", "", "pick up wherever you like")
        self.assertIn("0 cards", quiet)
        self.assertIn("Clarity is a competitive edge.", quiet)
        self.assertLessEqual(max(len(line) for line in quiet.splitlines()), 76)
        text = render.feedback("idk", "inversion", "Study the failure, then refuse it.")
        self.assertIn("not yet", text.splitlines()[0])
        self.assertNotIn("✓", text)
        self.assertTrue(all(len(line) <= 76 for line in text.splitlines()))

    def test_spacer_lines_survive_and_profile_has_no_prompt(self):
        from common import SPACER

        opening = render.opening(1).splitlines()
        self.assertNotIn("", opening)
        self.assertIn(SPACER, opening)
        tagline = opening.index("  you can always reach for clarity.")
        self.assertEqual(opening[tagline + 1], SPACER)
        self.assertEqual(opening[tagline + 2], SPACER)
        self.assertTrue(opening[tagline + 3].startswith("  ■"))
        self.assertIn("01 / 03", opening[tagline + 3])
        self.assertEqual(opening[tagline + 4], SPACER)
        self.assertEqual(opening[tagline + 5], SPACER)
        self.assertTrue(any(ch in "█▀▄" for ch in opening[tagline + 6]))
        self.assertNotIn("›", render.opening(1))
        self._status_strip_fits()

    def _status_strip_fits(self):
        from common import SPACER
        from progress import card_streak

        sample = render.status_strip(6, 63, 2, 5, 3)
        self.assertEqual(sample, "lane  ■■□□□□□□□□□□□□□□  6 / 63 ways      today  ●●○○○      streak 3d")
        self.assertLessEqual(len(sample), 72)
        self.assertIn("streak 1d", render.status_strip(0, 10, 1, None, 1))
        self.assertNotIn("streak", render.status_strip(0, 10, 1, None, 0))
        self.assertNotIn("○", render.status_strip(0, 10, 2, None, 1))
        self.assertIn("●●○○○", render.status_strip(1, 10, 2, 5, 1))
        wide = render.status_strip(999, 999, 99, 99, 999)
        self.assertLessEqual(len(wide), 72)
        self.assertIn("999 / 999 ways", wide)
        header = render.card(
            2,
            "axiom",
            "A founder pitches you for a check.",
            total=5,
            status={"lane_done": 6, "lane_total": 63, "reached": 2, "session_total": 5, "streak": 3},
        )
        self.assertIn("CARD 2 / 5", header)
        self.assertIn(sample, header)
        open_ended = render.card(2, "axiom", "A short scene.", status={"lane_done": 0, "lane_total": 10, "reached": 2, "session_total": None, "streak": 1})
        self.assertIn("CARD 2\n", open_ended)
        self.assertNotIn("CARD 2 /", open_ended)
        for phylum in render.DISPLAY_ORDER:
            titled = render.card(
                999,
                phylum,
                "x",
                total=999,
                status={"lane_done": 999, "lane_total": 999, "reached": 99, "session_total": 99, "streak": 999},
            )
            self.assertTrue(all(len(line) <= 76 for line in titled.splitlines()))
        days = {
            "recent_scenarios": [
                {"at": "2026-11-10T12:00:00Z"},
                {"at": "2026-11-12T12:00:00Z"},
            ],
            "history": [{"started_at": "2026-11-11T08:00:00Z", "scenarios": 1}],
            "session": None,
        }
        self.assertEqual(card_streak(days, "2026-11-12"), 3)
        self.assertEqual(card_streak(days, "2026-11-13"), 3)
        self.assertEqual(card_streak(days, "2026-11-14"), 0)
        guide = (ROOT / "references" / "format.md").read_text(encoding="utf-8")
        transcripts = (ROOT / "examples" / "transcripts.md").read_text(encoding="utf-8")
        self.assertIn(sample, guide)
        self.assertIn(sample, transcripts)
        self.assertNotIn("›", render.opening(2))
        self.assertNotIn("your own words", render.opening(1))
        card = render.card(1, "bias", "A short scene with a real stake.")
        self.assertNotIn("your own words", card)
        self.assertNotIn("type your answer", card)
        self.assertNotIn("›", card)
        typed_card = render.card(1, "bias", "A short scene with a real stake.", typed=True)
        self.assertNotIn("type your answer", typed_card)
        self.assertNotIn("›", typed_card)
        self.assertTrue(typed_card.rstrip().endswith("two."))
        self.assertNotIn("›", render.menu(4))
        self.assertIn("›", render.menu(4, typed=True))
        angle = render.another_angle(
            "A sentence true either way says nothing.",
            "Like saying the bus is on time or it is not.",
            "The launch line did not tell you whether to ship.",
        )
        self.assertIn("A N O T H E R   A N G L E", angle)
        self.assertNotIn("›", angle)
        self.assertNotIn("Clearer now", angle)
        self.assertTrue(all(len(line) <= 76 for line in angle.splitlines()))
        self.assertIn(angle, (ROOT / "references" / "format.md").read_text(encoding="utf-8"))
        self.assertIn(angle, (ROOT / "examples" / "transcripts.md").read_text(encoding="utf-8"))
        for block in (
            render.opening(1),
            render.menu(4),
            card,
            render.feedback_strong("You saw it.", "inversion", "one step further", "bias", 1, 0, 62),
            render.summary_block(1, 1, 0, 0, 0, "inversion", "", "", carry="Keep the name."),
        ):
            self.assertIn(SPACER, block.splitlines())
            self.assertNotIn("", block.splitlines())


class ProgressTests(unittest.TestCase):
    def test_session_flow(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "progress.json"
            first = run("progress.py", ["load"], path)
            self.assertEqual(first.returncode, 0, first.stderr)
            view = json.loads(first.stdout)
            self.assertEqual(view["welcome"]["kind"], "new")
            self.assertEqual(len(view["bars"]), 7)
            stored = json.loads(path.read_text(encoding="utf-8"))
            self.assertNotIn("welcome", stored)
            self.assertEqual(stored["version"], 2)

            saved = run(
                "progress.py",
                ["save-profile", "--role", "product designer", "--interests", "climbing"],
                path,
            )
            self.assertEqual(saved.returncode, 0, saved.stderr)
            kept = run("progress.py", ["save-profile", "--decisions", "what to ship"], path)
            profile = json.loads(kept.stdout)["profile"]
            self.assertEqual(profile["role"], "product designer")
            self.assertEqual(profile["decisions"], "what to ship")

            started = run(
                "progress.py",
                ["start", "--selection", "section", "--phylum", "Strategy", "--category", "game theory"],
                path,
            )
            self.assertEqual(started.returncode, 0, started.stderr)
            session = json.loads(started.stdout)["session"]
            self.assertEqual(session["phylum"], "strategy")

            live = {
                "number": 1,
                "practice": "decide",
                "phylum": "strategy",
                "category": "game theory",
                "entry_ids": ["schelling-point"],
                "prompt": "Meet at the usual lot \u2014 phones are dead.",
                "mode": "free",
                "options": [],
            }
            shown = run("progress.py", ["save"], path, json.dumps({"in_progress": live}))
            self.assertEqual(shown.returncode, 0, shown.stderr)
            view = json.loads(shown.stdout)
            self.assertEqual(view["welcome"]["kind"], "resume")
            self.assertEqual(view["session"]["counts"]["strong"], 0)
            self.assertNotIn(EM, view["session"]["in_progress"]["prompt"])
            blocked = run("progress.py", ["save"], path, json.dumps({"counts": {"strong": 9}}))
            self.assertNotEqual(blocked.returncode, 0)

            partial = run(
                "progress.py",
                ["record"],
                path,
                json.dumps(
                    {
                        "session_result": "partial",
                        "updates": [{"id": "schelling-point", "result": "partial"}],
                        "summary": "meet with phones dead",
                    }
                ),
            )
            self.assertEqual(partial.returncode, 0, partial.stderr)
            bars = {row["phylum"]: row for row in json.loads(partial.stdout)["bars"]}
            self.assertEqual(bars["strategy"]["well"], 0)

            # A second card, then idk, then a real strong.
            again = {
                "number": 2,
                "practice": "decide",
                "phylum": "strategy",
                "category": "game theory",
                "entry_ids": ["nash-equilibrium"],
                "prompt": "A price cut neither of you can afford.",
                "mode": "free",
            }
            self.assertEqual(run("progress.py", ["save"], path, json.dumps({"in_progress": again})).returncode, 0)
            idk = run(
                "progress.py",
                ["record"],
                path,
                json.dumps(
                    {
                        "session_result": "idk",
                        "updates": [{"id": "nash-equilibrium", "result": "idk"}],
                        "summary": "a price cut neither can afford",
                    }
                ),
            )
            stats = json.loads(idk.stdout)
            self.assertEqual(stats["session"]["counts"]["idk"], 1)
            self.assertEqual(stats["session"]["counts"]["miss"], 0)
            nash = stats["entries"]["nash-equilibrium"]
            self.assertEqual(nash["idk"], 1)
            self.assertEqual(nash["miss"], 0)

            strong_card = {
                "number": 3,
                "practice": "decide",
                "phylum": "strategy",
                "category": "game theory",
                "entry_ids": ["tit-for-tat"],
                "prompt": "They undercut you once.",
                "mode": "choice",
                "options": [{"id": "tit-for-tat", "name": "tit-for-tat"}],
            }
            self.assertEqual(run("progress.py", ["save"], path, json.dumps({"in_progress": strong_card})).returncode, 0)
            strong = run(
                "progress.py",
                ["record"],
                path,
                json.dumps(
                    {
                        "session_result": "strong",
                        "updates": [{"id": "tit-for-tat", "result": "strong"}],
                        "summary": "they undercut you once",
                    }
                ),
            )
            after = json.loads(strong.stdout)
            self.assertEqual(after["section_bars"][0]["label"], "game theory")
            self.assertEqual(after["section_bars"][0]["well"], 1)
            ended = run("progress.py", ["end"], path)
            self.assertEqual(ended.returncode, 0, ended.stderr)
            summary = json.loads(ended.stdout)["summary"]
            self.assertEqual(summary["scenarios"], 3)
            self.assertEqual(summary["strong"], 1)
            self.assertEqual(summary["idk"], 1)
            self.assertEqual(summary["sharpest"], "tit-for-tat")
            self.assertEqual(summary["revisit"], "nash equilibrium")
            self.assertEqual(summary["next"], "pick up in game theory")
            back = json.loads(run("progress.py", ["load"], path).stdout)
            self.assertIsNone(back["session"])
            self.assertEqual(back["welcome"]["line"], "Last time: playing to win, 3 scenarios.")
            self.assertEqual(back["entries"]["tit-for-tat"]["strong"], 1)

            # One strong, then end, is a singular welcome. Use a fresh sitting.
            run("progress.py", ["start", "--selection", "random", "--mode", "free"], path)
            solo = {
                "number": 1,
                "practice": "spot",
                "phylum": "axiom",
                "entry_ids": ["tautology"],
                "prompt": "Either it ships or it does not.",
                "mode": "free",
            }
            run("progress.py", ["save"], path, json.dumps({"in_progress": solo}))
            run(
                "progress.py",
                ["record"],
                path,
                json.dumps(
                    {
                        "session_result": "strong",
                        "updates": [{"id": "tautology", "result": "strong"}],
                        "summary": "a sentence true either way",
                    }
                ),
            )
            run("progress.py", ["end"], path)
            solo_view = json.loads(run("progress.py", ["load"], path).stdout)
            self.assertIn("1 scenario", solo_view["welcome"]["line"])

    def test_refuses_bad_version_and_open_card(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "progress.json"
            path.write_text('{"version": 9}\n', encoding="utf-8")
            bad = run("progress.py", ["load"], path)
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("not supported", bad.stderr)
            path.unlink()
            run("progress.py", ["load"], path)
            run("progress.py", ["start", "--selection", "section", "--phylum", "bias"], path)
            live = {
                "number": 1,
                "practice": "decide",
                "phylum": "bias",
                "entry_ids": ["confirmation-bias"],
                "prompt": "You only read the agreeing comments.",
                "mode": "free",
            }
            run("progress.py", ["save"], path, json.dumps({"in_progress": live}))
            refused = run("progress.py", ["start", "--selection", "random"], path)
            self.assertNotEqual(refused.returncode, 0)
            unknown = run("progress.py", ["start", "--selection", "section", "--phylum", "foundations", "--fresh"], path)
            self.assertNotEqual(unknown.returncode, 0)


class PickTests(unittest.TestCase):
    def test_names_and_filters(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "progress.json"
            named = subprocess.run(
                [PY, str(SCRIPTS / "pick.py"), "--names", "goodhart, inversion, not a thing", "--seed", "2", "--progress", str(path)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(named.returncode, 0, named.stderr)
            payload = json.loads(named.stdout)
            self.assertEqual(payload["queue"], ["goodharts-law", "inversion"])
            self.assertEqual(payload["unmatched"][0]["query"], "not a thing")
            fud = subprocess.run(
                [PY, str(SCRIPTS / "pick.py"), "--name", "fud", "--seed", "1", "--progress", str(path)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(json.loads(fud.stdout)["intended"][0]["id"], "fear-uncertainty-and-doubt")
            vague = subprocess.run(
                [PY, str(SCRIPTS / "pick.py"), "--name", "law", "--seed", "1", "--progress", str(path)],
                text=True,
                capture_output=True,
                check=False,
            )
            vague_payload = json.loads(vague.stdout)
            self.assertNotIn("intended", vague_payload)
            self.assertTrue(vague_payload["unmatched"])

    def test_avoids_recent_and_leans_on_misses(self):
        _doc, catalog = load_catalog()
        operators = [entry for entry in catalog if entry["category"] == "logical operators"]
        held = operators[0]
        recent = [{"entry_ids": [entry["id"]], "summary": "x"} for entry in operators[1:]]
        games = [entry for entry in catalog if entry["phylum"] == "strategy" and entry["category"] == "game theory"]
        untouched = games[0]
        stats = {
            entry["id"]: {"attempts": 2, "strong": 2, "partial": 0, "miss": 0, "idk": 0, "name": entry["name"]}
            for entry in games[1:]
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "progress.json"
            path.write_text(
                json.dumps({"version": 1, "profile": None, "session": None, "entries": stats, "recent_scenarios": recent, "history": []}),
                encoding="utf-8",
            )
            for seed in range(1, 8):
                spot = subprocess.run(
                    [
                        PY,
                        str(SCRIPTS / "pick.py"),
                        "--phylum",
                        "axiom",
                        "--category",
                        "logical operators",
                        "--pair",
                        "no",
                        "--seed",
                        str(seed),
                        "--progress",
                        str(path),
                    ],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(json.loads(spot.stdout)["intended"][0]["id"], held["id"])
                leaned = subprocess.run(
                    [
                        PY,
                        str(SCRIPTS / "pick.py"),
                        "--phylum",
                        "strategy",
                        "--category",
                        "game theory",
                        "--pair",
                        "no",
                        "--seed",
                        str(seed),
                        "--progress",
                        str(path),
                    ],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(json.loads(leaned.stdout)["intended"][0]["id"], untouched["id"])
            paired = subprocess.run(
                [
                    PY,
                    str(SCRIPTS / "pick.py"),
                    "--phylum",
                    "strategy",
                    "--category",
                    "game theory",
                    "--pair",
                    "yes",
                    "--choices",
                    "--seed",
                    "4",
                    "--progress",
                    str(path),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            body = json.loads(paired.stdout)
            self.assertEqual(len(body["intended"]), 2)
            self.assertEqual(len(body["options"]), 4)
            intended_ids = {entry["id"] for entry in body["intended"]}
            self.assertTrue(intended_ids <= {option["id"] for option in body["options"]})
            self.assertEqual({entry["category"] for entry in body["intended"]}, {"game theory"})


class IdaCommandTests(unittest.TestCase):
    def test_open_is_one_line_and_save_is_silent(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "progress.json"
            opened = subprocess.run(
                [PY, str(SCRIPTS / "ida.py"), "--path", str(path), "open"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(opened.returncode, 0, opened.stderr)
            assert_blank_tail(self, opened.stdout)
            opened_info = json.loads(opened.stdout.splitlines()[0])
            self.assertEqual(opened_info["kind"], "new")
            self.assertEqual(opened_info["bars"]["axiom"][0], 0)
            quiet = subprocess.run(
                [
                    PY,
                    str(SCRIPTS / "ida.py"),
                    "--path",
                    str(path),
                    "profile",
                    "--role",
                    "designer",
                    "--interests",
                    "climbing",
                    "--decisions",
                    "what to ship",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(quiet.returncode, 0, quiet.stderr)
            self.assertEqual(quiet.stdout, "")
            nxt = subprocess.run(
                [PY, str(SCRIPTS / "ida.py"), "--path", str(path), "next", "--phylum", "strategy", "--seed", "1"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(nxt.returncode, 0, nxt.stderr)
            assert_blank_tail(self, nxt.stdout)
            fields = json.loads(nxt.stdout.splitlines()[0])
            self.assertEqual(fields["section"], "playing to win")
            self.assertNotIn("\t", nxt.stdout)
            saved = subprocess.run(
                [
                    PY,
                    str(SCRIPTS / "ida.py"),
                    "--path",
                    str(path),
                    "save",
                    "--result",
                    "idk",
                    "--summary",
                    "a stake with no answer",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(saved.returncode, 0, saved.stderr)
            self.assertEqual(saved.stdout, "")
            again = subprocess.run(
                [PY, str(SCRIPTS / "ida.py"), "--path", str(path), "open"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(json.loads(again.stdout.splitlines()[0])["bars"]["strategy"][0], 0)
            strong = subprocess.run(
                [PY, str(SCRIPTS / "ida.py"), "--path", str(path), "next", "--phylum", "strategy", "--seed", "2"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(strong.returncode, 0, strong.stderr)
            subprocess.run(
                [
                    PY,
                    str(SCRIPTS / "ida.py"),
                    "--path",
                    str(path),
                    "save",
                    "--result",
                    "strong",
                    "--summary",
                    "a real stake",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            after = subprocess.run(
                [PY, str(SCRIPTS / "ida.py"), "--path", str(path), "open"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(json.loads(after.stdout.splitlines()[0])["bars"]["strategy"][0], 1)

    def test_turn_is_one_command_and_help_is_one_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "progress.json")
            def run(args, payload=None):
                return subprocess.run(
                    [PY, str(SCRIPTS / "ida.py"), "--path", path, *args],
                    input=json.dumps(payload) if payload is not None else None,
                    text=True,
                    capture_output=True,
                    check=False,
                )
            opening = run(["turn"])
            self.assertEqual(opening.returncode, 0, opening.stderr)
            self.assertIn("01 / 03", opening.stdout)
            self.assertIn("QUESTION: What do you do for work?", opening.stdout)
            self.assertIn("█", opening.stdout)
            self.assertIn("[ida -> agent]", opening.stdout)
            self.assertLess(opening.stdout.index("[ida -> agent]"), opening.stdout.index("BEGIN"))
            self.assertNotIn("\033", screen_body(opening.stdout))
            self.assertEqual(opening.stderr, "")
            assert_blank_tail(self, opening.stdout)
            run(["turn", "designer"])
            run(["turn", "climbing"])
            menu = run(["turn", "what to ship"])
            self.assertIn("pick a lane", menu.stdout)
            self.assertIn("THEN call the choice tool.", menu.stdout)
            self.assertIn("Lanes are the seven kinds of thinking ida trains.", menu.stdout)
            self.assertIn("thinking clearly: reason without fooling yourself (new, suggested)", menu.stdout)
            self.assertIn("daily: one card picked for today", menu.stdout)
            self.assertIn("surprise me: ida picks the idea", menu.stdout)
            assert_blank_tail(self, menu.stdout)
            deal = "sh ~/.agents/skills/ida/ida turn deal inversion"
            self.assertLessEqual(len(deal), 48)
            card = run(["turn", "deal", "inversion"])
            self.assertEqual(card.returncode, 0, card.stderr)
            self.assertEqual(card.stderr.splitlines()[0], "inversion")
            assert_blank_tail(self, card.stderr)
            self.assertIn("Replace the word SCENE", card.stdout)
            self.assertIn("SCENE", screen_body(card.stdout))
            self.assertIn("streak 1d", card.stdout)
            self.assertIn(" ways", card.stdout)
            self.assertIn("today", card.stdout)
            self.assertNotIn("CARD 1 /", card.stdout)
            self.assertIn("T H E   Q U E S T I O N", card.stdout)
            self.assertNotIn("study how to fail", card.stdout.lower())
            reveal = run(["turn", "idk"], {"explain": "FROM STDIN"})
            self.assertEqual(reveal.returncode, 0, reveal.stderr)
            self.assertIn("█", reveal.stdout)
            self.assertIn("not yet", reveal.stdout)
            self.assertIn("study how to fail", reveal.stdout.lower())
            self.assertNotIn("H O W   T O   A P P L Y", reveal.stdout)
            self.assertNotIn("FROM STDIN", reveal.stdout)
            self.assertIn("THEN call the choice tool.", reveal.stdout)
            self.assertIn("QUESTION_BANNER: block", reveal.stdout)
            self.assertIn("In your scene: <one sentence on this scene>.", reveal.stdout)
            self.assertIn("━" * 64, reveal.stdout)
            self.assertIn("To master a problem, study how to fail at it, then refuse to.", reveal.stdout)
            self.assertLess(reveal.stdout.index("\nEND"), reveal.stdout.index("\nQUESTION:"))
            explained = run(["turn", "explain"])
            self.assertIn("In plain words: To master a problem", explained.stdout)
            self.assertIn("In your scene: <one sentence on this scene>.", explained.stdout)
            self.assertIn("━" * 64, explained.stdout)
            self.assertIn("<everyday comparison>", explained.stdout)
            self.assertIn("<3 short steps>", explained.stdout)
            asked = run(["turn", "Can you break this down for me even more, please?"])
            self.assertIn("In plain words:", asked.stdout)
            self.assertNotIn("use strong", asked.stderr)
            self.assertLess(reveal.stdout.index("BEGIN"), reveal.stdout.index("not yet"))
            self.assertLess(reveal.stdout.index("not yet"), reveal.stdout.index("\nEND"))
            self.assertNotIn("\033", screen_body(reveal.stdout))
            self.assertNotIn("{", reveal.stderr)
            self.assertIn("three steps", reveal.stderr)
            assert_blank_tail(self, reveal.stdout)
            assert_blank_tail(self, reveal.stderr)
            helped = run(["show", "card", "--help"])
            self.assertNotEqual(helped.returncode, 0)
            self.assertEqual(helped.stderr.splitlines()[0], "commands are in references/commands.md")
            assert_blank_tail(self, helped.stderr)
            self.assertEqual(helped.stdout, "")
            typed = run(["turn", "--typed"])
            self.assertIn("›", typed.stdout)
            remembered = run(["turn", "menu"])
            self.assertIn("›", remembered.stdout)


class ShimTests(unittest.TestCase):
    def test_one_command_and_shim_accepts_python(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("sh ~/.agents/skills/ida/ida turn", skill)
        self.assertIn("The choice tool question MUST be the exact string printed after `QUESTION:`.", skill)
        self.assertLess(skill.index("## idk"), skill.index("## Language"))
        self.assertIn("## Golden rule", skill)
        self.assertIn("Command output is invisible to the user.", skill)
        self.assertLess(skill.index("## Golden rule"), skill.index("## Language"))
        self.assertIn("braille blanks", (ROOT / "references" / "commands.md").read_text(encoding="utf-8"))
        self.assertIn("heredoc", skill)
        self.assertIn("file-edit", skill)
        self.assertNotIn("/tmp/ida-screen.json", skill)
        self.assertNotIn("command -v", skill)
        self.assertNotIn("||", skill)
        self.assertNotIn("&&", skill)
        for line in skill.splitlines():
            stripped = line.strip()
            if stripped.startswith("sh ~/.agents/skills/ida/ida "):
                self.assertLessEqual(len(stripped), 48, stripped)
                self.assertNotIn(" the ", stripped)
        commands = (ROOT / "references" / "commands.md").read_text(encoding="utf-8")
        self.assertIn("heredoc", commands)
        self.assertIn("Do not pipe stdin.", commands)
        self.assertNotIn("/tmp/ida-screen.json", commands)
        checklist = (ROOT / "evals" / "checklist.md").read_text(encoding="utf-8")
        self.assertIn("no chained fallbacks", checklist)
        self.assertIn("command -v", checklist)
        self.assertIn("No temp file.", checklist)
        shim = ROOT / "ida"
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["IDA_PROGRESS"] = str(Path(tmp) / "progress.json")
            env.pop("IDA_COLOR", None)
            for argv in (["sh", str(shim), "turn"], [PY, str(shim), "turn"]):
                proc = subprocess.run(argv, text=True, capture_output=True, env=env, check=False)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertIn("01 / 03", proc.stdout)
                self.assertNotIn("SyntaxError", proc.stderr)
                self.assertNotIn("Traceback", proc.stderr)
                self.assertEqual(proc.stderr, "")
                assert_blank_tail(self, proc.stdout)
                self.assertEqual(visible_glyphs(proc.stdout.splitlines()[-1]), "")
                self.assertIn("01 / 03", proc.stdout)


class IdaRevealTests(unittest.TestCase):
    def test_turn_idk_prints_the_saved_name(self):
        from banner import render_name

        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["IDA_PROGRESS"] = str(Path(tmp) / "progress.json")
            env.pop("IDA_COLOR", None)
            shim = str(ROOT / "ida")

            def run(args, payload=None):
                return subprocess.run(
                    ["sh", shim, *args],
                    input=json.dumps(payload) if payload else None,
                    text=True,
                    capture_output=True,
                    env=env,
                    check=False,
                )

            run(["turn", "designer"])
            run(["turn", "climbing"])
            self.assertEqual(run(["turn", "shipping"]).returncode, 0)
            name = "inversion"
            card = run(["turn", "deal", name])
            self.assertEqual(card.returncode, 0, card.stderr)
            self.assertIn("SCENE", card.stdout)
            self.assertEqual(card.stderr.splitlines()[0], name)
            reveal = run(["turn", "idk"], {"explain": "FROM STDIN"})
            self.assertEqual(reveal.returncode, 0, reveal.stderr)
            self.assertNotIn("FROM STDIN", reveal.stdout + reveal.stderr)
            self.assertNotIn("{", reveal.stderr)
            self.assertIn("three steps", reveal.stderr.splitlines()[0])
            self.assertIn("THEN call the choice tool.", reveal.stdout)
            self.assertIn("QUESTION_BANNER: block", reveal.stdout)
            self.assertIn("In your scene: <one sentence on this scene>.", reveal.stdout)
            self.assertIn("━" * 64, reveal.stdout)
            self.assertIn("To master a problem, study how to fail at it, then refuse to.", reveal.stdout)
            self.assertLess(reveal.stdout.index("[ida -> agent]"), reveal.stdout.index("BEGIN"))
            assert_blank_tail(self, reveal.stdout)
            assert_blank_tail(self, reveal.stderr)
            self.assertIn("not yet", reveal.stdout)
            self.assertIn("study how to fail", reveal.stdout.lower())
            self.assertNotIn("H O W   T O   A P P L Y", reveal.stdout)
            self.assertLess(len(reveal.stdout.splitlines()), 48)
            for line in render_name(name):
                if line.strip(" \u200b"):
                    self.assertIn(line, reveal.stdout)
            self.assertLessEqual(max(len(line) for line in render_name(name)), 72)
            self.assertEqual(len(render_name("or")), 3)
            bare = run(["turn", "deal", "contingency"])
            self.assertEqual(bare.stderr.splitlines()[0], "contingency")
            open_reveal = run(["turn", "idk"])
            self.assertIn("no stored definition", open_reveal.stderr)
            self.assertNotIn("to master a problem", open_reveal.stdout)
            self.assertIn("QUESTION_BANNER: block", open_reveal.stdout)
            self.assertIn("In your scene: <one sentence on this scene>.", open_reveal.stdout)
            self.assertIn("<one-line definition you write>.", open_reveal.stdout)
            spaced_env = env.copy()
            spaced_env["IDA_QUESTION_BANNER"] = "spaced"
            saved_env = env.copy()
            env.clear()
            env.update(spaced_env)
            spaced = run(["turn", "idk"])
            env.clear()
            env.update(saved_env)
            self.assertIn("QUESTION_BANNER: spaced", spaced.stdout)
            self.assertIn("C O N T I N G E N C Y", spaced.stdout)
            self.assertIn("In your scene: <one sentence on this scene>.", spaced.stdout)
            self.assertIn("█", open_reveal.stdout)
            again = run(["turn", "deal", "via-negativa"])
            self.assertEqual(again.returncode, 0, again.stderr)
            answered = run(["turn", "strong"])
            self.assertIn("S T R O N G", answered.stdout)
            self.assertIn("N E G A T I V A", answered.stdout)
            self.assertIn("QUESTION: That's Via negativa. Where to from here?", answered.stdout)
            partial = run(["turn", "deal", "inversion"])
            self.assertEqual(partial.returncode, 0, partial.stderr)
            partial_grade = run(["turn", "partial"])
            self.assertIn("QUESTION: Close. The idea was Inversion. Where to from here?", partial_grade.stdout)
            missed = run(["turn", "deal", "inversion"])
            self.assertEqual(missed.returncode, 0, missed.stderr)
            miss_grade = run(["turn", "miss"])
            self.assertIn("QUESTION: The idea was Inversion. Where to from here?", miss_grade.stdout)
            assert_blank_tail(self, answered.stdout)
            self.assertEqual(answered.stderr, "")
            prose = run(["turn", "deal", "inversion"])
            ignored = run(["turn", "Cut the sections nobody reads."])
            self.assertIn("SCENE", ignored.stdout)
            self.assertNotIn("S T R O N G", ignored.stdout)
            self.assertIn("use strong partial miss or idk", ignored.stderr)
            self.assertEqual(prose.returncode, 0)


class ColorAndBannerTests(unittest.TestCase):
    def test_every_question_line_fits_the_choice_box(self):
        from ida import _idk_question

        _doc, catalog = load_catalog()
        self.assertEqual(len(catalog), 443)
        for entry in catalog:
            question = _idk_question(entry["name"], "A short definition of the idea.")
            body = question.split("QUESTION:\n", 1)[1]
            for line in body.splitlines():
                self.assertLessEqual(len(line), 64, entry["name"])
            self.assertIn("In your scene: <one sentence on this scene>.", body)
            self.assertIn("━" * 64, body)
        framed = _idk_question(
            "material conditional (→)",
            '"If P, then Q" is false only when P is true and Q is false.',
        )
        self.assertIn("  (→)", framed)
        self.assertIn("Where to from here?", framed)

    def test_every_name_fits_the_banner_width(self):
        from banner import render_name

        _doc, catalog = load_catalog()
        self.assertEqual(len(catalog), 443)
        for entry in catalog:
            for line in render_name(entry["name"]):
                self.assertLessEqual(len(line), 72, entry["name"])

    def test_color_falls_back(self):
        from color import color_mode, paint

        plain = render.opening(1)
        self.assertNotIn("\033", paint(plain, "plain"))
        colored = paint(plain, "truecolor")
        self.assertIn("\033[38;2;10;132;255m", colored)
        indexed = paint(plain, "256")
        self.assertIn("\033[38;5;", indexed)
        with tempfile.TemporaryDirectory() as tmp:
            progress = str(Path(tmp) / "progress.json")
            env = os.environ.copy()
            env["NO_COLOR"] = "1"
            env.pop("IDA_COLOR", None)
            proc = subprocess.run(
                [PY, str(SCRIPTS / "ida.py"), "--path", progress, "show", "opening"],
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            assert_blank_tail(self, proc.stdout)
            self.assertNotIn("\033", "\n".join(proc.stdout.splitlines()[:-TAIL_LINES]))
            env = os.environ.copy()
            env.pop("NO_COLOR", None)
            env["TERM"] = "dumb"
            proc = subprocess.run(
                [PY, str(SCRIPTS / "ida.py"), "--path", progress, "show", "opening"],
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )
            assert_blank_tail(self, proc.stdout)
            self.assertNotIn("\033", "\n".join(proc.stdout.splitlines()[:-TAIL_LINES]))
            env = {"PATH": os.environ.get("PATH", ""), "IDA_COLOR": "always"}
            proc = subprocess.run(
                [PY, str(SCRIPTS / "ida.py"), "--path", progress, "show", "opening"],
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("\033[38;2;", "\n".join(proc.stdout.splitlines()[:-TAIL_LINES]))
        self.assertEqual(proc.stdout.splitlines()[-TAIL_LINES:], [TAIL_LINE] * TAIL_LINES)
        self.assertFalse(proc.stdout.startswith("\n"))

    def test_version_1_progress_migrates_without_losing_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "progress.json"
            original = {
                "version": 1,
                "profile": {"role": "nurse", "interests": "climbing", "decisions": "shifts", "updated_at": "2026-01-01T00:00:00Z"},
                "session": None,
                "entries": {"inversion": {"name": "inversion", "attempts": 2, "strong": 1, "partial": 0, "miss": 0, "idk": 1, "last_practiced": "2026-01-01T00:00:00Z", "last_result": "strong"}},
                "recent_scenarios": [{"entry_ids": ["inversion"], "summary": "a launch", "result": "strong"}],
                "history": [{"scenarios": 1, "strong": 1}],
            }
            path.write_text(json.dumps(original), encoding="utf-8")
            proc = subprocess.run(
                [PY, str(SCRIPTS / "progress.py"), "--path", str(path), "load"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            stored = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(stored["version"], 2)
            self.assertEqual(stored["entries"]["inversion"]["strong"], 1)
            self.assertEqual(stored["profile"]["role"], "nurse")
            self.assertEqual(stored["recent_scenarios"][0]["summary"], "a launch")
            self.assertEqual(stored["history"][0]["scenarios"], 1)
            self.assertIn("streak", stored["practice"])


class ManifestTests(unittest.TestCase):
    def test_plugin_manifests_point_at_the_skill(self):
        marketplace = json.loads((REPO / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        plugin = json.loads((REPO / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(marketplace["name"], "ida-skill")
        self.assertEqual(marketplace["owner"]["name"], "e-bushi")
        self.assertEqual(len(marketplace["plugins"]), 1)
        entry = marketplace["plugins"][0]
        self.assertEqual(entry["name"], "ida")
        self.assertEqual(entry["source"], "./")
        self.assertNotIn("skills", entry)
        self.assertEqual(plugin["name"], "ida")
        self.assertEqual(plugin["version"], "1.10.0")
        self.assertTrue((REPO / "skills" / "ida" / "SKILL.md").is_file())
        self.assertNotIn("skills", plugin)


class ProseTests(unittest.TestCase):
    def test_no_em_dash_outside_the_source_csv(self):
        roots = [REPO / "README.md", REPO / ".claude-plugin", ROOT]
        for root in roots:
            paths = [root] if root.is_file() else [path for path in root.rglob("*") if path.is_file()]
            for path in paths:
                if path.suffix == ".csv" or "__pycache__" in path.parts or path.suffix == ".pyc":
                    continue
                text = path.read_text(encoding="utf-8")
                self.assertNotIn(EM, text, str(path))

    def test_banned_phrase_stays_in_the_instructions(self):
        phrase = "mental " + "models"
        allowed = {
            ROOT / "SKILL.md",
            ROOT / "references" / "voice.md",
            ROOT / "evals" / "checklist.md",
        }
        self.assertEqual((ROOT / "SKILL.md").read_text(encoding="utf-8").count(phrase), 1)
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        self.assertNotIn(phrase, readme)
        for path in ROOT.rglob("*"):
            if not path.is_file() or path.suffix not in {".md", ".json", ".py"}:
                continue
            if path in allowed:
                continue
            self.assertNotIn(phrase, path.read_text(encoding="utf-8"), str(path))
        for law in json.loads((LIBRARY / "exemplars.json").read_text(encoding="utf-8"))["entries"]:
            self.assertIn(law["law"], (ROOT / "references" / "voice.md").read_text(encoding="utf-8"))
        self.assertIn("reach for clarity", readme)
        self.assertIn("~/.claude/skills", readme)
        self.assertIn("~/.cursor/skills", readme)
        self.assertIn("~/.ida/progress.json", readme)
        self.assertIn("/plugin marketplace add e-bushi/ida-skill", readme)
        self.assertIn("/plugin install ida@ida-skill", readme)
        self.assertIn("npx skills add e-bushi/ida-skill", readme)
        self.assertIn("/ida:ida", readme)
        self.assertIn("#111316", readme)
        self.assertIn("#EDEAE4", readme)
        self.assertIn("#0A84FF", readme)


if __name__ == "__main__":
    unittest.main()
