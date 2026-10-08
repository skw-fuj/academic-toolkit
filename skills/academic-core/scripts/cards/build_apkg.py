#!/usr/bin/env python3
"""Build an Anki .apkg deck from a tab-separated Front\tBack file.

Usage: build_apkg.py <cards.tsv> "<Deck Name>" <out.apkg>

Deck/model IDs are derived deterministically from the deck name, so
re-running for the same lecture updates the existing Anki deck on
import rather than creating a duplicate.
"""
import csv
import hashlib
import sys

import genanki


def stable_id(seed: str, salt: str) -> int:
    digest = hashlib.sha256(f"{salt}:{seed}".encode("utf-8")).hexdigest()
    return int(digest[:8], 16) | (1 << 30)


def main(tsv_path: str, deck_name: str, out_path: str) -> None:
    model = genanki.Model(
        stable_id(deck_name, "model"),
        "Academic Q/A Model",
        fields=[{"name": "Front"}, {"name": "Back"}],
        templates=[
            {
                "name": "Card 1",
                "qfmt": "{{Front}}",
                "afmt": '{{FrontSide}}<hr id="answer">{{Back}}',
            }
        ],
        css="""
.card {
    font-family: Calibri, Carlito, sans-serif;
    font-size: 13pt;
    text-align: center;
    color: black;
    background-color: white;
    max-width: 34em;
    margin: 0 auto;
    padding: 1em;
    line-height: 1.4;
}
hr#answer {
    margin: 1em auto;
    max-width: 20em;
}
""",
    )
    deck = genanki.Deck(stable_id(deck_name, "deck"), deck_name)

    with open(tsv_path, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        count = 0
        for row in reader:
            if len(row) < 2 or not row[0].strip():
                continue
            front, back = row[0].strip(), row[1].strip()
            deck.add_note(genanki.Note(model=model, fields=[front, back]))
            count += 1

    genanki.Package(deck).write_to_file(out_path)
    print(f"Wrote {count} cards to {out_path}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
