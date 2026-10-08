#!/usr/bin/env python3
"""Automate the mechanical parts of the MCQ Construction Standard Part 3 self-audit.

Covers, deterministically:
  check 1  length cueing          — flags items where the keyed option is materially longer/shorter
  check 2  absolute / hedge words  — scans every option for cueing vocabulary
  check 5  all / none of the above — flags either phrase anywhere in the set
  check 6  numeric range overlap   — flags pairs of options that are overlapping numeric ranges
  check 4  answer-position pattern — shells out to check_answer_pattern.py on the key sequence

Checks 3 (grammar fit), 7 (distractor plausibility), 8 (cover-the-options), 9 (cross-item
independence) are judgement passes and are NOT automated — do them by reading.

Input: a JSON file (or stdin) shaped as
  [
    {"stem": "...", "options": {"A": "...", "B": "...", "C": "...", "D": "..."}, "answer": "C"},
    ...
  ]

Exit 0 and print PASS if nothing mechanical is flagged; exit 1 and list every flag otherwise.
Stdlib only.
"""
import json
import os
import re
import subprocess
import sys

ABSOLUTES = ["always", "never", "all of", "none of", "only", "every", "no ", "cannot", "must "]
HEDGES = ["may ", "might", "can be", "could", "sometimes", "usually", "often", "rarely",
          "occasionally", "many", "few", "some ", "generally", "typically", "tends to"]

RANGE_RE = re.compile(
    r"(-?\d+(?:\.\d+)?)\s*(?:-|–|—|to)\s*(-?\d+(?:\.\d+)?)")


def _len_flag(item, idx):
    opts = item["options"]
    key = item["answer"]
    lengths = {k: len(v) for k, v in opts.items()}
    keylen = lengths[key]
    others = [v for k, v in lengths.items() if k != key]
    if not others:
        return None
    avg_other = sum(others) / len(others)
    # keyed option >60% longer or <50% as long as the mean distractor
    if keylen > avg_other * 1.6 or keylen < avg_other * 0.5:
        return (f"item {idx+1}: keyed option {key} is {keylen} chars vs mean distractor "
                f"{avg_other:.0f} — length cueing risk (check 1)")
    return None


def _vocab_flags(item, idx):
    flags = []
    for k, v in item["options"].items():
        low = " " + v.lower() + " "
        hits = [w.strip() for w in ABSOLUTES if w in low]
        if hits:
            flags.append(f"item {idx+1} option {k}: absolute term(s) {hits} — check 2")
        hedge_hits = [w.strip() for w in HEDGES if w in low]
        if hedge_hits and k == item["answer"]:
            flags.append(
                f"item {idx+1} keyed option {k}: hedge word(s) {hedge_hits} in the correct "
                f"answer — check 2")
    return flags


def _aotu_flags(item, idx):
    flags = []
    for k, v in item["options"].items():
        low = v.lower()
        if "all of the above" in low or "none of the above" in low or "both a and" in low:
            flags.append(f"item {idx+1} option {k}: '{v}' — no all/none-of-the-above (check 5)")
    return flags


def _overlap_flags(item, idx):
    flags = []
    ranges = {}
    for k, v in item["options"].items():
        m = RANGE_RE.search(v)
        if m:
            lo, hi = sorted((float(m.group(1)), float(m.group(2))))
            ranges[k] = (lo, hi)
    keys = list(ranges)
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = ranges[keys[i]], ranges[keys[j]]
            if a[0] <= b[1] and b[0] <= a[1]:
                flags.append(
                    f"item {idx+1}: options {keys[i]} {a} and {keys[j]} {b} are overlapping "
                    f"numeric ranges (check 6)")
    return flags


def _pattern_check(items):
    seq = ",".join(it["answer"].upper() for it in items)
    checker = os.path.join(os.path.dirname(os.path.abspath(__file__)), "check_answer_pattern.py")
    if not os.path.exists(checker):
        return [f"check 4 skipped: {checker} not found — run it manually on '{seq}'"]
    r = subprocess.run([sys.executable, checker, seq], capture_output=True, text=True)
    if r.returncode != 0:
        return ["check 4 (answer-position pattern) FAILED:\n" + r.stdout.strip()]
    return []


def main():
    raw = sys.stdin.read() if len(sys.argv) < 2 else open(sys.argv[1]).read()
    items = json.loads(raw)
    flags = []
    for idx, it in enumerate(items):
        for f in (_len_flag(it, idx),):
            if f:
                flags.append(f)
        flags += _vocab_flags(it, idx)
        flags += _aotu_flags(it, idx)
        flags += _overlap_flags(it, idx)
    flags += _pattern_check(items)

    if flags:
        print(f"FAIL — {len(flags)} mechanical flag(s) across {len(items)} items:")
        for f in flags:
            print(f"  - {f}")
        print("\nChecks 3, 7, 8, 9 are judgement passes — still do them by reading.")
        sys.exit(1)
    print(f"PASS — no mechanical flags across {len(items)} items "
          f"(checks 1, 2, 4, 5, 6). Still do checks 3, 7, 8, 9 by reading.")
    sys.exit(0)


if __name__ == "__main__":
    main()
