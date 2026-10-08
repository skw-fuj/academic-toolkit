#!/usr/bin/env python3
"""Template for a per-subject figure builder. Copy it to your own `figures/` folder.

    python3 figures_example.py <output_dir>

Rules (see standards/visuals.md): house palette, ONE accent per figure, no title inside the image,
free labels via fit_text(), and save(fig, path, ax=ax) so the overlap gate runs.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_diagrams import (ACCENT_L, GREY_L, arrow, fit_text, new_figure,  # noqa: E402
                           rounded_box, save)


def stage_flow(out_dir: str) -> str:
    """A three-stage process with exactly one highlighted (accent) stage."""
    fig, ax = new_figure(6.4, 2.2)
    rounded_box(ax, (0.04, 0.35), 0.24, 0.30, "stage one:\ninput", fill=GREY_L)
    rounded_box(ax, (0.38, 0.35), 0.24, 0.30, "stage two:\ntransformation", fill=ACCENT_L)
    rounded_box(ax, (0.72, 0.35), 0.24, 0.30, "stage three:\noutput", fill=GREY_L)
    arrow(ax, (0.28, 0.50), (0.38, 0.50))
    arrow(ax, (0.62, 0.50), (0.72, 0.50))
    fit_text(ax, (0.50, 0.14), "the highlighted stage is where the lecture's point is made", 0.7)
    path = os.path.join(out_dir, "stage_flow.png")
    save(fig, path, ax=ax)          # always pass ax: runs the text-overlap gate
    return path


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    print(stage_flow(out))
