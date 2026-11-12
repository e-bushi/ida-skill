"""Checks for the ida library, renderer, and progress file.

    python3 skills/ida/scripts/test_ida.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import build_library  # noqa: E402
import render  # noqa: E402
from catalog import load_catalog  # noqa: E402
from common import LIBRARY, ROOT  # noqa: E402

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
    def test_cards_share_a_width(self):
        doc = json.loads((LIBRARY / "phyla.json").read_text(encoding="utf-8"))
        for phylum in doc["phyla"]:
            for practice in ("decide", "spot"):
                text = render.card(4, phylum["id"], practice, "A short scene with a real stake.")
                widths = {len(line) for line in text.splitlines()}
                self.assertEqual(widths, {render.CARD_WIDTH}, phylum["id"] + " " + practice)
        long_name = "commutative / associative / distributive laws"
        text = render.card(
            8,
            "axiom",
            "spot",
            "A long label has to wrap inside the border.",
            mode="choice",
            options=[long_name, "tautology", "contradiction", "validity"],
        )
        self.assertTrue(all(len(line) == render.CARD_WIDTH for line in text.splitlines()))
        self.assertIn("1  commutative", text)

    def test_samples_live_in_the_docs(self):
        card = render.card(
            4,
            "strategy",
            "decide",
            "Your biggest customer asks for a custom feature only they would use. They pay 40% of your revenue.",
        )
        feedback = render.feedback(
            "strong",
            "second-order thinking",
            [
                "You saw the roadmap cost.",
                "Also consider inversion: what would make losing them survivable?",
            ],
        )
        bars = render.render_bars(
            [
                {"phylum": "axiom", "subtitle": "how to think clearly", "well": 0, "total": 103},
                {"phylum": "strategy", "subtitle": "how to win when others play too", "well": 24, "total": 81},
            ]
        )
        summary = render.summary_block(6, 4, 1, 0, 1, "inversion", "sunk cost fallacy", "pick up in strategy")
        guide = (ROOT / "references" / "format.md").read_text(encoding="utf-8")
        for block in (card, feedback, bars, summary, render.WORDMARK):
            self.assertIn(block, guide)
        transcripts = (ROOT / "examples" / "transcripts.md").read_text(encoding="utf-8")
        blocks = [
            render.opening("new"),
            render.opening("ready"),
            render.opening("returning", "Last time: 4 scenarios, last one in axiom."),
            render.opening("resume", "Last time: strategy, scenario 3."),
            render.sections(),
            render.card(
                1,
                "strategy",
                "decide",
                "You and your climbing partner are split across two trailheads. Both phones are dead. You still have to meet before dark, and neither of you named a place.",
            ),
            render.card(
                2,
                "systema",
                "decide",
                "Your team gets a bonus for tickets closed. This week the count is up, and the same bugs are coming back renamed.",
            ),
            render.card(
                4,
                "axiom",
                "spot",
                '"Either the launch ships on Tuesday, or it does not."',
            ),
            render.summary_block(4, 3, 0, 0, 1, "schelling point", "goodhart's law", "pick up at random"),
            render.feedback(
                "strong",
                "schelling point",
                [
                    "You named the place each of you expects the other to expect.",
                    "That is the whole move when you cannot talk.",
                ],
            ),
            render.card(
                3,
                "bias",
                "decide",
                "You are hiring from the founders who got famous. The ones who tried the same playbook and folded never show up in the interviews.",
                mode="choice",
                options=["confirmation bias", "survivorship bias", "halo effect", "planning fallacy"],
            ),
        ]
        for block in blocks:
            self.assertIn(block, transcripts)
        section_lines = [line for line in render.sections().splitlines() if len(line) > 4 and line[2].isdigit()]
        for line in section_lines:
            self.assertEqual(line[13:15], "  ")
            self.assertNotEqual(line[15], " ")

    def test_opening_and_summary_edges(self):
        self.assertNotIn("Practice:", render.opening("new"))
        self.assertIn("Practice:", render.opening("ready"))
        quiet = render.summary_block(0, 0, 0, 0, 0, "", "", "pick up wherever you like")
        self.assertIn("No scenarios this time.", quiet)
        self.assertLessEqual(max(len(line) for line in quiet.splitlines()), render.CARD_WIDTH)
        text = render.feedback("idk", "inversion", ["Study the failure, then refuse it."])
        self.assertTrue(text.startswith("? inversion."))
        self.assertTrue(all(len(line) <= render.CARD_WIDTH for line in text.splitlines()))


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
            self.assertEqual(stored["version"], 1)

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
            self.assertEqual(back["welcome"]["line"], "Last time: strategy, 3 scenarios.")
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
            path.write_text('{"version": 2}\n', encoding="utf-8")
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


class ProseTests(unittest.TestCase):
    def test_no_em_dash_outside_the_source_csv(self):
        roots = [REPO / "README.md", ROOT]
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
        self.assertIn("#111316", readme)
        self.assertIn("#EDEAE4", readme)
        self.assertIn("#0A84FF", readme)


if __name__ == "__main__":
    unittest.main()
