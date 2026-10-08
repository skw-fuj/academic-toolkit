#!/usr/bin/env python3
"""Verify an MCQ worksheet's correct-answer letter sequence has no detectable
guessing pattern before filing it.

Usage: check_answer_pattern.py A,B,C,D,B,A,...   (one letter per question, in order)

Exits non-zero and prints every violation if the sequence is guessable; prints
PASS and exits 0 otherwise. This exists because hand-balancing letters by eye
is unreliable — a real past failure had 14/22 answers on "B" (pure frequency
bias), and a second hand-fix that balanced frequency still repeated the
bigram "CD" four times (a learnable adjacency pattern). Always run this
script on the final letter sequence rather than eyeballing it.
"""
import sys
from collections import Counter, defaultdict


def check(seq: str):
    seq = seq.upper()
    n = len(seq)
    issues = []

    counts = Counter(seq)
    for letter in "ABCD":
        counts.setdefault(letter, 0)
    if max(counts.values()) - min(counts.values()) > 1:
        issues.append(
            f"Letter frequency imbalance: {dict(counts)} — max/min spread > 1. "
            "Rebalance so each letter appears roughly n/4 times."
        )

    for i in range(n - 2):
        if seq[i] == seq[i + 1] == seq[i + 2]:
            issues.append(f"Run of 3+ identical letters at positions {i+1}-{i+3} ('{seq[i:i+3]}').")

    letters = "ABCD"
    for i in range(n - 3):
        window = seq[i:i + 4]
        if window == letters or window == letters[::-1]:
            issues.append(f"Straight A-B-C-D (or reverse) cycle at positions {i+1}-{i+4} ('{window}').")

    trans = defaultdict(Counter)
    for i in range(n - 1):
        trans[seq[i]][seq[i + 1]] += 1
    for src, nxt in trans.items():
        total = sum(nxt.values())
        if not total:
            continue
        maxletter, maxcount = nxt.most_common(1)[0]
        if maxcount >= 3:
            issues.append(
                f"'{src}' is followed by '{maxletter}' {maxcount} times — a learnable "
                f"transition pattern ('after {src} comes {maxletter}')."
            )
        elif total >= 2 and maxcount / total > 0.6:
            issues.append(f"'{src}' is followed by '{maxletter}' in {maxcount}/{total} cases — too dominant.")

    bigrams = Counter(seq[i:i + 2] for i in range(n - 1))
    for bg, count in bigrams.items():
        if count > 2:
            issues.append(f"Bigram '{bg}' repeats {count} times — reduce to at most 2 (mathematical floor for n={n}).")

    return issues


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    raw = sys.argv[1].replace(" ", "")
    seq = raw.split(",") if "," in raw else list(raw)
    seq = "".join(s.strip().upper() for s in seq if s.strip())
    issues = check(seq)
    if issues:
        print(f"FAIL — {len(issues)} guessing-pattern issue(s) in sequence '{seq}' (n={len(seq)}):")
        for i in issues:
            print(f"  - {i}")
        sys.exit(1)
    print(f"PASS — no detectable guessing pattern in sequence '{seq}' (n={len(seq)}).")
    sys.exit(0)


if __name__ == "__main__":
    main()
