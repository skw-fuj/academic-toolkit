#!/usr/bin/env python3
"""Diagram palette + primitives for academic notes figures (matplotlib).

Design contract: standards/pdf-design.md. The DOCUMENT is pure
greyscale; diagrams are the ONLY place colour appears, on this restrained
palette. House palette for academic-toolkit figures.

    from make_diagrams import *
    fig, ax = new_figure(6.4, 2.6)
    b1 = rounded_box(ax, (0.02, 0.35), 0.14, 0.30, "Domain", fill=ACCENT_L)
    b2 = rounded_box(ax, (0.22, 0.35), 0.14, 0.30, "Kingdom")
    arrow(ax, (0.16, 0.50), (0.22, 0.50))
    save(fig, "fig1.png")        # 220 DPI, tight bbox

Rules (enforced by convention, not code — check the rendered image at real size):
  * NAVY + GREY do all structural work. ACCENT is spent on EXACTLY ONE element
    per figure — the thing the figure is making a point about. Never decoration.
  * No red / teal / purple, no rainbow category colours — distinguish categories
    by shape / position / label.
  * Flat fills only — no gradients, shadows, 3D / perspective.
  * Thin lines (~1.0-1.8 pt). Rounded rectangles, never sharp corners.
  * NEVER a title inside the image — the numbered caption carries the description.
  * Generous spacing — crowded/overlapping elements is the #1 first-draft failure.
"""
from __future__ import annotations

import glob
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.font_manager as _fm  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

# matplotlib doesn't always pick up user font dirs — register Liberation here
# so diagram text matches the note set regardless of the font cache.
for _d in (os.path.expanduser("~/Library/Fonts"), "/Library/Fonts",
           "/usr/share/fonts", "/usr/local/share/fonts",
           os.path.expanduser("~/.local/share/fonts"),
           os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")):
    for _p in glob.glob(os.path.join(_d, "**", "Liberation*.ttf"), recursive=True):
        try:
            _fm.fontManager.addfont(_p)
        except Exception:  # noqa: BLE001
            pass
_HAS_LIB_SANS = any(f.name == "Liberation Sans" for f in _fm.fontManager.ttflist)
_DIAGRAM_FONT = "Liberation Sans" if _HAS_LIB_SANS else "DejaVu Sans"

INK      = "#1a1a1a"   # body text / primary lines
NAVY     = "#2b3a55"   # the one structural accent — muted, not saturated
GREY     = "#8a8f98"   # secondary lines / muted elements
GREY_L   = "#e4e6ea"   # light fills
GREY_XL  = "#f5f6f8"   # very light fills / backgrounds
ACCENT   = "#b8873a"   # sparing highlight ONLY
ACCENT_L = "#efe3c8"   # light tint of the accent
WHITE    = "#ffffff"

plt.rcParams.update({
    "font.family": _DIAGRAM_FONT,
    "text.color": INK, "axes.edgecolor": GREY, "axes.labelcolor": INK,
    "xtick.color": INK, "ytick.color": INK,
    "axes.titlesize": 0,                 # no in-figure titles
    "figure.facecolor": WHITE, "savefig.facecolor": WHITE,
    "axes.grid": False, "font.size": 9,
})


def new_figure(width_in: float = 6.4, height_in: float = 2.8, *, band: bool = True):
    """A (fig, ax). `band=True` paints the faint GREY_XL background band seen
    behind figures in the shipped set. Do NOT set a title on the axes."""
    fig, ax = plt.subplots(figsize=(width_in, height_in))
    if band:
        fig.patch.set_facecolor(GREY_XL)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


def plot_axes(width_in: float = 6.4, height_in: float = 3.0):
    """A (fig, ax) for genuine plotted data (curves / scatter / bar) — spines
    left+bottom only, GREY_XL figure band, no grid, no title."""
    fig, ax = plt.subplots(figsize=(width_in, height_in))
    fig.patch.set_facecolor(GREY_XL)
    ax.set_facecolor(WHITE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GREY)
    return fig, ax


def _text_px_size(ax, text_artist):
    """(width, height) of a text artist in display pixels, via the actual
    renderer — the only reliable way to know if text fits its container."""
    renderer = ax.figure.canvas.get_renderer()
    bbox = text_artist.get_window_extent(renderer=renderer)
    return bbox.width, bbox.height


def _axes_frac_to_px(ax, w, h):
    """Convert an (w, h) size in axes-fraction units (0-1) to display pixels,
    for comparison against `_text_px_size`."""
    p0 = ax.transAxes.transform((0, 0))
    p1 = ax.transAxes.transform((w, h))
    return abs(p1[0] - p0[0]), abs(p1[1] - p0[1])


def rounded_box(ax, xy, w, h, label="", *, fill=None, fontsize=9, pad_frac=0.85):
    """A rounded rectangle: navy edge, flat `fill` (default white), centred
    label. xy is the lower-left corner in axes fraction (0-1).

    The label is auto-fit to the box: if it would render wider than
    `pad_frac` of the box's usable width, fontsize is shrunk (down to a 6pt
    floor) until it fits, so label text can never overflow the shape's frame
    the way manual font sizing sometimes did. This runs every time — it does
    not depend on anyone remembering to eyeball the PNG.
    """
    x, y = xy
    p = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.008,rounding_size=0.02",
        linewidth=1.4, edgecolor=NAVY, facecolor=(fill or WHITE))
    ax.add_patch(p)
    if label:
        txt = ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
                       fontsize=fontsize, color=INK)
        max_w_px, max_h_px = _axes_frac_to_px(ax, w * pad_frac, h * pad_frac)
        fs = fontsize
        while fs > 6:
            tw_px, th_px = _text_px_size(ax, txt)
            if tw_px <= max_w_px and th_px <= max_h_px:
                break
            fs -= 0.5
            txt.set_fontsize(fs)
        else:
            tw_px, th_px = _text_px_size(ax, txt)
            if tw_px > max_w_px or th_px > max_h_px:
                import warnings
                warnings.warn(
                    f"rounded_box: label {label!r} still overflows its box "
                    f"at the {fs}pt floor — shorten the text.", stacklevel=2)
    return p


def fit_text(ax, xy, text, max_w_frac, *, fontsize=8, color=INK, ha="center",
             va="top", max_lines=4):
    """Free-standing (non-boxed) label, auto-wrapped and auto-shrunk to fit
    within `max_w_frac` of axes width — the callout-label equivalent of
    `rounded_box`'s auto-fit. Use this instead of a bare `ax.text(...)` for
    any label placed near other elements, so adjacent labels can't collide.
    Wraps on word boundaries only (never mid-word) — if a single word is
    still too wide at the 6pt floor, that one line is allowed to slightly
    exceed `max_w_frac` rather than being hyphen-broken. Returns the Text
    artist.
    """
    import textwrap
    x, y = xy
    max_w_px, _ = _axes_frac_to_px(ax, max_w_frac, 1.0)
    fs = fontsize
    wrapped = text
    while True:
        # measure THIS text's actual average char width at this fontsize
        # (not a worst-case glyph like "M"), so the wrap width is realistic
        flat = text.replace("\n", " ")
        probe = ax.text(x, y, flat, fontsize=fs, alpha=0)
        full_w_px, _ = _text_px_size(ax, probe)
        probe.remove()
        avg_char_w = full_w_px / max(len(flat), 1)
        chars_per_line = max(6, int(max_w_px / max(avg_char_w, 1)))
        wrapped = "\n".join(
            "\n".join(textwrap.wrap(
                line, chars_per_line,
                break_long_words=False, break_on_hyphens=False)) or ""
            for line in text.split("\n")
        )
        n_lines = wrapped.count("\n") + 1
        txt = ax.text(x, y, wrapped, fontsize=fs, color=color, ha=ha, va=va)
        tw_px, _ = _text_px_size(ax, txt)
        if (tw_px <= max_w_px and n_lines <= max_lines) or fs <= 6:
            return txt
        txt.remove()
        fs -= 0.5


def check_layout(fig, ax, *, extra_texts=None):
    """Post-render safety net: measure every Text artist in `ax` (plus any
    passed in `extra_texts`) and raise if two of them overlap, or if any
    text's bbox falls outside the axes (0,1)x(0,1) data area. Call this
    right before `save()`. This is the automated replacement for "eyeball
    the PNG" — it catches the collision class of defect (label text running
    into the next label, or past its own shape) mechanically, every time.
    """
    renderer = fig.canvas.get_renderer()
    texts = list(ax.texts) + list(extra_texts or [])
    boxes = []
    for t in texts:
        s = t.get_text().strip()
        if not s:
            continue
        boxes.append((t, t.get_window_extent(renderer=renderer)))
    problems = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            t1, b1 = boxes[i]
            t2, b2 = boxes[j]
            if b1.overlaps(b2):
                problems.append(
                    f"text overlap: {t1.get_text()!r} <-> {t2.get_text()!r}")
    if problems:
        raise AssertionError(
            "check_layout found " + str(len(problems)) + " problem(s):\n  " +
            "\n  ".join(problems) +
            "\nFix by: shortening the label, widening the figure, increasing "
            "spacing between elements, or staggering label depth/position."
        )


def arrow(ax, xy_from, xy_to, *, color=NAVY, lw=1.4):
    """Clean triangular arrowhead, thin line."""
    ax.annotate("", xy=xy_to, xytext=xy_from,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                shrinkA=0, shrinkB=0))


def annotate_point(ax, xy, text, *, xytext=None):
    """The ONE accented callout per figure — gold marker + thin grey leader +
    label."""
    ax.plot(*xy, marker="D", markersize=6, color=ACCENT, zorder=5)
    ax.annotate(text, xy=xy, xytext=xytext or (xy[0] + 0.12, xy[1] - 0.12),
                fontsize=8, color=INK,
                arrowprops=dict(arrowstyle="-", color=GREY, lw=0.8))


def save(fig, path: str, *, dpi: int = 220, ax=None, skip_layout_check: bool = False):
    """Save the figure. By default, runs `check_layout(fig, ax)` first and
    raises (figure NOT written) if any label text overlaps another or its
    own shape — pass the `ax` from `new_figure()`/`plot_axes()` so this
    check actually runs; pass `skip_layout_check=True` only for a figure
    with no text labels (e.g. a bare scatter plot).
    """
    if ax is not None and not skip_layout_check:
        fig.canvas.draw()  # text extents are only valid after a draw pass
        check_layout(fig, ax)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", pad_inches=0.13,
                facecolor=fig.get_facecolor())
    plt.close(fig)
    return path


if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.abspath(__file__))

    # 1 — a structural figure (the taxonomy-hierarchy pattern)
    fig, ax = new_figure(6.6, 1.9)
    names = ["Domain", "Kingdom", "Phylum", "Class", "Order", "Family", "Genus", "Species"]
    n = len(names)
    bw, gap = 0.09, 0.033
    x = 0.01
    for k, nm in enumerate(names):
        fill = ACCENT_L if k in (0, n - 1) else None
        rounded_box(ax, (x, 0.30), bw, 0.42, nm, fill=fill, fontsize=7.5)
        if k < n - 1:
            arrow(ax, (x + bw, 0.51), (x + bw + gap, 0.51))
        x += bw + gap
    ax.text(0.02, 0.86, "broadest, most inclusive", fontsize=7, color=GREY)
    ax.text(0.98, 0.86, "narrowest, most specific", fontsize=7, color=GREY, ha="right")
    save(fig, os.path.join(here, "_smoke_fig1.png"))

    # 2 — a plotted-data figure with the one accent point
    import numpy as np
    fig, ax = plot_axes(6.4, 2.8)
    k = np.arange(1, 41)
    ax.plot(k, (1 - (1 - 0.05) ** k) * 100, color=NAVY, lw=1.6)
    ax.axhline(50, color=GREY, lw=0.8, ls=":")
    ax.axvline(20, color=ACCENT, lw=1.2, ls="--")
    y20 = (1 - 0.95 ** 20) * 100
    ax.plot(20, y20, "D", color=ACCENT, ms=6)
    ax.annotate("k=20 → 64% chance of ≥ 1 false positive", xy=(20, y20),
                xytext=(23, y20 - 14), fontsize=8, color=INK,
                arrowprops=dict(arrowstyle="-", color=GREY, lw=0.8))
    ax.set_xlabel("number of independent tests (k), true H₀, α = 0.05")
    ax.set_ylabel("P(≥ 1 false positive) %")
    save(fig, os.path.join(here, "_smoke_fig2.png"))
    print("wrote _smoke_fig1.png, _smoke_fig2.png")
