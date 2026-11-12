"""Load the lean library. Never reads the source CSV."""

from __future__ import annotations

from common import LIBRARY, read_json


def load_catalog() -> tuple[dict, list[dict]]:
    phyla_doc = read_json(LIBRARY / "phyla.json")
    entries: list[dict] = []
    for phylum in phyla_doc["phyla"]:
        doc = read_json(LIBRARY / "index" / f"{phylum['id']}.json")
        for entry in doc["entries"]:
            entries.append(
                {
                    **entry,
                    "phylum": phylum["id"],
                    "subtitle": phylum["subtitle"],
                }
            )
    return phyla_doc, entries
