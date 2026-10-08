#!/usr/bin/env python3
"""Diagram palette + helpers for academic PDF figures (matplotlib).

House palette — ONE restrained palette across every figure in a document set:
  navy  #2b3a55   structural / primary data-ink
  grey  #8a8f98   secondary structure / axes / gridlines
  pale  #e4e6ea   fills / bands / inactive elements
  gold  #b8873a   the ONE accent — reserved for the single element the figure
                  is making a point about. Never decorative.
No red / teal / purple. No in-figure titles — the numbered caption below the
figure (wblocks/blocks `figure()`) carries the description; the image carries
only axis and data labels.

Rendering route for figures whose labels carry examinable content stays as
standards/visuals.md prescribes (markdown tables by default,
/diagram-design for editorial figures). Use this module only for genuine
plotted data (distributions, curves, scatter, bar) in a standalone PDF.

    from make_diagrams import PALETTE, new_figure, save_figure, reset_counters
"""
from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

PALETTE = {
    "navy": "#2b3a55",
    "grey": "#8a8f98",
    "pale": "#e4e6ea",
    "gold": "#b8873a",
    "ink": "#121417",
}

_FIG_COUNT = {"n": 0}

_RC = {
    "font.family": "Carlito, DejaVu Sans",
    "font.size": 9,
    "axes.edgecolor": PALETTE["grey"],
    "axes.labelcolor": PALETTE["ink"],
    "axes.titlesize": 0,          # no in-figure titles
    "axes.grid": True,
    "grid.color": PALETTE["pale"],
    "grid.linewidth": 0.6,
    "xtick.color": PALETTE["ink"],
    "ytick.color": PALETTE["ink"],
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 200,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
}


def reset_counters() -> None:
    """Call at the start of each document build so figure numbers restart at 1."""
    _FIG_COUNT["n"] = 0


def new_figure(width_in: float = 5.4, height_in: float = 3.2):
    """A styled (fig, ax). Do not set a title on it."""
    plt.rcParams.update(_RC)
    fig, ax = plt.subplots(figsize=(width_in, height_in))
    return fig, ax


def save_figure(fig, out_dir: str, stem: str) -> str:
    """Save as <stem>_figN.png in out_dir, N incrementing per document. Returns the path."""
    _FIG_COUNT["n"] += 1
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{stem}_fig{_FIG_COUNT['n']}.png")
    fig.savefig(path)
    plt.close(fig)
    return path


if __name__ == "__main__":
    import numpy as np

    reset_counters()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_smoke_fig")
    fig, ax = new_figure()
    x = np.linspace(0, 10, 200)
    ax.plot(x, np.sin(x), color=PALETTE["navy"], lw=1.4, label="baseline")
    ax.plot(x, np.sin(x) * 0.4, color=PALETTE["grey"], lw=1.2, label="damped")
    ax.axvline(np.pi, color=PALETTE["gold"], lw=1.6, label="first zero (the point)")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("amplitude")
    ax.legend(frameon=False, fontsize=8)
    p = save_figure(fig, out, "smoke")
    print(p)
