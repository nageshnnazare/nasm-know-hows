#!/usr/bin/env python3
"""Generate the guide's SVG figures, tuned to the htmler blue theme.

The kit's grey/purple house style is re-hued to htmler's blue-forward palette.
Because the figures are inlined as static base64 images (no page CSS reaches
them), every colour is chosen to work on BOTH the dark (#0b0d12) and light
(#ffffff) themes at once. The trick: a mid-slate around luminance ~0.2 gives
roughly 4.3:1 contrast three ways — white text sitting on the fill, and the
same colour used as ink on either background.

  * slate blue  #6B7B94  (neutral boxes, connectors, axes, labels)
  * blue        #3E7CC0  (highlighted / "after" boxes)         + dark #2F5F98
  * teal        #1F918C  (positive "result" accent)
  * amber       #D9922B  (warning / spill; dark text on fill)
  * red         #D65A5F  (problem callouts)
  * muted       #9AA0B4  (captions)
  * white       #FFFFFF  (text inside dark fills)
  * 1.5pt wide rules, Aptos / system sans font stack

Run:  python3 scripts/gen_figures.py
Output: <chapter>/figures/*.svg
"""
import base64
import io
import os
import re

# ── House-style constants (htmler blue theme, dual light/dark legible) ───────
GREY = "#6B7B94"
GREY_D = "#55637A"
PURPLE = "#3E7CC0"
PURPLE_D = "#2F5F98"
TEAL = "#1F918C"
AMBER = "#D9922B"
RED = "#D65A5F"
WHITE = "#FFFFFF"
LIGHT = "#9AA0B4"
INK_DARK = "#1F2433"  # text on light (amber) fills
# Hand-drawn Excalidraw look: Virgil is embedded per-figure (see _font_face);
# 'Segoe Print'/cursive are only fallbacks if the embed ever fails.
FONT = "'Virgil','Segoe Print','Comic Sans MS',cursive"
RULE = 1.5  # pt wide rules

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "fonts", "Virgil.woff2")
_FACE_CACHE = {}


def _font_face(text):
    """Return a <style> block embedding a Virgil subset for `text`.

    The figures are inlined as base64 <img> data URIs, and browsers do not
    fetch external fonts for <img>-loaded SVGs — so the hand-drawn font must
    travel *inside* each SVG. We subset to the glyphs actually used to keep
    each figure tiny (~8-14 KB)."""
    # Subset to exactly the glyphs this figure uses (plus a space) so each
    # embedded font stays as small as possible.
    key = "".join(sorted(set(text) | {" "}))
    if key in _FACE_CACHE:
        return _FACE_CACHE[key]
    try:
        from fontTools import subset as _subset
        opts = _subset.Options()
        opts.flavor = "woff2"
        opts.desubroutinize = True
        opts.ignore_missing_unicodes = True
        font = _subset.load_font(FONT_PATH, opts)
        ss = _subset.Subsetter(options=opts)
        ss.populate(text=key)
        ss.subset(font)
        buf = io.BytesIO()
        font.save(buf)
        b64 = base64.b64encode(buf.getvalue()).decode()
        face = ("<style>@font-face{font-family:'Virgil';font-style:normal;"
                "font-weight:400;src:url(data:font/woff2;base64," + b64 +
                ") format('woff2');}</style>")
    except Exception as exc:  # pragma: no cover - fonttools optional
        print("  ! font embed skipped:", exc)
        face = ""
    _FACE_CACHE[key] = face
    return face


# ── Primitive builders ──────────────────────────────────────────────────────
def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def defs():
    """Arrowhead markers in each ink colour."""
    marks = []
    for name, col in (("g", GREY), ("p", PURPLE), ("t", TEAL),
                      ("r", RED), ("a", AMBER), ("l", LIGHT)):
        marks.append(
            f'<marker id="ah-{name}" viewBox="0 0 10 10" refX="8.5" refY="5" '
            f'markerWidth="4.5" markerHeight="4.5" orient="auto-start-reverse">'
            f'<path d="M0 0L10 5L0 10z" fill="{col}"/></marker>')
    return "<defs>" + "".join(marks) + "</defs>"


def rrect(x, y, w, h, fill, rx=9, stroke=None, sw=RULE, dash=None, opacity=None):
    s = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" ry="{rx}" '
         f'fill="{fill}"')
    if stroke:
        s += f' stroke="{stroke}" stroke-width="{sw}"'
    if dash:
        s += f' stroke-dasharray="{dash}"'
    if opacity is not None:
        s += f' opacity="{opacity}"'
    return s + "/>"


def tspan_lines(x, cy, lines, fill, size, weight, lh):
    """Vertically centred multiline <text>."""
    n = len(lines)
    y0 = cy - (n - 1) * lh / 2.0
    out = [f'<text x="{x}" y="{y0}" fill="{fill}" font-family="{FONT}" '
           f'font-size="{size}" font-weight="{weight}" text-anchor="middle" '
           f'dominant-baseline="central">']
    for i, ln in enumerate(lines):
        dy = 0 if i == 0 else lh
        out.append(f'<tspan x="{x}" dy="{dy}">{esc(ln)}</tspan>')
    out.append("</text>")
    return "".join(out)


def box(x, y, w, h, lines, fill=GREY, tcol=WHITE, size=13, weight=600,
        rx=9, lh=16, stroke=None, sw=RULE, dash=None):
    if isinstance(lines, str):
        lines = [lines]
    r = rrect(x, y, w, h, fill, rx=rx, stroke=stroke, sw=sw, dash=dash)
    t = tspan_lines(x + w / 2.0, y + h / 2.0, lines, tcol, size, weight, lh)
    return r + t


def obox(x, y, w, h, lines, stroke=GREY, tcol=GREY, size=13, weight=600,
         rx=9, lh=16, sw=RULE, dash=None, fill="none"):
    """Outlined box (transparent fill) with coloured text."""
    r = rrect(x, y, w, h, fill, rx=rx, stroke=stroke, sw=sw, dash=dash)
    t = tspan_lines(x + w / 2.0, y + h / 2.0, lines if isinstance(lines, list)
                    else [lines], tcol, size, weight, lh)
    return r + t


def text(x, y, s, fill=GREY, size=13, weight=600, anchor="middle",
         italic=False, mono=False):
    fam = ("'SFMono-Regular',ui-monospace,'JetBrains Mono',Consolas,monospace"
           if mono else FONT)
    st = ""  # italics disabled: the hand-drawn font is hard to read slanted
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-family="{fam}" '
            f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}"'
            f'{st} dominant-baseline="central">{esc(s)}</text>')


def line(x1, y1, x2, y2, col=GREY, sw=RULE, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" '
            f'stroke-width="{sw}"{d}/>')


def _mk(col):
    return {GREY: "g", PURPLE: "p", TEAL: "t", RED: "r", AMBER: "a",
            LIGHT: "l"}.get(col, "g")


def arrow(x1, y1, x2, y2, col=GREY, sw=RULE, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" '
            f'stroke-width="{sw}" marker-end="url(#ah-{_mk(col)})"{d}/>')


def path(d, col=GREY, sw=RULE, dash=None, arrow_end=False, fill="none"):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#ah-{_mk(col)})"' if arrow_end else ""
    return (f'<path d="{d}" fill="{fill}" stroke="{col}" stroke-width="{sw}"'
            f'{dd}{m}/>')


def cylinder(x, y, w, h, fill=GREY, tcol=WHITE, lines=None, size=12,
             stroke=None, sw=RULE):
    """Database / memory cylinder."""
    ry = min(h * 0.16, 14)
    st = (f' stroke="{stroke}" stroke-width="{sw}"') if stroke else ""
    body = (f'<path d="M{x} {y+ry} A{w/2} {ry} 0 0 0 {x+w} {y+ry} '
            f'L{x+w} {y+h-ry} A{w/2} {ry} 0 0 1 {x} {y+h-ry} Z" '
            f'fill="{fill}"{st}/>')
    top = (f'<ellipse cx="{x+w/2}" cy="{y+ry}" rx="{w/2}" ry="{ry}" '
           f'fill="{fill}"{st}/>')
    lip = (f'<path d="M{x} {y+ry} A{w/2} {ry} 0 0 0 {x+w} {y+ry}" '
           f'fill="none" stroke="{WHITE}" stroke-width="1" opacity="0.35"/>')
    t = ""
    if lines:
        t = tspan_lines(x + w / 2.0, y + h / 2.0 + ry / 2, lines, tcol, size,
                        600, 15)
    return body + top + lip + t


def svg(w, h, body, title=""):
    t = f"<title>{esc(title)}</title>" if title else ""
    used = "".join(re.findall(r'>([^<]*)<', body)) + title
    face = _font_face(used)
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" font-family="{FONT}">{face}{t}{defs()}'
            f'{body}</svg>\n')


def write(rel_path, content):
    full = os.path.join(REPO_ROOT, rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)
    print("wrote", rel_path, f"({len(content)} bytes)")


# ── Before/after "code card" primitives ─────────────────────────────────────
MONO = ("'SFMono-Regular',ui-monospace,'JetBrains Mono',Menlo,"
        "Consolas,monospace")
CARD_BG = "#232A35"          # self-contained dark code card (theme-independent)
CODE_FG = "#D7DCE6"
CODE_DIM = "#8892A5"
CODE_HI = "#7FC4FF"          # changed / highlighted line
CODE_GOOD = "#83CEA3"        # added
CODE_BAD = "#E98A90"         # removed
LBL_BEFORE = "#9AA0B4"
LBL_AFTER = "#7FC4FF"
PAD = 14
LH = 19
CSIZE = 12.5
CHARW = 7.55
LABEL_AREA = 28
BOTTOM = 12
_STYLE_COL = {"n": CODE_FG, "hi": CODE_HI, "dim": CODE_DIM,
              "good": CODE_GOOD, "bad": CODE_BAD}


def _txt(ln):
    return ln[0] if isinstance(ln, tuple) else ln


def card_size(lines, label, minw=0):
    maxlen = max([len(_txt(l)) for l in lines] + [len(label) + 2])
    w = max(minw, PAD * 2 + int(round(maxlen * CHARW)))
    h = LABEL_AREA + len(lines) * LH + BOTTOM
    return w, h


def code_card(x, y, lines, label, border, labelcol, minw=0):
    w, h = card_size(lines, label, minw)
    out = [rrect(x, y, w, h, CARD_BG, rx=11, stroke=border, sw=1.75)]
    out.append(f'<text x="{x+PAD}" y="{y+15}" fill="{labelcol}" '
               f'font-family="{FONT}" font-size="10.5" font-weight="700" '
               f'letter-spacing="1.2" text-anchor="start" '
               f'dominant-baseline="central">{esc(label)}</text>')
    cy = y + LABEL_AREA + LH / 2
    for ln in lines:
        txt, style = (ln if isinstance(ln, tuple) else (ln, "n"))
        out.append(
            f'<text x="{x+PAD}" y="{cy}" fill="{_STYLE_COL[style]}" '
            f'font-family="{MONO}" font-size="{CSIZE}" text-anchor="start" '
            f'dominant-baseline="central" '
            f'xml:space="preserve">{esc(txt)}</text>')
        cy += LH
    return "".join(out), w, h


def before_after(fname, title, before, after, op="", note_b="", note_a="",
                 blabel="BEFORE", alabel="AFTER", title2="", gap=104):
    wl, hl = card_size(before, blabel)
    wr, hr = card_size(after, alabel)
    top = 46 if not title2 else 62
    y0 = top
    maxh = max(hl, hr)
    xl = 24
    xr = xl + wl + gap
    W = xr + wr + 24
    note_h = 26 if (note_b or note_a) else 0
    H = top + maxh + note_h + 18
    b = [text(W / 2, 24, title, GREY, 15.5, 700)]
    if title2:
        b.append(text(W / 2, 44, title2, LIGHT, 11.5, 500, italic=True))
    cl, _, _ = code_card(xl, y0, before, blabel, GREY_D, LBL_BEFORE)
    cr, _, _ = code_card(xr, y0, after, alabel, PURPLE, LBL_AFTER)
    b.append(cl)
    b.append(cr)
    ay = y0 + maxh / 2
    b.append(arrow(xl + wl + 16, ay, xr - 12, ay, PURPLE, 2.0))
    if op:
        b.append(text((xl + wl + xr) / 2, ay - 13, op, PURPLE, 11, 700))
    if note_b:
        b.append(text(xl + wl / 2, y0 + maxh + 15, note_b, RED, 11, 600))
    if note_a:
        b.append(text(xr + wr / 2, y0 + maxh + 15, note_a, TEAL, 11, 600))
    write(fname, svg(W, H, "".join(b), title))


def rules_fig(fname, title, pairs, note="", lhs_hdr="", rhs_hdr=""):
    """A card of  lhs  →  rhs  rewrite rules (monospace)."""
    lw = max(len(l) for l, _ in pairs)
    rw = max(len(r) for _, r in pairs)
    x0, y0 = 24, 46
    lx = x0 + PAD
    arrow_x1 = lx + int(lw * CHARW) + 12
    arrow_x2 = arrow_x1 + 30
    rx = arrow_x2 + 12
    cardw = (rx + int(rw * CHARW) + PAD) - x0
    rows = len(pairs)
    hdr_h = 20 if (lhs_hdr or rhs_hdr) else 0
    cardh = LABEL_AREA + hdr_h + rows * LH + BOTTOM
    W = x0 + cardw + 24
    H = y0 + cardh + (24 if note else 12)
    b = [text(W / 2, 24, title, GREY, 15.5, 700)]
    b.append(rrect(x0, y0, cardw, cardh, CARD_BG, rx=11, stroke=GREY_D,
                   sw=1.75))
    cy = y0 + LABEL_AREA + hdr_h + LH / 2
    if hdr_h:
        b.append(text(lx, y0 + 16, lhs_hdr, LBL_BEFORE, 10.5, 700,
                      anchor="start"))
        b.append(text(rx, y0 + 16, rhs_hdr, LBL_AFTER, 10.5, 700,
                      anchor="start"))
    for l, r in pairs:
        b.append(f'<text x="{lx}" y="{cy}" fill="{CODE_FG}" '
                 f'font-family="{MONO}" font-size="{CSIZE}" text-anchor="start"'
                 f' dominant-baseline="central" '
                 f'xml:space="preserve">{esc(l)}</text>')
        b.append(arrow(arrow_x1, cy, arrow_x2, cy, PURPLE, 1.8))
        b.append(f'<text x="{rx}" y="{cy}" fill="{CODE_GOOD}" '
                 f'font-family="{MONO}" font-size="{CSIZE}" text-anchor="start"'
                 f' dominant-baseline="central" '
                 f'xml:space="preserve">{esc(r)}</text>')
        cy += LH
    if note:
        b.append(text(W / 2, y0 + cardh + 13, note, LIGHT, 11, 500,
                      italic=True))
    write(fname, svg(W, H, "".join(b), title))




# ── memory-domain helpers ────────────────────────────────────────────────────
def seg(x, y, w, h, label, color, sub=None, tcol=WHITE, size=12.5, rx=3,
        stroke=None):
    lines = [label] if sub is None else [label, sub]
    return box(x, y, w, h, lines, color, tcol=tcol, size=size, rx=rx, lh=15,
               stroke=stroke)


def addr(x, y, s):
    return text(x, y, s, LIGHT, 10.5, 600, anchor="end", mono=True)


def perm(x, y, s, col=TEAL):
    return text(x, y, s, col, 11, 700, anchor="start", mono=True)


# ── root: the virtual address-space map (signature hero) ─────────────────────
def fig_address_space():
    W, H = 780, 740
    bx, bw = 250, 330
    b = [text(W / 2, 28, "The process virtual address space (x86-64)",
              GREY, 16, 700)]
    rows = [
        ("KERNEL SPACE", "mapped in every process \u00b7 CPL0 only", GREY_D, 66,
         "0xFFFFFFFFFFFFFFFF", "---"),
        ("non-canonical hole", "unmapped 47-bit gap", LIGHT, 40,
         "0xFFFF800000000000", ""),
    ]
    y = 46
    for label, sub, col, h, a, pr in rows:
        b.append(seg(bx, y, bw, h, label, col, sub=sub,
                     tcol=(INK_DARK if col == LIGHT else WHITE), size=12))
        b.append(addr(bx - 12, y + 12, a))
        y += h + 6
    b.append(addr(bx - 12, y + 8, "0x00007FFFFFFFFFFF"))
    y += 14
    # stack (grows down)
    b.append(seg(bx, y, bw, 58, "STACK  \u2193", PURPLE,
                 sub="args/env \u00b7 frames \u00b7 grows down", size=12))
    b.append(perm(bx + bw + 12, y + 22, "rw-", TEAL))
    y += 58 + 8
    b.append(seg(bx, y, bw, 92, "mmap region", GREY,
                 sub="shared libs \u00b7 thread stacks \u00b7 anon mmap", size=12))
    b.append(perm(bx + bw + 12, y + 30, "rw-/r-x", GREY))
    y += 92 + 8
    b.append(seg(bx, y, bw, 58, "HEAP  \u2191", TEAL,
                 sub="malloc / brk-managed \u00b7 grows up", size=12))
    b.append(perm(bx + bw + 12, y + 22, "rw-", TEAL))
    y += 58 + 6
    for label, sub, col, pr in [
            ("BSS", "zero-init data", GREY_D, "rw-"),
            ("DATA", "initialised globals", GREY_D, "rw-"),
            ("TEXT + RODATA", "code & constants", GREY, "r-x")]:
        b.append(seg(bx, y, bw, 40, label, col, sub=sub, size=11))
        b.append(perm(bx + bw + 12, y + 20, pr, GREY))
        y += 40 + 4
    b.append(addr(bx - 12, y + 4, "0x0000000000400000"))
    y += 10
    b.append(seg(bx, y, bw, 34, "NULL guard  (PROT_NONE)", LIGHT,
                 tcol=INK_DARK, size=11))
    b.append(addr(bx - 12, y + 24, "0x0"))
    b.append(text(W / 2, H - 12,
                  "virtual \u2260 physical \u00b7 memory is lazy \u00b7 the MMU maps "
                  "pages to frames", LIGHT, 11, 500))
    write("figures/address-space.svg", svg(W, H, "".join(b),
                                           "Virtual address space"))


def fig_roadmap():
    W, H = 940, 560
    b = [text(W / 2, 28, "A reading path through the guide", GREY, 16, 700)]
    bw, bh = 150, 46

    def chip(x, y, num, ttl, col=GREY, w=bw):
        b.append(box(x, y, w, bh, [f"{num}  {ttl}"], col, size=11.5, rx=8))

    cols = [40, 240, 440, 640, 780]
    chip(cols[1], 60, "00", "fundamentals", PURPLE)
    chip(cols[1], 130, "02", "address space")
    chip(cols[0], 200, "03", "stack")
    chip(cols[2], 200, "01", "virtual memory")
    chip(cols[0], 270, "04", "heap / malloc")
    chip(cols[1], 270, "05", "mmap")
    chip(cols[2], 270, "06", "brk / sbrk")
    chip(cols[1], 340, "08", "process syscalls")
    chip(cols[0], 410, "09", "threads")
    chip(cols[2], 410, "10", "IPC & shm")
    chip(cols[1], 410, "11", "protection")
    chip(cols[1], 480, "07", "paging / swap")
    chip(cols[0], 480 - 0, "13", "advanced", GREY_D)
    chip(cols[2], 480, "12", "debugging", GREY_D)
    chip(cols[3] + 40, 340, "14", "allocators", PURPLE, w=170)
    # a few guiding arrows
    def a(x1, y1, x2, y2, dash=None):
        b.append(arrow(x1, y1, x2, y2, GREY, 1.6, dash=dash))
    a(cols[1] + bw / 2, 106, cols[1] + bw / 2, 130)
    a(cols[1] + bw / 2, 176, cols[1] + bw / 2, 200 - 0, dash="4 4")
    a(cols[1] + 20, 176, cols[0] + bw / 2, 200)
    a(cols[1] + bw - 20, 176, cols[2] + bw / 2, 200)
    a(cols[0] + bw / 2, 246, cols[0] + bw / 2, 270)
    a(cols[2] + bw / 2, 246, cols[2] + bw / 2, 270)
    a(cols[1] + bw / 2, 316, cols[1] + bw / 2, 340)
    a(cols[1] + bw / 2, 386, cols[1] + bw / 2, 410)
    a(cols[1] + bw / 2, 456, cols[1] + bw / 2, 480)
    b.append(arrow(cols[1] + bw, 363, cols[3] + 40, 363, PURPLE, 2))
    write("figures/roadmap.svg", svg(W, H, "".join(b), "Reading path"))


# ── 00 fundamentals ──────────────────────────────────────────────────────────
def fig_hierarchy():
    W, H = 1060, 430
    b = [text(W / 2, 28, "The memory hierarchy \u2014 latency vs capacity",
              GREY, 16, 700)]
    rows = [
        ("registers", "~1 cycle", "< 1 KiB", PURPLE, 170),
        ("L1 cache", "~4 cycles / ~1 ns", "32 KiB / core", PURPLE, 250),
        ("L2 cache", "~12 cycles / ~3 ns", "256 KiB\u20131 MiB", GREY, 340),
        ("L3 cache", "~40 cycles / ~10 ns", "8\u201332 MiB", GREY, 430),
        ("DRAM", "~200 cycles / ~80 ns", "many GiB", GREY_D, 540),
        ("NVMe SSD", "~10 \u00b5s", "TiB", GREY_D, 620),
        ("spinning disk", "~10 ms", "TiB", LIGHT, 700),
    ]
    y = 52
    cx = 60
    for name, lat, cap, col, w in rows:
        tc = INK_DARK if col == LIGHT else WHITE
        b.append(box(cx, y, w, 40, [name], col, tcol=tc, size=12.5, rx=6))
        b.append(text(cx + w + 14, y + 20,
                      f"{lat}   \u00b7   {cap}", GREY, 11, 600, anchor="start"))
        y += 50
    b.append(text(W / 2, H - 14,
                  "smaller & faster at the top \u2014 locality keeps you near "
                  "the top", LIGHT, 11, 500))
    write("figures/memory-hierarchy.svg",
          svg(W, H, "".join(b), "Memory hierarchy"))


def fig_cache_line():
    before_after(
        "figures/false-sharing.svg",
        "Cache line = 64 bytes (the unit of coherence)",
        [("core A writes a[0]", "n"), ("core B writes a[1]", "n"),
         ("a[0],a[1] same line", "bad")],
        [("pad to 64 B each", "good"), ("a[0] | line 0", "hi"),
         ("a[1] | line 1", "hi")], op="align",
        note_b="line ping-pongs (false sharing)",
        note_a="one line per core \u2014 no bouncing")


# ── 01 virtual memory ────────────────────────────────────────────────────────
def fig_page_walk():
    W, H = 1000, 460
    b = [text(W / 2, 28, "4-level page-table walk (x86-64, 4 KiB pages)",
              GREY, 16, 700)]
    # VA split bar
    bx, y = 90, 54
    parts = [("sign", 100, GREY_D), ("PML4", 120, PURPLE), ("PDPT", 120, PURPLE),
             ("PD", 120, PURPLE), ("PT", 120, PURPLE), ("offset", 160, GREY)]
    x = bx
    for name, w, col in parts:
        b.append(box(x, y, w, 40, [name], col, size=11.5, rx=4))
        x += w + 2
    b.append(text(bx, y - 8, "63", LIGHT, 9, 600, anchor="start"))
    b.append(text(x - 2, y - 8, "0", LIGHT, 9, 600, anchor="end"))
    # table chain
    ty = 150
    cx0, step, bw = 95, 195, 130
    names = ["PML4", "PDPT", "PD", "PT", "4 KiB frame"]
    for i, name in enumerate(names):
        cx = cx0 + i * step
        col = TEAL if i == 4 else GREY
        b.append(box(cx - bw / 2, ty, bw, 56, [name, "(4 KiB)"], col, size=11,
                     lh=14))
        if i > 0:
            b.append(arrow(cx - step + bw / 2, ty + 28, cx - bw / 2, ty + 28,
                           GREY, 1.8))
    fx = cx0 + 4 * step  # frame column centre
    b.append(text(cx0 - bw / 2, ty - 12, "CR3 \u2192", PURPLE, 11, 700,
                  anchor="start"))
    b.append(arrow(fx, ty + 56, fx, ty + 96, TEAL, 2))
    b.append(box(fx - bw / 2, ty + 96, bw, 46, ["+ offset", "\u2192 phys addr"],
                 TEAL, size=11, lh=14))
    b.append(text(W / 2, ty + 180,
                  "a TLB miss can cost 4 extra memory accesses \u2014 hence the TLB",
                  LIGHT, 11, 500))
    write("figures/page-table-walk.svg",
          svg(W, H, "".join(b), "Page-table walk"))


def fig_tlb():
    W, H = 720, 320
    b = [text(W / 2, 28, "TLB \u2014 caching virtual\u2192physical translations",
              GREY, 15, 700)]
    b.append(box(60, 70, 150, 50, ["CPU: load VA"], GREY, size=12))
    b.append(box(285, 70, 150, 50, ["TLB lookup"], PURPLE, size=12))
    b.append(arrow(210, 95, 285, 95, GREY, 1.8))
    b.append(box(510, 60, 150, 44, ["hit \u2192 phys addr"], TEAL, size=12))
    b.append(arrow(435, 88, 510, 78, TEAL, 1.8))
    b.append(text(475, 66, "~0 cycles", TEAL, 10, 700))
    b.append(box(285, 165, 150, 50, ["page-table walk"], GREY, size=11))
    b.append(arrow(360, 120, 360, 165, RED, 1.8))
    b.append(text(372, 142, "miss", RED, 10, 700, anchor="start"))
    b.append(box(285, 250, 150, 44, ["install in TLB", "retry"], GREY_D,
                 size=11, lh=14))
    b.append(arrow(360, 215, 360, 250, GREY, 1.8))
    b.append(path(f"M285 272 C180 272 180 95 285 95", GREY, 1.6,
                  arrow_end=True, dash="4 4"))
    b.append(text(W / 2, H - 12,
                  "flushed on CR3 reload / INVLPG / munmap / mprotect "
                  "(global pages survive)", LIGHT, 10.5, 500))
    write("figures/tlb.svg", svg(W, H, "".join(b), "TLB"))


def fig_page_fault():
    W, H = 760, 430
    b = [text(W / 2, 28, "Page-fault handling (#PF \u2192 do_page_fault)",
              GREY, 15, 700)]
    b.append(box(300, 56, 160, 44, ["MMU walk \u2192 #PF"], PURPLE, size=12))

    def q(x, y, t, col=GREY, w=200):
        b.append(box(x, y, w, 40, [t], col, size=11))
    q(280, 120, "valid VMA?", GREY)
    b.append(arrow(380, 100, 380, 120, GREY, 1.8))
    b.append(box(540, 120, 150, 40, ["SIGSEGV"], RED, size=11))
    b.append(arrow(480, 140, 540, 140, RED, 1.6))
    b.append(text(512, 132, "no", RED, 10, 700))
    q(280, 190, "perms OK?", GREY)
    b.append(arrow(380, 160, 380, 190, GREY, 1.8))
    b.append(box(540, 190, 150, 40, ["SIGSEGV / SIGBUS"], RED, size=10))
    b.append(arrow(480, 210, 540, 210, RED, 1.6))
    b.append(text(512, 202, "no", RED, 10, 700))
    b.append(box(200, 270, 170, 56, ["minor fault", "alloc frame / zero page"],
                 TEAL, size=11, lh=14))
    b.append(box(400, 270, 170, 56, ["major fault", "read swap / file"], AMBER,
                 tcol=INK_DARK, size=11, lh=14))
    b.append(arrow(340, 230, 285, 270, GREY, 1.8))
    b.append(arrow(420, 230, 485, 270, GREY, 1.8))
    b.append(box(300, 356, 160, 40, ["fill PTE \u2192 restart"], GREY_D, size=11))
    b.append(arrow(285, 326, 360, 356, GREY, 1.6))
    b.append(arrow(485, 326, 400, 356, GREY, 1.6))
    write("figures/page-fault.svg",
          svg(W, H, "".join(b), "Page fault"))


def fig_zero_page():
    W, H = 820, 300
    b = [text(W / 2, 28, "Lazy allocation: the shared zero page + CoW",
              GREY, 15, 700)]
    xs = [40, 300, 560]
    steps = [
        ("1  mmap(anon)", ["VMA created", "no PTEs", "RSS += 0"], GREY),
        ("2  read p[0]", ["PTE \u2192 zero page", "read-only, shared", "RSS += 0"],
         PURPLE),
        ("3  write p[0]", ["CoW: new frame", "PTE now rw-", "RSS += 4 KiB"],
         TEAL),
    ]
    for x, (ttl, rows, col) in zip(xs, steps):
        b.append(box(x, 60, 220, 120, [ttl] + rows, col, size=12, lh=20,
                     rx=10))
        if x != xs[-1]:
            b.append(arrow(x + 220, 120, x + 260, 120, GREY, 2))
    b.append(text(W / 2, H - 16,
                  "malloc(1 GiB) succeeds on a small machine \u2014 frames attach "
                  "only when touched", LIGHT, 11, 500))
    write("figures/zero-page.svg",
          svg(W, H, "".join(b), "Zero page"))


# ── 02 process address space ─────────────────────────────────────────────────
def fig_elf_load():
    W, H = 780, 380
    b = [text(W / 2, 28, "execve: ELF file \u2192 LOAD segments in memory",
              GREY, 15, 700)]
    # ELF file
    fx = 60
    b.append(text(fx + 95, 58, "a.out on disk", GREY, 12, 700))
    file_rows = [("ELF header", GREY_D), ("program headers", GREY_D),
                 (".text (RX)", GREY), (".rodata (R)", GREY),
                 (".data (RW)", PURPLE), (".bss (in headers only)", PURPLE_D)]
    y = 72
    for name, col in file_rows:
        b.append(seg(fx, y, 190, 40, name, col, size=11))
        y += 42
    # arrows to VA
    vx = 480
    b.append(text(vx + 95, 58, "process VA", GREY, 12, 700))
    va_rows = [("[stack]", PURPLE, "rw-"), ("mmap: libc, ld.so", GREY, "r-x"),
               ("[heap]", TEAL, "rw-"), (".bss (zero-filled)", PURPLE_D, "rw-"),
               (".data", PURPLE, "rw-"), (".text + .rodata", GREY, "r-x")]
    y = 72
    for name, col, pr in va_rows:
        b.append(seg(vx, y, 200, 40, name, col, size=11))
        b.append(perm(vx + 205, y + 20, pr, GREY))
        y += 42
    b.append(arrow(fx + 190, 92 + 42 * 2 + 20, vx, 72 + 42 * 5 + 20, GREY, 1.6))
    b.append(text((fx + 190 + vx) / 2, 194, "kernel honours", GREY, 10, 600))
    b.append(text((fx + 190 + vx) / 2, 208, "LOAD headers", GREY, 10, 600))
    b.append(text(W / 2, H - 14,
                  ".bss has memsz > filesz \u2014 the kernel zero-fills the extra",
                  LIGHT, 11, 500))
    write("figures/elf-load.svg",
          svg(W, H, "".join(b), "ELF load"))


# ── 03 stack ──────────────────────────────────────────────────────────────────
def fig_stack_frame():
    W, H = 640, 460
    b = [text(W / 2, 28, "A single stack frame (System V x86-64 ABI)",
              GREY, 15, 700)]
    bx, bw = 180, 300
    rows = [
        ("caller args 7,8,9\u2026", "first 6 in registers", GREY_D, 46),
        ("return address", "pushed by call", PURPLE, 40),
        ("saved RBP of caller", "push %rbp  \u2190 %rbp", GREY, 46),
        ("callee-saved regs", "rbx, r12-r15 if used", GREY_D, 40),
        ("local variables", "\u2026", GREY, 60),
        ("alignment padding", "16-byte aligned  \u2190 %rsp", GREY_D, 40),
    ]
    y = 56
    for label, sub, col, h in rows:
        b.append(seg(bx, y, bw, h, label, col, sub=sub, size=12))
        y += h + 5
    b.append(text(bx - 14, 56 + 12, "higher", LIGHT, 10, 600, anchor="end"))
    b.append(text(bx - 14, y - 20, "lower", LIGHT, 10, 600, anchor="end"))
    b.append(arrow(bx - 30, 80, bx - 30, y - 24, GREY, 1.6))
    b.append(text(W / 2, H - 16,
                  "stack grows downward; args in rdi,rsi,rdx,rcx,r8,r9; "
                  "return in rax", LIGHT, 10.5, 500))
    write("figures/stack-frame.svg",
          svg(W, H, "".join(b), "Stack frame"))


def fig_stack_canary():
    W, H = 720, 360
    b = [text(W / 2, 28, "Stack canary: overflow trips the guard before return",
              GREY, 15, 700)]

    def panel(x, title, canary):
        b.append(text(x + 130, 58, title, GREY, 12, 700))
        rows = [("return address", PURPLE), ("saved rbp", GREY_D)]
        if canary:
            rows.append(("CANARY (random)", AMBER))
        rows.append(("locals / buffers", GREY))
        y = 76
        for name, col in rows:
            tc = INK_DARK if col == AMBER else WHITE
            b.append(seg(x, y, 260, 44, name, col, tcol=tc, size=12))
            if canary and name.startswith("CANARY"):
                b.append(text(x + 260 + 10, y + 22, "checked", TEAL, 10, 700,
                              anchor="start"))
                b.append(text(x + 260 + 10, y + 34, "before ret", TEAL, 10, 700,
                              anchor="start"))
            y += 48
    panel(40, "-fno-stack-protector", False)
    panel(410, "-fstack-protector-strong", True)
    b.append(text(180, H - 16, "overflow silently overwrites ret",
                  RED, 10.5, 600))
    b.append(text(540, H - 16, "overflow hits canary \u2192 __stack_chk_fail",
                  TEAL, 10.5, 600))
    write("figures/stack-canary.svg",
          svg(W, H, "".join(b), "Stack canary"))


# ── 04 heap / malloc ─────────────────────────────────────────────────────────
def fig_malloc_paths():
    W, H = 820, 400
    b = [text(W / 2, 28, "malloc(N): which path?", GREY, 16, 700)]
    b.append(box(330, 54, 160, 44, ["malloc(N)"], PURPLE, size=13))
    b.append(box(560, 130, 220, 60, ["mmap() region", "one VMA per alloc",
                                     "munmap on free"], GREY, size=11, lh=15))
    b.append(arrow(430, 98, 620, 130, GREY, 1.8))
    b.append(text(560, 112, "N \u2265 128 KiB", GREY, 10, 700))
    b.append(box(40, 130, 240, 60, ["tcache (per-thread)",
                                    "64 LIFO bins, lock-free"], TEAL, size=11,
                 lh=15))
    b.append(arrow(360, 98, 160, 130, GREY, 1.8))
    b.append(text(200, 112, "small & cached", TEAL, 10, 700))
    b.append(box(300, 210, 240, 150,
                 ["arena (brk-grown)", "", "fastbins", "small / large bins",
                  "unsorted bin", "top chunk (wilderness)"], GREY_D, size=11,
                 lh=22))
    b.append(arrow(380, 98, 400, 210, GREY, 1.8))
    b.append(text(470, 150, "else lock arena", GREY_D, 10, 700))
    b.append(arrow(420, 360, 420, 384, GREY, 1.6))
    b.append(text(420, 392, "sbrk / mmap when the top chunk is too small",
                  LIGHT, 10.5, 500))
    write("figures/malloc-paths.svg",
          svg(W, H, "".join(b), "malloc paths"))


def fig_chunk():
    W, H = 720, 360
    b = [text(W / 2, 28, "A glibc chunk: in-use vs free", GREY, 15, 700)]

    def panel(x, title, rows, col_hi):
        b.append(text(x + 130, 58, title, GREY, 12, 700))
        y = 76
        for name, col in rows:
            b.append(seg(x, y, 260, 40, name, col, size=11.5))
            y += 44
    panel(40, "allocated", [
        ("prev_size", GREY_D), ("size | A M P", PURPLE),
        ("payload  \u2190 malloc returns here", TEAL),
        ("\u2026 padding to 16B", GREY)], TEAL)
    panel(420, "free (in a bin)", [
        ("prev_size", GREY_D), ("size | A 0 P", PURPLE),
        ("fd  (next free)", AMBER), ("bk  (prev free)", AMBER)], AMBER)
    b.append(text(W / 2, H - 14,
                  "16 B of metadata per allocation; free chunks store fd/bk "
                  "inside the old payload", LIGHT, 10.5, 500))
    write("figures/chunk.svg", svg(W, H, "".join(b), "Chunk"))


def fig_bins():
    rules_fig(
        "figures/bins.svg",
        "Freelist bins by chunk size",
        [("16..1032 B", "tcache (per-thread LIFO)"),
         ("16..88 B", "fastbin (LIFO, no coalesce)"),
         ("16..512 B", "smallbin (exact size)"),
         ("\u2265 1024 B", "largebin (size-ordered)"),
         ("just freed", "unsorted bin"),
         ("top of heap", "top chunk / wilderness")],
        note="free(p) routes the chunk to a bin by size",
        lhs_hdr="size", rhs_hdr="destination")


def fig_brk_vs_mmap():
    W, H = 760, 320
    b = [text(W / 2, 28, "Why ptmalloc uses both brk and mmap", GREY, 15, 700)]
    # brk contiguous
    b.append(text(170, 60, "brk heap (one VMA)", GREY, 12, 700))
    rows = [("in-use", GREY), ("free", LIGHT), ("in-use", GREY),
            ("top chunk", TEAL)]
    y = 78
    for name, col in rows:
        tc = INK_DARK if col == LIGHT else WHITE
        b.append(seg(60, y, 220, 40, name, col, tcol=tc, size=11.5))
        y += 44
    b.append(text(170, y + 6, "shrinks only from the top", RED, 10, 600))
    # mmap separate
    b.append(text(560, 60, "mmap chunks (many VMAs)", GREY, 12, 700))
    for i in range(3):
        b.append(seg(470, 78 + i * 60, 220, 44, f"alloc {i+1}", PURPLE,
                     size=11.5))
        b.append(text(700, 78 + i * 60 + 22, "\u2192 munmap", TEAL, 9.5, 600,
                      anchor="start"))
    b.append(text(560, y + 6, "each returnable on its own free", TEAL, 10, 600))
    write("figures/brk-vs-mmap.svg",
          svg(W, H, "".join(b), "brk vs mmap"))


# ── 05 mmap ───────────────────────────────────────────────────────────────────
def fig_mmap_quadrants():
    W, H = 780, 420
    b = [text(W / 2, 28, "mmap: MAP_PRIVATE/SHARED \u00d7 anonymous/file",
              GREY, 15, 700)]
    cells = [
        (60, 70, "PRIVATE \u00b7 anon", ["zero pages, CoW",
                                     "malloc-style memory"], TEAL),
        (410, 70, "PRIVATE \u00b7 file", ["read file lazily",
                                      "writes stay local"], GREY),
        (60, 230, "SHARED \u00b7 anon", ["shared after fork",
                                     "(or memfd/shm)"], GREY),
        (410, 230, "SHARED \u00b7 file", ["writes go to the file",
                                      "shared page cache"], PURPLE),
    ]
    for x, y, ttl, rows, col in cells:
        b.append(box(x, y, 310, 130, [ttl, ""] + rows, col, size=12, lh=24,
                     rx=10))
    write("figures/mmap-quadrants.svg",
          svg(W, H, "".join(b), "mmap quadrants"))


def fig_file_mapping():
    W, H = 760, 340
    b = [text(W / 2, 28, "File mapping: pages served from the page cache",
              GREY, 15, 700)]
    b.append(text(W / 2, 60, "disk file img.bmp", GREY, 12, 700))
    for i in range(3):
        b.append(seg(180 + i * 140, 74, 130, 40, f"page {i}", GREY_D, size=11))
    b.append(text(W / 2, 200, "process virtual address space", GREY, 12, 700))
    for i in range(3):
        x = 180 + i * 140
        b.append(seg(x, 214, 130, 40, f"p + {i}\u00d74K", PURPLE, size=11))
        b.append(arrow(x + 65, 114, x + 65, 214, GREY, 1.6, dash="4 4"))
    b.append(text(W / 2, H - 14,
                  "pages pulled in on demand (major fault, then cache hits are "
                  "free)", LIGHT, 10.5, 500))
    write("figures/file-mapping.svg",
          svg(W, H, "".join(b), "File mapping"))


def fig_mmap_lifecycle():
    W, H = 900, 240
    b = [text(W / 2, 28, "The lifecycle of an anonymous mapping", GREY, 15, 700)]
    steps = [
        ("mmap", "VMA, no PTEs", GREY),
        ("touch", "fault \u2192 frame", TEAL),
        ("madvise\nDONTNEED", "drop frames", AMBER),
        ("mprotect", "flip perms", PURPLE),
        ("munmap", "VMA gone", GREY_D),
    ]
    bw = 150
    xs = [30 + i * 172 for i in range(5)]
    for x, (ttl, sub, col) in zip(xs, steps):
        tc = INK_DARK if col == AMBER else WHITE
        b.append(box(x, 90, bw, 64, [ttl, sub], col, tcol=tc, size=12, lh=17))
        if x != xs[-1]:
            b.append(arrow(x + bw, 122, x + 172, 122, GREY, 1.8))
    write("figures/mmap-lifecycle.svg",
          svg(W, H, "".join(b), "mmap lifecycle"))


# ── 06 brk ────────────────────────────────────────────────────────────────────
def fig_brk():
    W, H = 700, 340
    b = [text(W / 2, 28, "The program break (sbrk grows the heap up)",
              GREY, 15, 700)]

    def panel(x, title, brk_y):
        b.append(text(x + 130, 58, title, GREY, 12, 700))
        b.append(seg(x, 76, 260, 44, ".bss / .data", GREY_D, size=11))
        b.append(text(x - 10, 88, "start_brk", LIGHT, 9.5, 600, anchor="end"))
        b.append(seg(x, 122, 260, brk_y, "in-use heap", TEAL, size=11))
        b.append(text(x - 10, 122 + brk_y - 8, "brk(0)", LIGHT, 9.5, 600,
                      anchor="end"))
        b.append(seg(x, 122 + brk_y + 4, 260, 150 - brk_y,
                     "virtual hole (unused)", LIGHT, tcol=INK_DARK, size=11))
    panel(40, "before sbrk", 44)
    panel(400, "after sbrk(+page)", 96)
    b.append(arrow(310, 170, 400, 170, PURPLE, 2))
    b.append(text(355, 156, "sbrk", PURPLE, 10, 700))
    write("figures/brk.svg", svg(W, H, "".join(b), "Program break"))


# ── 07 paging / swap ─────────────────────────────────────────────────────────
def fig_swap():
    W, H = 820, 260
    b = [text(W / 2, 28, "Anonymous page lifecycle \u2192 swap", GREY, 15, 700)]
    steps = [("created", "malloc + touch", TEAL),
             ("active", "recently used", PURPLE),
             ("inactive", "aged by LRU", GREY),
             ("swapped out", "written to disk", GREY_D)]
    bw = 165
    xs = [24 + i * 195 for i in range(4)]
    for x, (ttl, sub, col) in zip(xs, steps):
        b.append(box(x, 84, bw, 60, [ttl, sub], col, size=12, lh=17))
        if x != xs[-1]:
            b.append(arrow(x + bw, 114, x + 195, 114, GREY, 1.8))
    b.append(path(f"M{xs[3]+bw/2} 144 C{xs[3]+bw/2} 210 {xs[0]+bw/2} 210 "
                  f"{xs[0]+bw/2} 144", AMBER, 2, arrow_end=True))
    b.append(text(W / 2, 200, "next access \u2192 major fault reads it back in",
                  AMBER, 11, 700))
    b.append(text(W / 2, H - 12,
                  "only anonymous pages swap; file pages are just dropped & "
                  "re-read", LIGHT, 10.5, 500))
    write("figures/swap.svg", svg(W, H, "".join(b), "Swap"))


def fig_page_cache():
    W, H = 780, 240
    b = [text(W / 2, 28, "The page cache absorbs file writes", GREY, 15, 700)]
    steps = [("write(fd,buf,n)", "user call", GREY),
             ("copy \u2192 page cache", "marked dirty (RAM)", PURPLE),
             ("returns now", "no disk I/O yet", TEAL),
             ("writeback later", "kworker \u00b7 fsync forces", GREY_D)]
    bw = 168
    xs = [24 + i * 188 for i in range(4)]
    for x, (ttl, sub, col) in zip(xs, steps):
        b.append(box(x, 84, bw, 60, [ttl, sub], col, size=11.5, lh=17))
        if x != xs[-1]:
            b.append(arrow(x + bw, 114, x + 188, 114, GREY, 1.8))
    b.append(text(W / 2, H - 14,
                  "look at MemAvailable, not MemFree \u2014 cache is reclaimable",
                  LIGHT, 10.5, 500))
    write("figures/page-cache.svg",
          svg(W, H, "".join(b), "Page cache"))


def fig_buddy():
    W, H = 720, 340
    b = [text(W / 2, 28, "Buddy allocator: split & coalesce powers of two",
              GREY, 15, 700)]
    y = 60
    widths = [(1, 560), (2, 276), (4, 134)]
    labels = ["order 4  (16 pages)", "split \u2192 8 | 8", "split \u2192 4 | 4"]
    for i, ((n, w), lab) in enumerate(zip(widths, labels)):
        x = 80
        for j in range(n):
            col = TEAL if (i == 2 and j == 0) else (PURPLE if i > 0 else GREY)
            b.append(seg(x, y, w, 44, "" if n > 1 else "one 16-page block", col,
                         size=11))
            x += w + 8
        b.append(text(660, y + 22, lab, GREY, 10.5, 600, anchor="start")
                 if False else text(80, y - 8, lab, LIGHT, 10, 600,
                                    anchor="start"))
        y += 66
    b.append(text(140, y + 4, "return first 4 pages (order 2), mark used",
                  TEAL, 10.5, 600, anchor="start"))
    b.append(text(W / 2, H - 12,
                  "free coalesces buddies recursively back up the orders",
                  LIGHT, 10.5, 500))
    write("figures/buddy.svg", svg(W, H, "".join(b),
                                                      "Buddy allocator"))


# ── 08 process syscalls ──────────────────────────────────────────────────────
def fig_process_lifecycle():
    W, H = 820, 240
    b = [text(W / 2, 28, "The life of a process", GREY, 16, 700)]
    steps = [("fork / clone", "newborn child", GREY),
             ("running", "R / S / D / T", PURPLE),
             ("zombie (Z)", "exit code held", AMBER),
             ("reaped", "parent wait()", TEAL)]
    bw = 168
    xs = [24 + i * 195 for i in range(4)]
    for x, (ttl, sub, col) in zip(xs, steps):
        tc = INK_DARK if col == AMBER else WHITE
        b.append(box(x, 88, bw, 62, [ttl, sub], col, tcol=tc, size=12, lh=17))
        if x != xs[-1]:
            b.append(arrow(x + bw, 119, x + 195, 119, GREY, 1.8))
    b.append(text(xs[1] + bw / 2, 172, "execve replaces the image", GREY, 10,
                  600))
    b.append(text(W / 2, H - 14,
                  "an unreaped child is a zombie; an orphan is re-parented to "
                  "init (PID 1)", LIGHT, 10.5, 500))
    write("figures/process-lifecycle.svg",
          svg(W, H, "".join(b), "Process lifecycle"))


def fig_fork_cow():
    W, H = 820, 320
    b = [text(W / 2, 28, "fork(): copy-on-write shares frames until a write",
              GREY, 15, 700)]

    def frames(x, y, cols, tag):
        for i, c in enumerate(cols):
            b.append(seg(x + i * 62, y, 58, 40, f"F{i+1}", c, size=11))
        b.append(text(x - 10, y + 20, tag, GREY, 11, 700, anchor="end"))
    b.append(text(150, 62, "after fork (no copies)", GREY, 12, 700))
    frames(150, 80, [GREY, GREY, GREY], "parent")
    frames(150, 130, [GREY, GREY, GREY], "child")
    b.append(text(150 + 90, 186, "all PTEs read-only, refcount 2",
                  GREY, 10, 600))
    b.append(arrow(360, 140, 430, 140, PURPLE, 2))
    b.append(text(395, 126, "child writes F2", PURPLE, 10, 700))
    b.append(text(600, 62, "after the write", GREY, 12, 700))
    frames(560, 80, [GREY, GREY, GREY], "parent")
    b.append(seg(560, 130, 58, 40, "F1", GREY, size=11))
    b.append(seg(560 + 62, 130, 58, 40, "F2'", TEAL, size=11))
    b.append(seg(560 + 124, 130, 58, 40, "F3", GREY, size=11))
    b.append(text(560 - 10, 150, "child", GREY, 11, 700, anchor="end"))
    b.append(text(560 + 90, 186, "only F2 was copied", TEAL, 10, 600))
    write("figures/fork-cow.svg",
          svg(W, H, "".join(b), "fork copy-on-write"))


def fig_signal():
    W, H = 760, 300
    b = [text(W / 2, 28, "Signal delivery", GREY, 15, 700)]
    b.append(box(300, 54, 160, 44, ["kernel queues", "a signal"], PURPLE,
                 size=11, lh=15))
    b.append(box(300, 130, 160, 40, ["in thread mask?"], GREY, size=11))
    b.append(arrow(380, 98, 380, 130, GREY, 1.8))
    b.append(box(540, 130, 180, 40, ["stays pending"], GREY_D, size=11))
    b.append(arrow(460, 150, 540, 150, GREY, 1.6))
    b.append(text(500, 142, "yes", GREY, 10, 700))
    outs = [("SIG_DFL", "term / core / stop", RED),
            ("SIG_IGN", "discarded", GREY_D),
            ("handler", "save ctx \u2192 run \u2192 sigreturn", TEAL)]
    for i, (ttl, sub, col) in enumerate(outs):
        x = 40 + i * 240
        b.append(box(x, 220, 210, 56, [ttl, sub], col, size=11, lh=15))
        b.append(arrow(380, 170, x + 105, 220, GREY, 1.4))
    b.append(text(300, 196, "no \u2192 deliver", GREY, 10, 700, anchor="end"))
    write("figures/signal-delivery.svg",
          svg(W, H, "".join(b), "Signal delivery"))


# ── 09 threads ────────────────────────────────────────────────────────────────
def fig_thread_memory():
    W, H = 780, 340
    b = [text(W / 2, 28, "Threads: one address space, private stacks + TLS",
              GREY, 15, 700)]
    b.append(rrect(40, 56, 700, 240, CARD_BG, rx=12, stroke=GREY_D, sw=1.75))
    b.append(text(W / 2, 84, "PROCESS  (one PML4 / CR3)", LIGHT, 12, 700))
    b.append(box(70, 104, 640, 44,
                 ["text \u00b7 rodata \u00b7 data \u00b7 bss \u00b7 heap \u00b7 mmap \u00b7 fds  "
                  "\u2014  SHARED"], TEAL, size=11.5))
    for i in range(3):
        x = 90 + i * 210
        b.append(box(x, 170, 180, 108,
                     [f"thread {i+1}", "", "stack", "registers / PC", "TLS"],
                     PURPLE, size=11, lh=19))
    b.append(text(W / 2, H - 14,
                  "kernel schedules tasks sharing a TGID; signal mask is "
                  "per-thread", LIGHT, 10.5, 500))
    write("figures/thread-memory.svg",
          svg(W, H, "".join(b), "Thread memory"))


def fig_thread_stack():
    W, H = 560, 420
    b = [text(W / 2, 28, "A non-main thread's stack VMA", GREY, 15, 700)]
    bx, bw = 170, 250
    rows = [("TCB (glibc)", GREY_D, 46), ("TLS data", PURPLE, 46),
            ("stack frames", GREY, 96), ("free / unused", LIGHT, 60),
            ("guard page (---p)", RED, 44)]
    y = 56
    for name, col, h in rows:
        tc = INK_DARK if col == LIGHT else WHITE
        b.append(seg(bx, y, bw, h, name, col, tcol=tc, size=12))
        y += h + 6
    b.append(text(bx - 14, 70, "high", LIGHT, 10, 600, anchor="end"))
    b.append(text(bx + bw / 2, 56 + 46 + 46 + 40, "grows down", WHITE, 10, 600))
    b.append(text(W / 2, H - 14,
                  "default 8 MiB mmap + 4 KiB PROT_NONE guard; touching the "
                  "guard \u2192 SIGSEGV", LIGHT, 10, 500))
    write("figures/thread-stack.svg",
          svg(W, H, "".join(b), "Thread stack"))


def fig_futex():
    W, H = 780, 300
    b = [text(W / 2, 28, "Futex: fast userspace path, kernel only on contention",
              GREY, 15, 700)]
    b.append(box(60, 90, 300, 90,
                 ["FAST PATH (no syscall)", "atomic CAS on the futex word",
                  "0 \u2192 1  : lock acquired"], TEAL, size=12, lh=22, rx=10))
    b.append(box(420, 90, 300, 90,
                 ["SLOW PATH (contended)", "FUTEX_WAIT: sleep if still locked",
                  "FUTEX_WAKE: wake a waiter"], PURPLE, size=12, lh=22, rx=10))
    b.append(arrow(360, 135, 420, 135, GREY, 2))
    b.append(text(390, 122, "CAS fails", RED, 9.5, 700))
    b.append(text(W / 2, H - 16,
                  "word: 0=free, 1=locked, 2=locked+waiters \u00b7 kernel keys "
                  "waiters by physical address", LIGHT, 10, 500))
    write("figures/futex.svg", svg(W, H, "".join(b), "Futex"))


# ── 10 IPC ────────────────────────────────────────────────────────────────────
def fig_shared_memory():
    W, H = 760, 320
    b = [text(W / 2, 28, "Shared memory: one object, two mappings", GREY, 15,
              700)]
    b.append(box(60, 90, 200, 70, ["process A", "mmap(MAP_SHARED)"], PURPLE,
                 size=12, lh=18))
    b.append(box(500, 90, 200, 70, ["process B", "mmap(MAP_SHARED)"], PURPLE,
                 size=12, lh=18))
    b.append(box(300, 200, 160, 70, ["shm object", "tmpfs / memfd", "frames"],
                 TEAL, size=11, lh=17))
    b.append(arrow(180, 160, 340, 200, GREY, 1.8))
    b.append(arrow(580, 160, 420, 200, GREY, 1.8))
    b.append(text(W / 2, H - 14,
                  "shm_open + ftruncate + mmap; or memfd_create passed over "
                  "SCM_RIGHTS", LIGHT, 10.5, 500))
    write("figures/shared-memory.svg",
          svg(W, H, "".join(b), "Shared memory"))


# ── 11 protection ─────────────────────────────────────────────────────────────
def fig_defenses():
    W, H = 720, 430
    b = [text(W / 2, 28, "The user-space memory-protection stack", GREY, 15,
              700)]
    rows = [
        ("ASLR", "randomise the layout", PURPLE),
        ("NX / W^X", "data pages non-executable", GREY),
        ("stack canaries", "detect overflow before ret", GREY),
        ("RELRO (full)", "GOT/PLT read-only after load", GREY),
        ("Fortify Source", "checked memcpy/sprintf/\u2026", GREY_D),
        ("PIE", "executable base randomised too", PURPLE),
    ]
    y = 56
    for name, sub, col in rows:
        b.append(box(120, y, 480, 50, [f"{name}  \u2014  {sub}"], col, size=12,
                     rx=8))
        y += 58
    b.append(text(W / 2, H - 14,
                  "check with checksec --file=./a.out", LIGHT, 11, 500))
    write("figures/defenses.svg",
          svg(W, H, "".join(b), "Protection stack"))


# ── 13 advanced ───────────────────────────────────────────────────────────────
def fig_numa():
    W, H = 780, 320
    b = [text(W / 2, 28, "NUMA: local DRAM is fast, remote costs ~2\u00d7",
              GREY, 15, 700)]
    for i, (x, node) in enumerate([(60, 0), (440, 1)]):
        b.append(box(x, 70, 280, 90,
                     [f"CPU socket {node}", f"cores {i*16}..{i*16+15}",
                      "L1 / L2 / L3"], PURPLE if i == 0 else GREY, size=12,
                     lh=20))
        b.append(box(x + 40, 200, 200, 60, [f"NUMA node {node}", "local DRAM"],
                     TEAL if i == 0 else GREY_D, size=12, lh=17))
        b.append(arrow(x + 140, 160, x + 140, 200, GREY, 1.8))
    b.append(path("M340 115 C390 115 390 115 440 115", GREY, 2))
    b.append(arrow(340, 115, 380, 115, GREY, 2))
    b.append(arrow(440, 115, 400, 115, GREY, 2))
    b.append(text(390, 100, "QPI / UPI", GREY, 10, 700))
    b.append(text(W / 2, H - 12,
                  "first-touch policy: a page lands on the node of the CPU that "
                  "first writes it", LIGHT, 10.5, 500))
    write("figures/numa.svg", svg(W, H, "".join(b), "NUMA"))


def fig_huge_pages():
    W, H = 940, 280
    b = [text(W / 2, 28, "Huge pages: one TLB entry covers far more",
              GREY, 15, 700)]
    rows = [("4 KiB page", "walk 4 levels \u00b7 1 TLB entry / 4 KiB", GREY, 200),
            ("2 MiB page", "walk 3 levels \u00b7 512\u00d7 coverage", PURPLE, 360),
            ("1 GiB page", "walk 2 levels \u00b7 almost free TLB", TEAL, 560)]
    y = 66
    for name, sub, col, w in rows:
        b.append(box(90, y, w, 46, [name], col, size=12.5, rx=6))
        b.append(text(90 + w + 14, y + 23, sub, GREY, 10.5, 600,
                      anchor="start"))
        y += 60
    b.append(text(W / 2, H - 12,
                  "THP (automatic) or explicit MAP_HUGETLB \u2014 wins when the "
                  "working set is huge", LIGHT, 10.5, 500))
    write("figures/huge-pages.svg",
          svg(W, H, "".join(b), "Huge pages"))


# ── 14 allocators ─────────────────────────────────────────────────────────────
def fig_allocators():
    rules_fig(
        "figures/allocators.svg",
        "Five allocators, five trade-offs",
        [("bump / arena", "O(1), no per-object free"),
         ("pool freelist", "fixed size, O(1) push/pop"),
         ("slab", "same-size sets, cache-aware"),
         ("freelist", "variable size, coalescing"),
         ("buddy", "power-of-2, OS page level")],
        note="real allocators = per-thread cache + size classes + page backing",
        lhs_hdr="allocator", rhs_hdr="what it is best at")


# ── second pass: more diagrams ───────────────────────────────────────────────
def fig_guide_map():
    W, H = 900, 460
    b = [box(250, 46, 400, 56, ["ONE-STOP GUIDE \u00b7 LINUX MEMORY",
                                 "kernel + glibc + hardware"], PURPLE, size=13,
             lh=18)]
    row1 = [("CPU / MMU", "caches \u00b7 TLB"),
            ("virtual memory", "pages \u00b7 page tables"),
            ("process space", "/proc \u00b7 segments"),
            ("allocators", "malloc \u00b7 mmap \u00b7 arenas")]
    xs = [36, 262, 488, 714]
    for x, (t, s) in zip(xs, row1):
        b.append(box(x, 168, 172, 62, [t, s], GREY, size=11, lh=15))
        b.append(arrow(450, 102, x + 86, 168, GREY, 1.3))
    row2 = [("syscalls", "fork \u00b7 exec \u00b7 clone"),
            ("threads", "pthreads \u00b7 TLS \u00b7 futex"),
            ("IPC", "shm \u00b7 pipe \u00b7 socket")]
    xs2 = [110, 364, 618]
    for i, (x, (t, s)) in enumerate(zip(xs2, row2)):
        b.append(box(x, 320, 180, 62, [t, s], GREY_D, size=11, lh=15))
        b.append(arrow(xs[i] + 86, 230, x + 90, 320, GREY, 1.2, dash="4 4"))
    b.append(text(W / 2, H - 14,
                  "every topic is an elaboration of the address-space map",
                  LIGHT, 11, 500))
    write("figures/guide-map.svg", svg(W, H, "".join(b), "Guide map"))


def fig_how_to_use():
    W, H = 860, 240
    b = [text(W / 2, 28, "How to use this guide", GREY, 15, 700)]
    steps = [("Read", "the section README", GREY),
             ("Run", "edit the examples", PURPLE),
             ("Inspect", "/proc \u00b7 gdb \u00b7 strace \u00b7 perf", TEAL)]
    xs = [40, 320, 600]
    bw = 220
    for x, (t, s, c) in zip(xs, steps):
        b.append(box(x, 74, bw, 64, [t, s], c, size=12, lh=17))
        if x != 600:
            b.append(arrow(x + bw, 106, x + bw + 60, 106, GREY, 2))
    b.append(box(320, 176, 220, 44, ["sketch what happened"], GREY_D, size=11))
    b.append(arrow(430, 138, 430, 176, GREY, 1.8))
    write("figures/how-to-use.svg", svg(W, H, "".join(b), "How to use"))


def fig_malloc_syscalls():
    W, H = 820, 300
    b = [text(W / 2, 26, "M1 \u2014 malloc is two syscalls in disguise",
              GREY, 15, 700)]
    b.append(box(40, 84, 190, 60, ["user", "malloc(40)"], GREY, size=12, lh=17))
    b.append(box(290, 84, 230, 60,
                 ["glibc ptmalloc", "find a free chunk in a bin", "(no syscall)"],
                 PURPLE, size=11, lh=16))
    b.append(arrow(230, 114, 290, 114, GREY, 2))
    b.append(text(560, 60, "no chunk fits \u2192 grow the heap", GREY, 10, 600))
    b.append(box(580, 78, 210, 46, ["small \u2192 brk(new_break)"], TEAL, size=11))
    b.append(box(580, 138, 210, 46, ["big \u2192 mmap(anon)"], TEAL, size=11))
    b.append(arrow(520, 104, 580, 98, GREY, 1.6))
    b.append(arrow(520, 124, 580, 158, GREY, 1.6))
    b.append(text(W / 2, H - 16,
                  "small requests are served from the cached arena with no "
                  "syscall at all", LIGHT, 10.5, 500))
    write("figures/malloc-syscalls.svg", svg(W, H, "".join(b), "malloc syscalls"))


def fig_virtual_physical():
    W, H = 800, 360
    b = [text(W / 2, 26, "Virtual \u2260 physical: same address, different frames",
              GREY, 15, 700)]
    b.append(box(40, 84, 180, 50, ["process A", "0x400000"], PURPLE, size=11,
                 lh=15))
    b.append(box(40, 170, 180, 50, ["process A", "0x401000"], PURPLE, size=11,
                 lh=15))
    b.append(box(580, 84, 180, 50, ["process B", "0x400000"], GREY, size=11,
                 lh=15))
    b.append(box(580, 170, 180, 50, ["process B", "0x401000"], GREY, size=11,
                 lh=15))
    b.append(box(330, 74, 140, 40, ["frame F1"], TEAL, size=11))
    b.append(box(330, 148, 140, 40, ["frame F2"], AMBER, tcol=INK_DARK,
                 size=11))
    b.append(box(330, 224, 140, 40, ["frame F3"], GREY_D, size=11))
    b.append(arrow(220, 109, 330, 96, GREY, 1.5))
    b.append(arrow(220, 195, 330, 172, GREY, 1.5))
    b.append(arrow(580, 109, 470, 244, GREY, 1.5))
    b.append(arrow(580, 195, 470, 172, GREY, 1.5))
    b.append(text(400, 138, "shared frame", AMBER, 9.5, 700))
    b.append(text(W / 2, H - 14,
                  "per-process page tables map identical virtual addresses to "
                  "distinct (or shared) frames", LIGHT, 10, 500))
    write("figures/virtual-physical.svg",
          svg(W, H, "".join(b), "Virtual vs physical"))


def fig_alignment():
    W, H = 820, 320
    b = [text(W / 2, 26, "Alignment & endianness", GREY, 15, 700)]
    b.append(text(200, 66, "aligned load @ 0x1008", TEAL, 11, 700))
    b.append(box(60, 82, 280, 44, ["one 8-byte access"], TEAL, size=11))
    b.append(text(610, 66, "unaligned @ 0x1009", RED, 11, 700))
    b.append(box(475, 82, 155, 44, ["7 bytes\u2026"], GREY, size=11))
    b.append(box(632, 82, 155, 44, ["\u2026 1 byte"], GREY, size=11))
    b.append(text(610, 142, "straddles two lines \u2192 two loads", RED, 10, 600))
    b.append(text(W / 2, 202, "little-endian: uint32 0x11223344", GREY, 12, 700))
    for i, bv in enumerate(["44", "33", "22", "11"]):
        b.append(box(282 + i * 66, 218, 60, 40, [bv],
                     PURPLE if i == 0 else GREY, size=12))
    b.append(text(312, 274, "low addr", LIGHT, 10, 600))
    b.append(text(510, 274, "high addr", LIGHT, 10, 600))
    write("figures/alignment.svg",
          svg(W, H, "".join(b), "Alignment & endianness"))


def fig_va_split():
    W, H = 900, 280
    b = [text(W / 2, 28, "The 48-bit canonical virtual address", GREY, 15, 700)]
    fields = [("sign ext", "63..48", GREY_D, 130), ("PML4", "47..39", PURPLE,
              110), ("PDPT", "38..30", PURPLE, 110), ("PD", "29..21", PURPLE,
              110), ("PT", "20..12", PURPLE, 110), ("offset", "11..0", GREY,
              140)]
    x, y = 40, 64
    for name, bits, col, w in fields:
        b.append(box(x, y, w, 50, [name], col, size=11.5, rx=4))
        b.append(text(x + w / 2, y - 8, bits, LIGHT, 9, 600))
        x += w + 2
    desc = [("PML4", "index into the top-level table"),
            ("PDPT", "\u2192 page-directory-pointer table"),
            ("PD", "\u2192 page directory"),
            ("PT", "\u2192 page table"),
            ("offset", "byte within the 4 KiB page")]
    for i, (k, v) in enumerate(desc):
        b.append(text(60, 150 + i * 22, k, PURPLE, 10.5, 700, anchor="start",
                      mono=True))
        b.append(text(170, 150 + i * 22, v, GREY, 10.5, 600, anchor="start"))
    write("figures/va-split.svg",
          svg(W, H, "".join(b), "VA split"))


def fig_pte():
    W, H = 960, 300
    b = [text(W / 2, 28, "Page-table entry (PTE) bits", GREY, 15, 700)]
    fields = [("NX", "63", RED, 60), ("reserved", "62..52", GREY_D, 100),
              ("PFN", "51..12", TEAL, 200), ("OS", "11..9", GREY_D, 80),
              ("G", "8", GREY, 44), ("PS", "7", GREY, 44), ("D", "6", GREY, 44),
              ("A", "5", GREY, 44), ("PCD", "4", GREY, 54), ("PWT", "3", GREY,
              54), ("U/S", "2", GREY, 54), ("R/W", "1", GREY, 54),
              ("P", "0", PURPLE, 40)]
    x, y = 20, 64
    for name, bit, col, w in fields:
        b.append(box(x, y, w, 46, [name], col, size=10, rx=3))
        b.append(text(x + w / 2, y - 8, bit, LIGHT, 8.5, 600))
        x += w + 2
    notes = ["P = present", "R/W = writable", "U/S = user vs kernel",
             "A / D = accessed / dirty (HW-set)",
             "G = global (survives CR3 reload)", "PS = 1 \u2192 huge page here",
             "NX = 1 \u2192 non-executable (data)", "PFN = physical frame number"]
    for i, n in enumerate(notes):
        b.append(text(40 + (i % 2) * 470, 150 + (i // 2) * 24, "\u2022 " + n,
                      GREY, 10.5, 600, anchor="start"))
    write("figures/pte.svg", svg(W, H, "".join(b), "PTE"))


def fig_per_process_tables():
    W, H = 740, 320
    b = [text(W / 2, 26, "Per-process page tables can share a frame",
              GREY, 15, 700)]
    b.append(box(40, 90, 160, 50, ["process A", "CR3 \u2192 PML4 A"], PURPLE,
                 size=11, lh=15))
    b.append(box(40, 190, 160, 50, ["process B", "CR3 \u2192 PML4 B"], GREY,
                 size=11, lh=15))
    b.append(box(300, 90, 150, 50, ["\u2026 tables \u2026"], GREY_D, size=11))
    b.append(box(300, 190, 150, 50, ["\u2026 tables \u2026"], GREY_D, size=11))
    b.append(box(550, 140, 150, 50, ["frame F7"], TEAL, size=12))
    b.append(arrow(200, 115, 300, 115, GREY, 1.6))
    b.append(arrow(200, 215, 300, 215, GREY, 1.6))
    b.append(arrow(450, 115, 550, 160, GREY, 1.6))
    b.append(arrow(450, 215, 550, 175, GREY, 1.6))
    b.append(text(625, 210, "refcount = 2", TEAL, 10, 700))
    b.append(text(625, 224, "(shared library)", TEAL, 10, 600))
    write("figures/per-process-tables.svg",
          svg(W, H, "".join(b), "Per-process tables"))


def fig_initial_stack():
    W, H = 520, 410
    b = [text(W / 2, 26, "The initial stack the kernel builds", GREY, 15, 700)]
    rows = [("argc", GREY_D, 36), ("argv[] pointers", GREY, 40),
            ("envp[] pointers", GREY, 40), ("auxv[] key/value", PURPLE, 44),
            ("envp strings", GREY_D, 40), ("argv strings", GREY_D, 40),
            ("AT_RANDOM, padding", LIGHT, 40)]
    bx, bw, y = 150, 240, 56
    for name, col, h in rows:
        tc = INK_DARK if col == LIGHT else WHITE
        b.append(seg(bx, y, bw, h, name, col, tcol=tc, size=11.5))
        y += h + 5
    b.append(text(bx - 14, 64, "top", LIGHT, 10, 600, anchor="end"))
    b.append(text(W / 2, H - 14,
                  "getauxval(3) reads auxv; argv/envp point into the strings "
                  "below", LIGHT, 10, 500))
    write("figures/initial-stack.svg",
          svg(W, H, "".join(b), "Initial stack"))


def fig_call_stack():
    W, H = 560, 470
    b = [text(W / 2, 26, "The call stack (grows down)", GREY, 15, 700)]
    rows = [("args / env / auxv", "set up at execve", GREY_D, 44),
            ("frame: main", "\u2190 %rbp", GREY, 40),
            ("return address", "", PURPLE_D, 32),
            ("frame: foo", "pushed by call", GREY, 40),
            ("return address", "", PURPLE_D, 32),
            ("frame: bar", "", GREY, 40),
            ("unused (mapped)", "\u2190 %rsp", LIGHT, 44),
            ("guard page", "PROT_NONE \u2192 SIGSEGV", RED, 44)]
    bx, bw, y = 160, 270, 52
    for name, sub, col, h in rows:
        tc = INK_DARK if col == LIGHT else WHITE
        b.append(seg(bx, y, bw, h, name, col, sub=(sub or None), tcol=tc,
                     size=11.5))
        y += h + 5
    b.append(arrow(bx - 26, 68, bx - 26, y - 22, GREY, 1.6))
    b.append(text(bx - 32, 64, "high", LIGHT, 9, 600, anchor="end"))
    b.append(text(bx - 32, y - 22, "low", LIGHT, 9, 600, anchor="end"))
    write("figures/call-stack.svg",
          svg(W, H, "".join(b), "Call stack"))


def fig_top_chunk():
    W, H = 900, 240
    b = [text(W / 2, 28, "The heap after a while: the top chunk (wilderness)",
              GREY, 15, 700)]
    segs = [("in-use", GREY, 120), ("free", LIGHT, 110), ("in-use", GREY, 120),
            ("in-use", GREY, 120), ("free", LIGHT, 110), ("TOP CHUNK", TEAL,
            230)]
    x, y = 30, 92
    for name, col, w in segs:
        tc = INK_DARK if col == LIGHT else WHITE
        b.append(seg(x, y, w, 50, name, col, tcol=tc, size=11))
        x += w + 2
    b.append(arrow(x - 2, y + 74, x - 2, y + 52, GREY, 1.6))
    b.append(text(x - 2, y + 88, "program break (sbrk(0))", GREY, 10, 600,
                  anchor="end"))
    b.append(text(W / 2, y - 12,
                  "only the top chunk can grow via sbrk / mmap", LIGHT, 10.5,
                  600))
    write("figures/top-chunk.svg",
          svg(W, H, "".join(b), "Top chunk"))


def fig_arenas():
    W, H = 820, 320
    b = [text(W / 2, 26, "Arenas: per-thread heaps cut lock contention",
              GREY, 15, 700)]
    cols = [("main arena", "grown by brk", PURPLE, 40),
            ("arena 1", "grown by mmap", GREY, 310),
            ("arena 2", "grown by mmap", GREY, 580)]
    for name, sub, col, x in cols:
        b.append(box(x, 70, 200, 52, ["freelist (bins)"], col, size=11))
        b.append(box(x, 130, 200, 44, ["top chunk"], GREY_D, size=11))
        b.append(text(x + 100, 194, sub, LIGHT, 10, 600))
        b.append(box(x, 214, 200, 44, [name + " lock"], col, size=11))
    b.append(text(W / 2, H - 14,
                  "a thread pins to an arena; many arenas can balloon VSZ far "
                  "past the working set", LIGHT, 10.5, 500))
    write("figures/arenas.svg", svg(W, H, "".join(b), "Arenas"))


def fig_physical_ram():
    W, H = 640, 420
    b = [text(W / 2, 26, "What lives in physical RAM", GREY, 15, 700)]
    rows = [("free pages", "on buddy free lists", GREY_D, 50),
            ("anonymous pages", "heap \u00b7 stack \u00b7 bss \u00b7 anon mmap", TEAL, 56),
            ("file-backed (page cache)", "mmap'd files \u00b7 read() buffers",
             PURPLE, 56),
            ("slab / kernel", "inode & network buffers", GREY, 50),
            ("reserved / kernel text", "", GREY_D, 44)]
    bx, bw, y = 150, 340, 56
    for name, sub, col, h in rows:
        b.append(seg(bx, y, bw, h, name, col, sub=(sub or None), size=11.5))
        y += h + 6
    b.append(text(W / 2, H - 16,
                  "reclaimable cache is why MemAvailable \u226b MemFree",
                  LIGHT, 10.5, 500))
    write("figures/physical-ram.svg",
          svg(W, H, "".join(b), "Physical RAM"))


def fig_tls():
    W, H = 680, 340
    b = [text(W / 2, 26, "Thread-local storage: one copy per thread",
              GREY, 15, 700)]
    for i, (x, lab) in enumerate([(90, "thread A"), (390, "thread B")]):
        b.append(text(x + 100, 60, lab + " TCB", GREY, 12, 700))
        yy = 76
        for name, col in [("dtv pointer", GREY_D), ("per_thread_x", PURPLE),
                          ("per_thread_y", PURPLE)]:
            b.append(seg(x, yy, 200, 44, name, col, size=11.5))
            yy += 48
        b.append(text(x + 100, yy + 6,
                      "%fs in " + ("A" if i == 0 else "B") + " points here",
                      TEAL, 10, 600))
    b.append(text(W / 2, H - 14,
                  "the FS register points at the TCB; each thread's vars are "
                  "distinct words", LIGHT, 10, 500))
    write("figures/tls.svg", svg(W, H, "".join(b), "TLS"))


def fig_ipc_options():
    W, H = 880, 360
    b = [text(W / 2, 26, "Choosing an IPC mechanism by data shape",
              GREY, 15, 700)]
    b.append(box(340, 54, 200, 44, ["how big is each message?"], PURPLE,
                 size=11))
    b.append(text(210, 122, "small (bytes)", GREY, 11, 700))
    for i, s in enumerate(["signals \u00b7 eventfd \u00b7 signalfd", "pipes / FIFO",
                           "UNIX sockets", "message queues"]):
        b.append(box(60, 140 + i * 46, 300, 38, [s], GREY, size=11))
    b.append(arrow(400, 98, 210, 140, GREY, 1.4))
    b.append(text(670, 122, "large / streaming", GREY, 11, 700))
    for i, s in enumerate(["mmap + shared memory", "memfd_create",
                           "MAP_SHARED file"]):
        b.append(box(520, 140 + i * 46, 300, 38, [s], TEAL, size=11))
    b.append(arrow(480, 98, 670, 140, GREY, 1.4))
    b.append(text(W / 2, H - 14,
                  "pass fds with socketpair + SCM_RIGHTS; wake a peer with "
                  "eventfd + epoll", LIGHT, 10, 500))
    write("figures/ipc-options.svg",
          svg(W, H, "".join(b), "IPC options"))


def fig_io_uring():
    W, H = 760, 280
    b = [text(W / 2, 26, "io_uring: two mmap'd rings shared with the kernel",
              GREY, 15, 700)]
    b.append(text(180, 64, "process VA", GREY, 12, 700))
    b.append(text(580, 64, "kernel", GREY, 12, 700))
    b.append(box(60, 84, 240, 54, ["SQ ring (mmap)", "submission queue"],
                 PURPLE, size=11, lh=15))
    b.append(box(460, 84, 240, 54, ["sq_entries[]"], GREY, size=11))
    b.append(box(60, 164, 240, 54, ["CQ ring (mmap)", "completion queue"],
                 TEAL, size=11, lh=15))
    b.append(box(460, 164, 240, 54, ["cq_entries[]"], GREY, size=11))
    b.append(arrow(300, 105, 460, 105, GREY, 1.7))
    b.append(arrow(460, 118, 300, 118, GREY, 1.7))
    b.append(arrow(300, 185, 460, 185, GREY, 1.7))
    b.append(arrow(460, 198, 300, 198, GREY, 1.7))
    b.append(text(380, 98, "shared", LIGHT, 9, 600))
    b.append(text(380, 178, "shared", LIGHT, 9, 600))
    b.append(text(W / 2, H - 14,
                  "queue requests with no syscall; io_uring_enter submits and "
                  "harvests completions", LIGHT, 10, 500))
    write("figures/io-uring.svg", svg(W, H, "".join(b), "io_uring"))


def fig_bump():
    W, H = 760, 200
    b = [text(W / 2, 28, "Bump allocator: alloc just advances a pointer",
              GREY, 15, 700)]
    b.append(seg(60, 82, 300, 50, "used", PURPLE, size=12))
    b.append(seg(360, 82, 340, 50, "free", LIGHT, tcol=INK_DARK, size=12))
    b.append(text(62, 150, "base", LIGHT, 10, 600, anchor="start"))
    b.append(arrow(360, 76, 420, 76, TEAL, 1.8))
    b.append(text(390, 66, "bump ptr", TEAL, 10, 700))
    b.append(text(698, 150, "end", LIGHT, 10, 600, anchor="end"))
    b.append(text(W / 2, H - 14,
                  "O(1) alloc, no per-object free \u2014 drop the whole region at "
                  "once", LIGHT, 10.5, 500))
    write("figures/bump.svg",
          svg(W, H, "".join(b), "Bump allocator"))


def fig_pool():
    W, H = 720, 270
    b = [text(W / 2, 26, "Pool allocator: fixed-size slots + freelist",
              GREY, 15, 700)]
    for i in range(4):
        col = GREY if i in (1, 3) else LIGHT
        tc = INK_DARK if col == LIGHT else WHITE
        b.append(box(80 + i * 150, 84, 130, 54, [f"slot {i}"], col, tcol=tc,
                     size=12))
    b.append(path("M145 138 C145 180 445 180 445 138", TEAL, 1.8,
                  arrow_end=True))
    b.append(text(300, 196, "free: 0 \u2192 2 \u2192 NULL (threaded through unused "
                  "slots)", TEAL, 10, 600))
    b.append(text(W / 2, H - 16,
                  "alloc = pop head \u00b7 free = push head \u00b7 both O(1)",
                  LIGHT, 10.5, 500))
    write("figures/pool.svg",
          svg(W, H, "".join(b), "Pool allocator"))


def fig_freelist():
    W, H = 860, 220
    b = [text(W / 2, 28, "Freelist allocator: header + payload chunks",
              GREY, 15, 700)]
    x = 40
    for i in range(3):
        b.append(seg(x, 82, 70, 54, "hdr", PURPLE, size=10))
        x += 72
        col = GREY if i % 2 == 0 else LIGHT
        tc = WHITE if i % 2 == 0 else INK_DARK
        b.append(seg(x, 82, 180, 54, "payload", col, tcol=tc, size=11))
        x += 182
    b.append(text(40, 152, "base", LIGHT, 10, 600, anchor="start"))
    b.append(text(x - 2, 152, "top", LIGHT, 10, 600, anchor="end"))
    b.append(text(W / 2, H - 16,
                  "the header holds size + free flag; free(p) reads it at "
                  "p - sizeof(header) and coalesces neighbours", LIGHT, 10, 500))
    write("figures/freelist.svg",
          svg(W, H, "".join(b), "Freelist allocator"))


def fig_kernel_user():
    W, H = 600, 320
    b = [text(W / 2, 26, "The canonical address split (x86-64)", GREY, 15, 700)]
    bx, bw = 170, 260
    rows = [("kernel space", "CPL0 only \u00b7 in every process", GREY_D, 60,
             "0xFFFFFFFFFFFFFFFF"),
            ("non-canonical hole", "unmapped 47-bit gap", LIGHT, 50,
             "0xFFFF800000000000"),
            ("user space", "your code \u00b7 per process", PURPLE, 70,
             "0x0000800000000000")]
    y = 54
    for name, sub, col, h, a in rows:
        tc = INK_DARK if col == LIGHT else WHITE
        b.append(seg(bx, y, bw, h, name, col, sub=sub, tcol=tc, size=12))
        b.append(addr(bx - 12, y + 12, a))
        y += h + 6
    b.append(addr(bx - 12, y + 2, "0x0"))
    b.append(text(W / 2, H - 16,
                  "a syscall switches to ring 0 and the kernel half becomes "
                  "addressable", LIGHT, 10, 500))
    write("figures/kernel-user-split.svg",
          svg(W, H, "".join(b), "Kernel/user split"))


def fig_thread_stacks():
    W, H = 560, 380
    b = [text(W / 2, 26, "Where thread stacks live", GREY, 15, 700)]
    bx, bw = 150, 270
    rows = [("main thread stack", "top of the address space", PURPLE, 54),
            ("mmap region", "", GREY_D, 40),
            ("thread 3 stack", "", GREY, 40),
            ("thread 2 stack", "", GREY, 40),
            ("thread 1 stack", "8 MiB + guard each", GREY, 44),
            ("\u2026 heap, libs below \u2026", "", LIGHT, 40)]
    y = 54
    for name, sub, col, h in rows:
        tc = INK_DARK if col == LIGHT else WHITE
        b.append(seg(bx, y, bw, h, name, col, sub=(sub or None), tcol=tc,
                     size=11.5))
        y += h + 5
    b.append(text(W / 2, H - 14,
                  "each pthread gets its own mmap'd stack with a PROT_NONE "
                  "guard page", LIGHT, 10, 500))
    write("figures/thread-stacks.svg",
          svg(W, H, "".join(b), "Thread stacks"))


def fig_pthread_create():
    W, H = 760, 360
    b = [text(W / 2, 26, "pthread_create is a wrapper around clone(2)",
              GREY, 15, 700)]
    b.append(box(280, 54, 200, 44, ["pthread_create(fn)"], PURPLE, size=12))
    steps = [("allocate stack", "mmap + guard page", GREY),
             ("allocate TCB", "at the top of the stack", GREY),
             ("set up TLS + signal mask", "", GREY),
             ("clone(CLONE_VM | \u2026)", "shares VM, files, fds, sighand", TEAL)]
    y = 120
    for t, s, col in steps:
        b.append(arrow(380, y - 18, 380, y, GREY, 1.6))
        b.append(box(220, y, 320, 46, [t, s] if s else [t], col, size=11,
                     lh=15))
        y += 60
    b.append(text(W / 2, H - 16,
                  "child_tid is cleared on exit, then futex_wake lets "
                  "pthread_join return", LIGHT, 10, 500))
    write("figures/pthread-create.svg",
          svg(W, H, "".join(b), "pthread_create"))


# ── NASM / assembly-specific figures ─────────────────────────────────────────
def fig_register_file():
    W, H = 900, 428
    b = [text(W / 2, 28, "The x86-64 general-purpose register file",
              GREY, 16, 700)]
    names = ["rax", "rbx", "rcx", "rdx", "rsi", "rdi", "rbp", "rsp",
             "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15"]
    roles = {"rax": "return / accum", "rdi": "arg 1", "rsi": "arg 2",
             "rdx": "arg 3", "rcx": "arg 4", "r8": "arg 5", "r9": "arg 6",
             "rsp": "stack pointer", "rbp": "frame pointer"}
    argset = {"rax", "rdi", "rsi", "rdx", "rcx", "r8", "r9"}
    ptr = {"rsp", "rbp"}
    cw, ch, gx, gy, x0, y0 = 190, 54, 20, 14, 40, 64
    for i, n in enumerate(names):
        r, c = divmod(i, 4)
        x, y = x0 + c * (cw + gx), y0 + r * (ch + gy)
        col = TEAL if n in ptr else (PURPLE if n in argset else GREY)
        b.append(seg(x, y, cw, ch, n, col, sub=roles.get(n, "general"),
                     size=13))
    yb = y0 + 4 * (ch + gy) + 4
    b.append(seg(40, yb, 400, 48, "rip", GREY_D,
                 sub="next instruction address", size=13))
    b.append(seg(460, yb, 400, 48, "rflags", GREY_D,
                 sub="status + control flags", size=13))
    write("figures/register-file.svg",
          svg(W, H, "".join(b), "Register file"))


def fig_rax_family():
    W, H = 820, 300
    b = [text(W / 2, 28, "One register, four names: RAX / EAX / AX / AH\u00b7AL",
              GREY, 16, 700)]
    x0, full = 60, 700
    b.append(text(x0, 60, "63", LIGHT, 9, 600))
    b.append(text(x0 + full, 60, "0", LIGHT, 9, 600))
    b.append(text(x0 + full / 2, 60, "31", LIGHT, 9, 600))
    b.append(text(x0 + full * 3 / 4, 60, "15", LIGHT, 9, 600))
    b.append(text(x0 + full * 7 / 8, 60, "7", LIGHT, 9, 600))
    b.append(seg(x0, 70, full, 46, "RAX  (64-bit)", GREY, size=13))
    b.append(seg(x0 + full / 2, 124, full / 2, 44, "EAX  (low 32)", PURPLE,
                 size=12))
    b.append(seg(x0 + full * 3 / 4, 176, full / 4, 42, "AX  (low 16)", TEAL,
                 size=12))
    b.append(seg(x0 + full * 3 / 4, 224, full / 8, 40, "AH", AMBER,
                 tcol=INK_DARK, size=11))
    b.append(seg(x0 + full * 7 / 8, 224, full / 8, 40, "AL", AMBER,
                 tcol=INK_DARK, size=11))
    b.append(text(W / 2, H - 14,
                  "writing EAX zeroes the upper 32 bits; writing AX / AL leaves "
                  "the rest intact", LIGHT, 10.5, 500))
    write("figures/rax-family.svg", svg(W, H, "".join(b), "RAX family"))


def fig_rflags():
    W, H = 880, 300
    b = [text(W / 2, 28, "RFLAGS \u2014 the status bits that drive branches",
              GREY, 16, 700)]
    bits = [("OF", "11", TEAL), ("DF", "10", GREY), ("IF", "9", GREY),
            ("TF", "8", GREY_D), ("SF", "7", PURPLE), ("ZF", "6", PURPLE),
            ("AF", "4", GREY), ("PF", "2", PURPLE), ("CF", "0", PURPLE)]
    x, cw = 40, 88
    for name, bit, col in bits:
        b.append(box(x, 72, cw, 50, [name], col, size=13))
        b.append(text(x + cw / 2, 62, "bit " + bit, LIGHT, 9, 600))
        x += cw + 2
    notes = ["CF  carry / unsigned overflow", "ZF  result was zero",
             "SF  sign (top bit) of result", "OF  signed overflow",
             "PF  low-byte parity", "AF  BCD adjust carry",
             "DF  string direction (0 = up)", "IF  interrupts enabled"]
    for i, n in enumerate(notes):
        b.append(text(60 + (i % 2) * 430, 150 + (i // 2) * 24, "\u2022 " + n,
                      GREY, 11, 600, anchor="start"))
    write("figures/rflags.svg", svg(W, H, "".join(b), "RFLAGS"))


def fig_cmp_jcc():
    W, H = 780, 300
    b = [text(W / 2, 26, "cmp / test set the flags; jcc reads them",
              GREY, 15, 700)]
    b.append(box(60, 78, 250, 60, ["cmp rax, rbx",
                 "computes rax - rbx,", "throws the result away"], GREY,
                 size=11, lh=16))
    b.append(box(60, 172, 250, 44, ["sets ZF SF CF OF"], PURPLE, size=12))
    b.append(arrow(185, 138, 185, 172, GREY, 1.8))
    b.append(box(470, 74, 270, 68, ["je  \u2192 ZF=1     (equal)",
                 "jl  \u2192 SF\u2260OF     (signed <)",
                 "jb  \u2192 CF=1     (unsigned <)"], TEAL, size=11, lh=17))
    b.append(box(470, 172, 270, 44, ["jcc reads those flags"], GREY_D,
                 size=12))
    b.append(arrow(310, 194, 470, 194, GREY, 1.8))
    b.append(text(390, 184, "flags", LIGHT, 9, 600))
    b.append(text(W / 2, H - 16,
                  "test does AND, cmp does SUB \u2014 neither writes its operands, "
                  "they only set flags", LIGHT, 10, 500))
    write("figures/cmp-jcc.svg", svg(W, H, "".join(b), "cmp and jcc"))


def fig_push_pop():
    W, H = 780, 330
    b = [text(W / 2, 26, "push and pop move RSP by 8", GREY, 15, 700)]
    bx, bw = 300, 200
    slots = ["(older frames)", "return address", "saved rbp", "local var",
             "rax  \u2190 just pushed"]
    for i, s in enumerate(slots):
        col = PURPLE if "pushed" in s else GREY
        b.append(seg(bx, 70 + i * 44, bw, 40, s, col, size=12))
    ry = 70 + 4 * 44 + 20
    b.append(arrow(bx - 44, ry, bx - 8, ry, TEAL, 2))
    b.append(text(bx - 50, ry, "rsp", TEAL, 12, 700, anchor="end"))
    b.append(text(bx + bw + 16, 90, "high addr", LIGHT, 10, 600,
                  anchor="start"))
    b.append(text(bx + bw + 16, ry, "low addr", LIGHT, 10, 600,
                  anchor="start"))
    b.append(text(W / 2, H - 16,
                  "push: rsp -= 8 then store  \u00b7  pop: load then rsp += 8  \u00b7  "
                  "the stack grows downward", LIGHT, 10, 500))
    write("figures/push-pop.svg", svg(W, H, "".join(b), "push and pop"))


def fig_sysv_args():
    W, H = 820, 320
    b = [text(W / 2, 26, "System V AMD64: how arguments are passed",
              GREY, 15, 700)]
    for i, r in enumerate(["rdi", "rsi", "rdx", "rcx", "r8", "r9"]):
        b.append(box(40 + i * 128, 74, 116, 52, [r, f"arg {i + 1}"], PURPLE,
                     size=12, lh=15))
    b.append(text(W / 2, 162, "args 7+  \u2192  pushed on the stack, right to left",
                  GREY, 12, 700))
    b.append(box(300, 188, 220, 44, ["return value  \u2192  rax"], TEAL, size=12))
    b.append(text(W / 2, H - 16,
                  "rdx can return a second word; for varargs, al holds the "
                  "vector-register count", LIGHT, 10, 500))
    write("figures/sysv-args.svg", svg(W, H, "".join(b), "SysV arguments"))


def fig_caller_callee():
    W, H = 820, 300
    b = [text(W / 2, 26, "Caller-saved vs callee-saved registers",
              GREY, 15, 700)]
    b.append(text(226, 64, "caller-saved (volatile)", AMBER, 12, 700))
    for i, r in enumerate(["rax", "rcx", "rdx", "rsi", "rdi", "r8", "r9",
                           "r10", "r11"]):
        b.append(box(40 + (i % 3) * 128, 80 + (i // 3) * 46, 116, 40, [r],
                     AMBER, tcol=INK_DARK, size=12))
    b.append(text(632, 64, "callee-saved (preserved)", TEAL, 12, 700))
    for i, r in enumerate(["rbx", "rbp", "rsp", "r12", "r13", "r14", "r15"]):
        b.append(box(470 + (i % 3) * 116, 80 + (i // 3) * 46, 104, 40, [r],
                     TEAL, size=12))
    b.append(text(226, 236, "the callee may clobber these", LIGHT, 10, 600))
    b.append(text(632, 236, "the callee must restore these", LIGHT, 10, 600))
    b.append(text(W / 2, H - 14,
                  "need a caller-saved value to survive a call? save it "
                  "yourself first", LIGHT, 10, 500))
    write("figures/caller-callee.svg",
          svg(W, H, "".join(b), "Caller/callee saved"))


def fig_addressing():
    W, H = 860, 280
    b = [text(W / 2, 26, "Effective address:  [ base + index*scale + disp ]",
              GREY, 15, 700)]
    parts = [("base", "rbx", "any GPR", PURPLE),
             ("index", "rsi", "any GPR but rsp", TEAL),
             ("scale", "\u00d74", "1 2 4 8", AMBER),
             ("disp", "+16", "constant", GREY)]
    x = 60
    for k, (name, ex, note, col) in enumerate(parts):
        w = 160
        tc = INK_DARK if col == AMBER else WHITE
        b.append(box(x, 80, w, 54, [name, ex], col, tcol=tc, size=12, lh=16))
        b.append(text(x + w / 2, 150, note, LIGHT, 10, 600))
        if k < 3:
            b.append(text(x + w + 20, 107, "+", GREY, 16, 700))
        x += w + 40
    b.append(box(260, 200, 340, 44,
                 ["\u2192 one memory operand, computed by the CPU"], GREY_D,
                 size=12))
    b.append(text(W / 2, H - 14,
                  "mov eax, [rbx + rsi*4 + 16] loads int element rsi of an "
                  "array at rbx+16", LIGHT, 10, 500))
    write("figures/addressing.svg", svg(W, H, "".join(b), "Addressing modes"))


def fig_muldiv():
    W, H = 780, 300
    b = [text(W / 2, 26, "mul and div use the RDX:RAX pair", GREY, 15, 700)]
    b.append(text(200, 64, "mul rbx   (unsigned)", PURPLE, 12, 700))
    b.append(box(60, 80, 120, 44, ["rax"], GREY, size=12))
    b.append(text(200, 102, "\u00d7 rbx", GREY, 12, 700))
    b.append(box(250, 80, 100, 44, ["rbx"], GREY, size=12))
    b.append(arrow(205, 124, 205, 158, GREY, 1.8))
    b.append(box(60, 162, 140, 44, ["rdx  (high)"], TEAL, size=11))
    b.append(box(210, 162, 140, 44, ["rax  (low)"], TEAL, size=11))
    b.append(text(575, 64, "div rbx", PURPLE, 12, 700))
    b.append(box(430, 80, 130, 44, ["rdx:rax"], GREY, size=12))
    b.append(text(590, 102, "\u00f7 rbx", GREY, 12, 700))
    b.append(box(620, 80, 100, 44, ["rbx"], GREY, size=12))
    b.append(arrow(575, 124, 575, 158, GREY, 1.8))
    b.append(box(430, 162, 140, 44, ["rax  quotient"], TEAL, size=11))
    b.append(box(580, 162, 140, 44, ["rdx  remainder"], TEAL, size=11))
    b.append(text(W / 2, H - 16,
                  "before div set rdx: xor it for unsigned, or cqo to "
                  "sign-extend rax", LIGHT, 10, 500))
    write("figures/muldiv.svg", svg(W, H, "".join(b), "mul and div"))


def fig_syscall_path():
    W, H = 780, 320
    b = [text(W / 2, 26, "A Linux syscall: user \u2192 kernel \u2192 back",
              GREY, 15, 700)]
    b.append(box(60, 78, 270, 68, ["set rax = syscall number",
                 "args in rdi rsi rdx r10 r8 r9", "execute  syscall"], PURPLE,
                 size=10.5, lh=16))
    b.append(box(450, 78, 270, 68, ["CPU enters ring 0 (MSR_LSTAR)",
                 "runs the sys_* handler", "no IDT lookup"], GREY, size=10.5,
                 lh=16))
    b.append(arrow(330, 100, 450, 100, GREY, 2))
    b.append(text(390, 90, "syscall", LIGHT, 9, 600))
    b.append(box(450, 190, 270, 44, ["result placed in rax"], TEAL, size=12))
    b.append(box(60, 190, 270, 44, ["check rax; negative = -errno"], GREY_D,
                 size=11))
    b.append(arrow(450, 212, 330, 212, GREY, 2))
    b.append(text(390, 202, "sysret", LIGHT, 9, 600))
    b.append(arrow(585, 146, 585, 190, GREY, 1.6))
    b.append(text(W / 2, H - 16,
                  "syscall is far cheaper than the legacy int 0x80 \u2014 it uses "
                  "MSRs, not the IDT", LIGHT, 10, 500))
    write("figures/syscall-path.svg", svg(W, H, "".join(b), "Syscall path"))


def fig_simd_regs():
    W, H = 820, 320
    b = [text(W / 2, 26, "SIMD registers: XMM \u2286 YMM \u2286 ZMM", GREY, 15, 700)]
    x0 = 60
    b.append(seg(x0, 72, 700, 44, "ZMM0  (512-bit, AVX-512)", GREY, size=12))
    b.append(seg(x0, 120, 350, 42, "YMM0  (256-bit, AVX)", PURPLE, size=12))
    b.append(seg(x0, 166, 175, 40, "XMM0  (128-bit, SSE)", TEAL, size=11))
    b.append(text(x0, 232, "one XMM as 4 packed float32 lanes:", GREY, 11, 700,
                  anchor="start"))
    for i in range(4):
        b.append(box(x0 + i * 92, 246, 88, 40, [f"f{i}"], AMBER, tcol=INK_DARK,
                     size=11))
    b.append(text(W / 2, H - 14,
                  "one instruction (addps) adds all four lanes at once \u2014 "
                  "data-level parallelism", LIGHT, 10, 500))
    write("figures/simd-regs.svg", svg(W, H, "".join(b), "SIMD registers"))


def fig_instr_format():
    W, H = 900, 250
    b = [text(W / 2, 28, "Anatomy of an x86-64 instruction", GREY, 15, 700)]
    parts = [("prefix", "0-4 B", GREY_D), ("REX", "0-1 B", AMBER),
             ("opcode", "1-3 B", PURPLE), ("ModRM", "0-1 B", TEAL),
             ("SIB", "0-1 B", TEAL), ("disp", "0/1/2/4", GREY),
             ("imm", "0/1/2/4/8", GREY)]
    x = 30
    for name, sz, col in parts:
        w = 118
        tc = INK_DARK if col == AMBER else WHITE
        b.append(box(x, 74, w, 54, [name, sz], col, tcol=tc, size=11.5, lh=15))
        x += w + 3
    b.append(text(W / 2, 162,
                  "only the opcode is mandatory; most instructions are "
                  "2\u20134 bytes", GREY, 11, 600))
    b.append(text(W / 2, H - 16,
                  "mov [rdi+rsi*4+1], eax = REX + opcode + ModRM + SIB + disp8",
                  LIGHT, 10, 500))
    write("figures/instr-format.svg",
          svg(W, H, "".join(b), "Instruction format"))


def fig_rex_byte():
    W, H = 760, 240
    b = [text(W / 2, 28, "The REX prefix byte", GREY, 15, 700)]
    cells = [("0100", "fixed", GREY_D, 150), ("W", "64-bit op", PURPLE, 110),
             ("R", "reg ext", TEAL, 110), ("X", "index ext", TEAL, 110),
             ("B", "r/m ext", TEAL, 110)]
    x = 50
    for name, sub, col, w in cells:
        b.append(box(x, 78, w, 54, [name, sub], col, size=12, lh=15))
        x += w + 2
    b.append(text(W / 2, H - 34,
                  "W=1 selects 64-bit operands; R / X / B supply the high bit to "
                  "reach r8\u2013r15", LIGHT, 10.5, 500))
    write("figures/rex-byte.svg", svg(W, H, "".join(b), "REX byte"))


def fig_modrm():
    W, H = 680, 240
    b = [text(W / 2, 28, "The ModR/M byte", GREY, 15, 700)]
    cells = [("mod  (2 bits)", "addressing mode", PURPLE),
             ("reg  (3 bits)", "register / opcode ext", TEAL),
             ("r/m  (3 bits)", "register or memory", GREY)]
    x = 60
    for head, sub, col in cells:
        b.append(box(x, 78, 180, 60, [head, sub], col, size=11, lh=16))
        x += 188
    b.append(text(W / 2, H - 34,
                  "mod=11 \u2192 register operand; mod=00/01/10 \u2192 memory with "
                  "0/1/4-byte disp", LIGHT, 10.5, 500))
    write("figures/modrm.svg", svg(W, H, "".join(b), "ModRM byte"))


def fig_sib():
    W, H = 680, 240
    b = [text(W / 2, 28, "The SIB byte (scaled-index addressing)",
              GREY, 15, 700)]
    cells = [("scale  (2 bits)", "1 2 4 8", AMBER),
             ("index  (3 bits)", "index register", TEAL),
             ("base  (3 bits)", "base register", GREY)]
    x = 60
    for head, sub, col in cells:
        tc = INK_DARK if col == AMBER else WHITE
        b.append(box(x, 78, 180, 60, [head, sub], col, tcol=tc, size=11, lh=16))
        x += 188
    b.append(text(W / 2, H - 34,
                  "present only when r/m=100; encodes [base + index*scale] like "
                  "[rbx + rsi*4]", LIGHT, 10.5, 500))
    write("figures/sib.svg", svg(W, H, "".join(b), "SIB byte"))


def fig_got_plt():
    W, H = 820, 300
    b = [text(W / 2, 26, "Lazy binding through the PLT and GOT",
              GREY, 15, 700)]
    b.append(box(40, 92, 180, 50, ["call printf@plt"], PURPLE, size=12))
    b.append(box(300, 92, 200, 50, ["PLT stub", "jmp *[GOT entry]"], GREY,
                 size=11, lh=15))
    b.append(box(580, 62, 200, 46, ["GOT \u2192 resolver", "(first call only)"],
                 AMBER, tcol=INK_DARK, size=11, lh=15))
    b.append(box(580, 132, 200, 46, ["GOT \u2192 real printf", "(after resolve)"],
                 TEAL, size=11, lh=15))
    b.append(arrow(220, 117, 300, 117, GREY, 1.8))
    b.append(arrow(500, 110, 580, 85, GREY, 1.6))
    b.append(arrow(500, 124, 580, 155, GREY, 1.6))
    b.append(text(W / 2, H - 40,
                  "the first call jumps to the dynamic linker, which patches the "
                  "GOT;", LIGHT, 10.5, 500))
    b.append(text(W / 2, H - 22,
                  "every later call jumps straight to the resolved address",
                  LIGHT, 10.5, 500))
    write("figures/got-plt.svg", svg(W, H, "".join(b), "GOT and PLT"))


def fig_elf_layout():
    W, H = 560, 420
    b = [text(W / 2, 26, "ELF file layout", GREY, 15, 700)]
    rows = [("ELF header", "entry point \u00b7 e_phoff", PURPLE, 46),
            ("program headers", "LOAD segments (loader)", TEAL, 44),
            (".text", "machine code", GREY, 38),
            (".rodata", "read-only constants", GREY, 38),
            (".data", "initialised globals", GREY, 38),
            (".bss", "zero-init, no file bytes", GREY_D, 38),
            ("section headers", "symbol / section names", GREY_D, 44)]
    bx, bw, y = 150, 300, 52
    for name, sub, col, h in rows:
        b.append(seg(bx, y, bw, h, name, col, sub=sub, size=11.5))
        y += h + 5
    b.append(text(W / 2, H - 14,
                  "the loader reads program headers; the linker reads section "
                  "headers", LIGHT, 10, 500))
    write("figures/elf-layout.svg", svg(W, H, "".join(b), "ELF layout"))


def fig_idt():
    W, H = 800, 320
    b = [text(W / 2, 26, "Interrupt dispatch through the IDT", GREY, 15, 700)]
    b.append(box(40, 96, 180, 66, ["event", "exception / IRQ /", "int n"],
                 PURPLE, size=11, lh=15))
    b.append(box(300, 92, 190, 76, ["IDT", "[vector] \u2192 handler",
                 "+ CPL / gate type"], GREY, size=11, lh=16))
    b.append(box(580, 62, 200, 44, ["#PF handler (14)"], TEAL, size=11))
    b.append(box(580, 122, 200, 44, ["timer IRQ (32)"], TEAL, size=11))
    b.append(box(580, 182, 200, 44, ["int 0x80 (128)"], TEAL, size=11))
    b.append(arrow(220, 129, 300, 129, GREY, 1.8))
    for yy in (84, 144, 204):
        b.append(arrow(490, 130, 580, yy, GREY, 1.4))
    b.append(text(W / 2, H - 16,
                  "the CPU pushes SS:RSP, RFLAGS, CS:RIP, then jumps to the "
                  "gated handler", LIGHT, 10, 500))
    write("figures/idt.svg", svg(W, H, "".join(b), "IDT dispatch"))


def fig_context_switch():
    W, H = 840, 300
    b = [text(W / 2, 26, "A context switch swaps register state via the kernel",
              GREY, 15, 700)]
    b.append(box(40, 92, 180, 62, ["process A", "running in CPU"], PURPLE,
                 size=11, lh=15))
    b.append(box(300, 64, 230, 50, ["save A's regs \u2192",
                 "A's kernel stack / TSS"], GREY, size=11, lh=15))
    b.append(box(300, 156, 230, 50, ["load B's regs \u2190",
                 "B's kernel stack / TSS"], GREY, size=11, lh=15))
    b.append(box(610, 156, 190, 62, ["process B", "runs (switch_to)"], TEAL,
                 size=11, lh=15))
    b.append(arrow(220, 118, 300, 92, GREY, 1.6))
    b.append(arrow(415, 114, 415, 156, GREY, 1.8))
    b.append(arrow(530, 182, 610, 186, GREY, 1.6))
    b.append(text(W / 2, H - 16,
                  "switching address spaces reloads CR3 and flushes "
                  "non-global TLB entries", LIGHT, 10, 500))
    write("figures/context-switch.svg",
          svg(W, H, "".join(b), "Context switch"))


def fig_process_states():
    W, H = 760, 320
    b = [text(W / 2, 26, "Process state machine", GREY, 15, 700)]
    b.append(box(300, 66, 160, 50, ["RUNNING"], PURPLE, size=12))
    b.append(box(80, 182, 160, 50, ["READY"], GREY, size=12))
    b.append(box(520, 182, 160, 50, ["BLOCKED"], AMBER, tcol=INK_DARK,
                 size=12))
    b.append(box(300, 256, 160, 46, ["ZOMBIE"], GREY_D, size=12))
    b.append(arrow(300, 108, 190, 182, GREY, 1.5))
    b.append(text(212, 138, "preempt", LIGHT, 9, 600))
    b.append(arrow(210, 182, 320, 112, GREY, 1.5))
    b.append(text(300, 150, "dispatch", LIGHT, 9, 600))
    b.append(arrow(430, 112, 560, 182, GREY, 1.5))
    b.append(text(520, 138, "wait I/O", LIGHT, 9, 600))
    b.append(arrow(520, 214, 240, 214, GREY, 1.5))
    b.append(text(380, 226, "I/O done \u2192 back to READY", LIGHT, 9, 600))
    b.append(arrow(380, 116, 380, 256, GREY, 1.5))
    b.append(text(404, 190, "exit", LIGHT, 9, 600))
    b.append(text(W / 2, H - 12,
                  "a blocked task wakes to READY, not straight to RUNNING \u2014 "
                  "the scheduler chooses next", LIGHT, 10, 500))
    write("figures/process-states.svg",
          svg(W, H, "".join(b), "Process states"))


def fig_spinlock():
    W, H = 780, 300
    b = [text(W / 2, 26, "A spinlock is one atomic compare-exchange",
              GREY, 15, 700)]
    card, w, h = code_card(50, 78,
                           [("acquire:", "dim"), ("  xor eax, eax   ; want 0",
                            "n"), ("  mov ecx, 1", "n"),
                            ("  lock cmpxchg [lk], ecx", "hi"),
                            ("  jnz acquire     ; retry", "n")],
                           "SPIN", GREY_D, LBL_BEFORE)
    b.append(card)
    xr = 50 + w + 56
    b.append(box(xr, 96, 230, 50, ["success \u2192 we own it", "(ZF=1, lock was 0)"],
                 TEAL, size=11, lh=15))
    b.append(box(xr, 166, 230, 50, ["fail \u2192 spin again",
                 "(someone else holds it)"], AMBER, tcol=INK_DARK, size=11,
                 lh=15))
    b.append(arrow(50 + w + 6, 118, xr, 121, GREY, 1.6))
    b.append(arrow(50 + w + 6, 138, xr, 191, GREY, 1.6))
    b.append(text(W / 2, H - 16,
                  "cmpxchg is atomic under the lock prefix; a futex lets waiters "
                  "sleep instead of burning CPU", LIGHT, 10, 500))
    write("figures/spinlock.svg", svg(W, H, "".join(b), "Spinlock"))


ALL = [
    # reused systems figures (assembly-relevant internals)
    fig_address_space,
    fig_hierarchy, fig_cache_line,
    fig_virtual_physical, fig_va_split, fig_pte, fig_page_walk,
    fig_tlb, fig_page_fault,
    fig_elf_load,
    fig_stack_frame, fig_call_stack,
    fig_malloc_paths, fig_chunk, fig_arenas, fig_brk_vs_mmap,
    fig_fork_cow, fig_signal,
    fig_futex,
    # NASM / assembly-specific
    fig_register_file, fig_rax_family, fig_rflags,
    fig_cmp_jcc, fig_push_pop,
    fig_sysv_args, fig_caller_callee,
    fig_addressing, fig_muldiv,
    fig_syscall_path, fig_simd_regs,
    fig_instr_format, fig_rex_byte, fig_modrm, fig_sib,
    fig_got_plt, fig_elf_layout,
    fig_idt, fig_context_switch, fig_process_states, fig_spinlock,
]

if __name__ == "__main__":
    for fn in ALL:
        fn()
    print(f"\nDone: {len(ALL)} figures generated.")
