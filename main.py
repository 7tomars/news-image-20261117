#!/usr/bin/env python3
"""Sum up 17 November's world news in one image.

Entry for make.fun bounty news-image-20261117. A small, fully self-contained
Python 3 program (standard library only, no network, deterministic) that
draws a one-page newspaper poster of Tuesday 17 November 2026 and writes it
to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png outside the grader).

Everything is rendered by this file: a raster canvas with 3x supersampling
for anti-aliasing, a hand-authored bitmap font (below) drawn at several
weights and sizes, and a PNG encoder built on zlib/struct. Two runs produce
byte-identical output because the picture is a pure function of constants.
"""

import os
import struct
import zlib
from binascii import crc32

# --------------------------------------------------------------------------
# Canvas
# --------------------------------------------------------------------------

W, H = 1024, 1024          # final image size
SS = 3                     # supersampling factor
SW, SH = W * SS, H * SS    # working canvas size

canvas = bytearray(SW * SH * 3)


def _px(x, y, rgb):
    i = (y * SW + x) * 3
    canvas[i] = rgb[0]
    canvas[i + 1] = rgb[1]
    canvas[i + 2] = rgb[2]


def fill_rect(x, y, w, h, rgb):
    """Fill a rectangle given in final-image coordinates (floats ok)."""
    x0 = max(0, int(round(x * SS)))
    y0 = max(0, int(round(y * SS)))
    x1 = min(SW, int(round((x + w) * SS)))
    y1 = min(SH, int(round((y + h) * SS)))
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(rgb) * (x1 - x0)
    for yy in range(y0, y1):
        i = (yy * SW + x0) * 3
        canvas[i:i + len(row)] = row


def fill_circle(cx, cy, r, rgb):
    x0 = max(0, int((cx - r) * SS) - 1)
    y0 = max(0, int((cy - r) * SS) - 1)
    x1 = min(SW, int((cx + r) * SS) + 2)
    y1 = min(SH, int((cy + r) * SS) + 2)
    rr = (r * SS) ** 2
    ccx, ccy = cx * SS, cy * SS
    for yy in range(y0, y1):
        dy = yy - ccy
        for xx in range(x0, x1):
            dx = xx - ccx
            if dx * dx + dy * dy <= rr:
                _px(xx, yy, rgb)


def stroke_circle(cx, cy, r, width, rgb):
    x0 = max(0, int((cx - r - width) * SS) - 1)
    y0 = max(0, int((cy - r - width) * SS) - 1)
    x1 = min(SW, int((cx + r + width) * SS) + 2)
    y1 = min(SH, int((cy + r + width) * SS) + 2)
    ccx, ccy = cx * SS, cy * SS
    ro = (r + width / 2.0) * SS
    ri = max(0.0, (r - width / 2.0) * SS)
    for yy in range(y0, y1):
        dy = yy - ccy
        for xx in range(x0, x1):
            dx = xx - ccx
            d2 = dx * dx + dy * dy
            if ri * ri <= d2 <= ro * ro:
                _px(xx, yy, rgb)


def downsample():
    """Box-downsample the SS canvas to the final 1024x1024 RGB bytes."""
    out = bytearray(W * H * 3)
    n = SS * SS
    for y in range(H):
        for x in range(W):
            r = g = b = 0
            base = (y * SS * SW + x * SS) * 3
            for dy in range(SS):
                i = base + dy * SW * 3
                for _ in range(SS):
                    r += canvas[i]
                    g += canvas[i + 1]
                    b += canvas[i + 2]
                    i += 3
            o = (y * W + x) * 3
            out[o] = r // n
            out[o + 1] = g // n
            out[o + 2] = b // n
    return bytes(out)


def encode_png(rgb):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


# --------------------------------------------------------------------------
# Hand-authored bitmap font.
#
# Every glyph lives on a 12-row grid: rows 0-8 are cap height / ascenders,
# rows 3-8 the x-height, rows 9-11 the descender zone; row 8 is the baseline.
# Glyphs are written with only the rows they need and padded at load time.
# '#' is ink, '.' is empty. Widths vary per glyph.
# --------------------------------------------------------------------------

GLYPHS = {
    "A": ("..###..", ".#...#.", "#.....#", "#.....#", "#######",
          "#.....#", "#.....#", "#.....#", "#.....#"),
    "B": ("######.", "#.....#", "#.....#", "#.....#", "######.",
          "#.....#", "#.....#", "#.....#", "######."),
    "C": (".#####.", "#.....#", "#......", "#......", "#......",
          "#......", "#......", "#.....#", ".#####."),
    "D": ("#####..", "#....#.", "#.....#", "#.....#", "#.....#",
          "#.....#", "#.....#", "#....#.", "#####.."),
    "E": ("#######", "#......", "#......", "#......", "######.",
          "#......", "#......", "#......", "#######"),
    "F": ("#######", "#......", "#......", "#......", "######.",
          "#......", "#......", "#......", "#......"),
    "G": (".#####.", "#.....#", "#......", "#......", "#..####",
          "#.....#", "#.....#", "#.....#", ".#####."),
    "H": ("#.....#", "#.....#", "#.....#", "#.....#", "#######",
          "#.....#", "#.....#", "#.....#", "#.....#"),
    "I": ("###", ".#.", ".#.", ".#.", ".#.", ".#.", ".#.", ".#.", "###"),
    "J": ("..####", ".....#", ".....#", ".....#", ".....#",
          ".....#", "#....#", "#....#", ".####."),
    "K": ("#.....#", "#....#.", "#...#..", "#..#...", "###....",
          "#..#...", "#...#..", "#....#.", "#.....#"),
    "L": ("#......", "#......", "#......", "#......", "#......",
          "#......", "#......", "#......", "#######"),
    "M": ("#.....#", "##...##", "#.#.#.#", "#.#.#.#", "#..#..#",
          "#.....#", "#.....#", "#.....#", "#.....#"),
    "N": ("#.....#", "##....#", "#.#...#", "#..#..#", "#...#.#",
          "#....##", "#.....#", "#.....#", "#.....#"),
    "O": (".#####.", "#.....#", "#.....#", "#.....#", "#.....#",
          "#.....#", "#.....#", "#.....#", ".#####."),
    "P": ("######.", "#.....#", "#.....#", "#.....#", "######.",
          "#......", "#......", "#......", "#......"),
    "Q": (".#####.", "#.....#", "#.....#", "#.....#", "#.....#",
          "#..#..#", "#...#..", "#....#.", ".####.#"),
    "R": ("######.", "#.....#", "#.....#", "#.....#", "######.",
          "#..#...", "#...#..", "#....#.", "#.....#"),
    "S": (".######", "#......", "#......", "#......", ".#####.",
          "......#", "......#", "#.....#", "######."),
    "T": ("#######", "...#...", "...#...", "...#...", "...#...",
          "...#...", "...#...", "...#...", "...#..."),
    "U": ("#.....#", "#.....#", "#.....#", "#.....#", "#.....#",
          "#.....#", "#.....#", "#.....#", ".#####."),
    "V": ("#.....#", "#.....#", "#.....#", "#.....#", "#.....#",
          ".#...#.", ".#...#.", "..#.#..", "...#..."),
    "W": ("#.....#", "#.....#", "#.....#", "#.....#", "#..#..#",
          "#.#.#.#", "#.#.#.#", "##...##", "#.....#"),
    "X": ("#.....#", ".#...#.", ".#...#.", "..#.#..", "...#...",
          "..#.#..", ".#...#.", ".#...#.", "#.....#"),
    "Y": ("#.....#", ".#...#.", ".#...#.", "..#.#..", "...#...",
          "...#...", "...#...", "...#...", "...#..."),
    "Z": ("#######", "......#", ".....#.", "....#..", "...#...",
          "..#....", ".#.....", "#......", "#######"),
    "0": (".#####.", "#....##", "#...#.#", "#..#..#", "#.#...#",
          "##....#", "#.....#", "#.....#", ".#####."),
    "1": ("..#..", ".##..", "#.#..", "..#..", "..#..", "..#..",
          "..#..", "..#..", "#####"),
    "2": (".#####.", "#.....#", "......#", "......#", ".....#.",
          "....#..", "...#...", "..#....", "#######"),
    "3": ("######.", "......#", "......#", "......#", ".#####.",
          "......#", "......#", "#.....#", "######."),
    "4": ("....#..", "...##..", "..#.#..", ".#..#..", "#....#.",
          "#######", ".....#.", ".....#.", ".....#."),
    "5": ("#######", "#......", "#......", "#......", "######.",
          "......#", "......#", "#.....#", ".#####."),
    "6": (".#####.", "#.....#", "#......", "#......", "######.",
          "#.....#", "#.....#", "#.....#", ".#####."),
    "7": ("#######", "......#", "......#", ".....#.", ".....#.",
          "....#..", "....#..", "...#...", "...#..."),
    "8": (".#####.", "#.....#", "#.....#", "#.....#", ".#####.",
          "#.....#", "#.....#", "#.....#", ".#####."),
    "9": (".#####.", "#.....#", "#.....#", "#.....#", ".######",
          "......#", "......#", "#.....#", ".#####."),
    ".": ("...", "...", "...", "...", "...", "...", "...", "##.", "##."),
    ",": ("...", "...", "...", "...", "...", "...", "...", "##.", "##.", "#.."),
    ";": ("...", "...", "##.", "##.", "...", "...", "...", "##.", "##.", "#.."),
    ":": ("...", "...", "##.", "##.", "...", "...", "...", "##.", "##."),
    "'": ("##.", ".#.", ".#.", "...", "...", "...", "...", "...", "..."),
    "-": (".....", ".....", ".....", ".....", "#####", ".....",
          ".....", ".....", "....."),
    "!": (".#.", ".#.", ".#.", ".#.", ".#.", ".#.", ".#.", "...", ".#."),
    "?": (".####.", "#....#", ".....#", "....#.", "...#..", "...#..",
          "...#..", "......", "...#.."),
    "&": (".####..", "#....#.", "#...#..", ".###...", "#.#.#..",
          "#..#.#.", "#...#..", "#....#.", ".####.."),
    "$": ("...#...", ".#####.", "#.#....", "#..#...", ".###...",
          "..#.##.", "..#..#.", ".####..", "...#..."),
    "/": ("....#", "....#", "...#.", "...#.", "..#..", "..#..",
          ".#...", ".#...", "#...."),
    "(": ("....#", "...#.", "..#..", "..#..", "..#..", "..#..",
          "..#..", "...#.", "....#"),
    ")": ("#....", ".#...", "..#..", "..#..", "..#..", "..#..",
          "..#..", ".#...", "#...."),
    "·": ("...", "...", "...", "...", ".#.", ".#.", "...", "...", "..."),
}

LOWER = {
    "a": (".......", ".......", ".......", ".#####.", "......#",
          ".######", "#.....#", "#.....#", ".######"),
    "b": ("#......", "#......", "#......", "######.", "#.....#",
          "#.....#", "#.....#", "#.....#", "######."),
    "c": (".......", ".......", ".......", ".#####.", "#.....#",
          "#......", "#......", "#.....#", ".#####."),
    "d": ("......#", "......#", "......#", ".######", "#.....#",
          "#.....#", "#.....#", "#.....#", ".######"),
    "e": (".......", ".......", ".......", ".#####.", "#.....#",
          "#######", "#......", "#.....#", ".#####."),
    "f": ("..###", ".#...", ".#...", "#####", ".#...", ".#...",
          ".#...", ".#...", ".#..."),
    "g": (".......", ".......", ".......", ".######", "#.....#",
          "#.....#", "#.....#", ".######", "......#", "#.....#",
          "#.....#", ".#####."),
    "h": ("#......", "#......", "#......", "######.", "#.....#",
          "#.....#", "#.....#", "#.....#", "#.....#"),
    "i": ("...", ".##", "...", "##.", ".#.", ".#.", ".#.", ".#.", "###"),
    "j": ("....", "..##", "....", ".###", "...#", "...#", "...#",
          "...#", "...#", "...#", "#..#", ".##."),
    "k": ("#.....", "#.....", "#.....", "#...##", "#..#..", "#.#...",
          "##....", "#.#...", "#..##."),
    "l": (".#.", ".#.", ".#.", ".#.", ".#.", ".#.", ".#.", ".#.", "###"),
    "m": (".......", ".......", ".......", "##.###.", "#.#.#.#",
          "#.#.#.#", "#.#.#.#", "#.#.#.#", "#.#.#.#"),
    "n": (".......", ".......", ".......", "######.", "#.....#",
          "#.....#", "#.....#", "#.....#", "#.....#"),
    "o": (".......", ".......", ".......", ".#####.", "#.....#",
          "#.....#", "#.....#", "#.....#", ".#####."),
    "p": (".......", ".......", ".......", "######.", "#.....#",
          "#.....#", "#.....#", "######.", "#......", "#......",
          "#......", "#......"),
    "q": (".......", ".......", ".......", ".######", "#.....#",
          "#.....#", "#.....#", ".######", "......#", "......#",
          "......#", "......#"),
    "r": (".....", ".....", ".....", "#.###", "##...", "#....",
          "#....", "#....", "#...."),
    "s": (".......", ".......", ".......", ".######", "#......",
          ".#####.", "......#", "......#", "######."),
    "t": (".#...", ".#...", ".#...", "#####", ".#...", ".#...",
          ".#...", ".#...", "..##."),
    "u": (".......", ".......", ".......", "#.....#", "#.....#",
          "#.....#", "#.....#", "#....##", ".####.#"),
    "v": (".......", ".......", ".......", "#.....#", "#.....#",
          ".#...#.", ".#...#.", "..#.#..", "...#..."),
    "w": (".......", ".......", ".......", "#.....#", "#.....#",
          "#..#..#", "#.#.#.#", "#.#.#.#", ".#...#."),
    "x": (".......", ".......", ".......", "#.....#", ".#...#.",
          "..#.#..", "...#...", "..#.#..", ".#...#."),
    "y": (".......", ".......", ".......", "#.....#", "#.....#",
          "#.....#", ".#...#.", "..#.#..", "...#...", "...#...",
          "..#....", ".#....."),
    "z": (".......", ".......", ".......", "#######", "....#..",
          "...#...", "..#....", ".#.....", "#######"),
}

GLYPHS.update(LOWER)

# Normalise every glyph to exactly 12 rows of equal width.
FONT = {}
for ch, rows in GLYPHS.items():
    w = max(len(r) for r in rows)
    padded = [r.ljust(w, ".") for r in rows]
    while len(padded) < 12:
        padded.append("." * w)
    FONT[ch] = (w, tuple(padded[:12]))

SPACE_UNITS = 4.4
BLANK = (4, tuple("...." for _ in range(12)))


def _advance(ch, bold):
    if ch == " ":
        return SPACE_UNITS
    w, _ = FONT.get(ch, BLANK)
    return w + (2.0 if bold else 1.15)


def measure(text, cap, bold=False):
    """Width in final-image pixels of `text` at cap height `cap`."""
    u = cap / 9.0
    return sum(_advance(ch, bold) for ch in text) * u


def fit_cap(text, cap, max_w, bold=False):
    """Shrink cap height (if needed) so the text fits max_w."""
    w = measure(text, cap, bold)
    if w <= max_w or w == 0:
        return cap
    return cap * (max_w / w)


def draw_text(text, x, y, cap, rgb, bold=False, center_w=None):
    """Draw one line; (x, y) is the top of the glyph cell. If center_w is
    given, the line is centred in the span [x, x + center_w]."""
    u = cap / 9.0
    if center_w is not None:
        x = x + (center_w - measure(text, cap, bold)) / 2.0
    bold_extra = 0.85 * u if bold else 0.0
    cx = x
    for ch in text:
        if ch == " ":
            cx += SPACE_UNITS * u
            continue
        gw, rows = FONT.get(ch, BLANK)
        for ry, row in enumerate(rows):
            for rx, cell in enumerate(row):
                if cell == "#":
                    fill_rect(cx + rx * u, y + ry * u,
                              u * 1.04 + bold_extra, u * 1.04, rgb)
        cx += (gw + (2.0 if bold else 1.15)) * u
    return cx - x


def wrap(text, cap, max_w, bold=False):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines = []
    cur = ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if measure(trial, cap, bold) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_block(text, x, y, cap, rgb, bold, max_w, pitch_units, max_lines=None):
    """Draw wrapped text; returns the y just below the block."""
    u = cap / 9.0
    lines = wrap(text, cap, max_w, bold)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        draw_text(line, x, y, cap, rgb, bold)
        y += pitch_units * u
    return y


# --------------------------------------------------------------------------
# Palette
# --------------------------------------------------------------------------

PAPER = (246, 242, 233)
INK = (20, 22, 26)
MUTED = (96, 98, 102)
CARD = (255, 253, 247)
BORDER = (213, 205, 188)
RED = (178, 34, 40)
NAVY = (20, 44, 72)
NAVY_DECK = (214, 223, 236)
GOLD = (219, 168, 66)
STEEL = (58, 92, 138)
ORANGE = (192, 96, 30)
OLIVE = (102, 114, 50)
GREEN = (46, 120, 72)
PURPLE = (96, 72, 160)
TEAL = (22, 118, 118)

MARGIN = 30
CW = W - 2 * MARGIN  # content width


# --------------------------------------------------------------------------
# Page composition
# --------------------------------------------------------------------------

def masthead():
    fill_rect(0, 0, W, H, PAPER)
    # Kicker line
    draw_text("WORLD NEWS", MARGIN, 24, 19, RED, bold=True)
    right = "THE DAY IN ONE IMAGE"
    rw = measure(right, 19, bold=True)
    draw_text(right, W - MARGIN - rw, 24, 19, MUTED, bold=True)
    # The date: the single most important line on the page.
    date = "TUESDAY 17 NOVEMBER 2026"
    cap = fit_cap(date, 54, CW, bold=True)
    draw_text(date, MARGIN, 52, cap, INK, bold=True)
    # Classic newspaper double rule
    fill_rect(MARGIN, 128, CW, 5, INK)
    fill_rect(MARGIN, 137, CW, 1.6, INK)


def lead_panel():
    x, y, w, h = MARGIN, 152, CW, 252
    fill_rect(x, y, w, h, NAVY)
    # Three summit rings, top right
    stroke_circle(x + w - 118, y + 58, 30, 5, GOLD)
    stroke_circle(x + w - 66, y + 58, 30, 5, (216, 90, 84))
    stroke_circle(x + w - 92, y + 96, 30, 5, (140, 178, 224))
    px = x + 24
    draw_text("TOP STORY · SHENZHEN, CHINA", px, y + 18, 17, GOLD, bold=True)
    head = "XI, TRUMP & PUTIN TO MEET IN SHENZHEN"
    cap = fit_cap(head, 50, w - 48, bold=True)
    y2 = draw_block(head, px, y + 48, cap, (255, 255, 255), True,
                    w - 48, 10.6, max_lines=2)
    fill_rect(px, y2 + 4, 120, 3.2, GOLD)
    deck = ("First-ever trilateral summit set for Thursday "
            "at APEC in China.")
    draw_block(deck, px, y2 + 18, 21, NAVY_DECK, False, w - 48, 13.2,
               max_lines=2)


def story_card(x, y, w, h, bar, tag, head, deck,
               head_cap=25, deck_cap=15.5, tag_cap=14.5):
    fill_rect(x, y, w, h, CARD)
    fill_rect(x, y, w, h, BORDER)  # border via outline below
    fill_rect(x + 1.5, y + 1.5, w - 3, h - 3, CARD)
    fill_rect(x, y, w, 6, bar)
    px = x + 16
    tw = w - 32
    draw_text(tag, px, y + 14, tag_cap, bar, bold=True)
    y2 = draw_block(head, px, y + 36, head_cap, INK, True, tw, 11.0,
                    max_lines=3)
    draw_block(deck, px, y2 + 5, deck_cap, (52, 55, 60), False, tw, 12.9,
               max_lines=3)


def page():
    masthead()
    lead_panel()
    gap = 12
    col_w = (CW - gap) // 2
    gy = 418
    row_h = 172
    story_card(MARGIN, gy, col_w, row_h, RED,
               "STRAIT OF HORMUZ · GULF",
               "FOURTH TANKER BURNS IN HORMUZ",
               "Ship hits naval mine in the strait; Iran seizes a US drone "
               "as Gulf tensions climb.")
    story_card(MARGIN + col_w + gap, gy, col_w, row_h, STEEL,
               "UKRAINE · WAR",
               "KYIV BATTERED, CRIMEA BRIDGE SHUT",
               "Russian ballistic missiles pound the capital; Ukraine "
               "strikes the Kerch Bridge.")
    gy += row_h + gap
    story_card(MARGIN, gy, col_w, row_h, ORANGE,
               "YEMEN · ADEN",
               "HOUTHIS CLOSE ON ADEN",
               "Rebels advance to within 60 km; Saudi Arabia replaces "
               "its coalition commander.")
    story_card(MARGIN + col_w + gap, gy, col_w, row_h, OLIVE,
               "GAZA · DIPLOMACY",
               "WEST PRESSES ISRAEL ON GAZA AID",
               "UK, Australia, Canada and Italy demand crossings open; "
               "Britain sanctions settlement firms.")
    gy += row_h + gap
    col3 = (CW - 2 * gap) // 3
    row3_h = 186
    story_card(MARGIN, gy, col3, row3_h, GREEN,
               "CLIMATE · COP31",
               "COP31 DRAFT: FASTER FOSSIL PHASE-OUT",
               "Antalya talks propose $120B a year in climate finance "
               "by 2035.",
               head_cap=21, deck_cap=14, tag_cap=13)
    story_card(MARGIN + col3 + gap, gy, col3, row3_h, PURPLE,
               "TECH · WASHINGTON",
               "US TIGHTENS AI CHIP BAN ON CHINA",
               "New export rules close loopholes for buying advanced "
               "chips abroad.",
               head_cap=21, deck_cap=14, tag_cap=13)
    story_card(MARGIN + 2 * (col3 + gap), gy, col3, row3_h, TEAL,
               "MARKETS · NVIDIA",
               "HUANG OPEN TO NVIDIA RETURN",
               "Ex-CEO signals comeback as investors await earnings; "
               "AI stocks slide.",
               head_cap=21, deck_cap=14, tag_cap=13)
    # Footer: restate the day, centred under a rule.
    fy = gy + row3_h + 12
    fill_rect(MARGIN, fy, CW, 2, INK)
    foot = "EVERY STORY ABOVE WAS REPORTED ON TUESDAY 17 NOVEMBER 2026"
    fcap = fit_cap(foot, 14, CW, bold=True)
    draw_text(foot, MARGIN, fy + 10, fcap, MUTED, bold=True, center_w=CW)


def main():
    page()
    png = encode_png(downsample())
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "entry.png"), "wb") as fh:
        fh.write(png)


if __name__ == "__main__":
    main()
