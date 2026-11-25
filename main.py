# news-image-20261125 — "The World in One Picture"
# A procedural newspaper poster summing up Wednesday 25 November 2026.
# Python 3.13, standard library only. No network, no clock, no randomness:
# every run writes byte-identical output to /output/entry.png
# (or $MAKEFUN_OUTPUT_DIR/entry.png when the harness sets it).
import os
import struct
import zlib
from binascii import crc32

# ---------------------------------------------------------------- canvas
W = 1024
H = 1024

PAPER = (247, 241, 227)
PANEL = (250, 245, 233)
TINT = (236, 228, 208)
INK = (26, 26, 26)
RED = (178, 38, 30)
BLUE = (29, 78, 137)
SKY = (120, 165, 205)
GRAY = (112, 106, 90)
GOLD = (214, 176, 58)
GREEN = (38, 110, 68)
ORANGE = (214, 110, 32)
SMOKE = (150, 144, 128)
DARK = (52, 52, 48)

px = bytearray(W * H * 3)
for i in range(W * H):
    px[i * 3] = PAPER[0]
    px[i * 3 + 1] = PAPER[1]
    px[i * 3 + 2] = PAPER[2]


def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        o = (y * W + x) * 3
        px[o] = c[0]
        px[o + 1] = c[1]
        px[o + 2] = c[2]


def fill_rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            set_px(xx, yy, c)


def rect(x, y, w, h, c, t):
    fill_rect(x, y, w, t, c)
    fill_rect(x, y + h - t, w, t, c)
    fill_rect(x, y, t, h, c)
    fill_rect(x + w - t, y, t, h, c)


def hline(x, y, w, c, t):
    fill_rect(x, y, w, t, c)


def line(x0, y0, x1, y1, c):
    dx = abs(x1 - x0)
    sx = 1 if x0 < x1 else -1
    dy = -abs(y1 - y0)
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        set_px(x, y, c)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def line_w(x0, y0, x1, y1, w, c):
    steps = max(abs(x1 - x0), abs(y1 - y0))
    half = w // 2
    for i in range(steps + 1):
        t = 0 if steps == 0 else i / steps
        x = round(x0 + (x1 - x0) * t)
        y = round(y0 + (y1 - y0) * t)
        fill_rect(x - half, y - half, w, w, c)


def fill_circle(cx, cy, r, c):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            dx = x - cx
            dy = y - cy
            if dx * dx + dy * dy <= r * r:
                set_px(x, y, c)


def circle(cx, cy, r, c):
    import math
    steps = max(48, r * 4)
    px0, py0 = cx + r, cy
    for i in range(1, steps + 1):
        a = (i / steps) * math.pi * 2
        x = round(cx + math.cos(a) * r)
        y = round(cy + math.sin(a) * r)
        line(px0, py0, x, y, c)
        px0, py0 = x, y


def fill_poly(pts, c):
    min_y = min(p[1] for p in pts)
    max_y = max(p[1] for p in pts)
    for y in range(min_y, max_y + 1):
        xs = []
        for i in range(len(pts)):
            a = pts[i]
            b = pts[(i + 1) % len(pts)]
            if (a[1] <= y < b[1]) or (b[1] <= y < a[1]):
                t = (y - a[1]) / (b[1] - a[1])
                xs.append(round(a[0] + t * (b[0] - a[0])))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            for x in range(xs[i], xs[i + 1] + 1):
                set_px(x, y, c)


def poly_outline(pts, c):
    for i in range(len(pts)):
        a = pts[i]
        b = pts[(i + 1) % len(pts)]
        line(a[0], a[1], b[0], b[1], c)


def burst(cx, cy, r, c):
    import math
    for i in range(8):
        a = (i * math.pi) / 4
        ln = r if i % 2 == 0 else round(r * 0.45)
        line(cx, cy, round(cx + math.cos(a) * ln), round(cy + math.sin(a) * ln), c)
    fill_circle(cx, cy, 3, c)


def dashed_curve(x0, y0, cx, cy, x1, y1, c):
    lx, ly = x0, y0
    for i in range(1, 49):
        t = i / 48
        x = round((1 - t) * (1 - t) * x0 + 2 * (1 - t) * t * cx + t * t * x1)
        y = round((1 - t) * (1 - t) * y0 + 2 * (1 - t) * t * cy + t * t * y1)
        if i % 4 < 2:
            line(lx, ly, x, y, c)
        lx, ly = x, y


# ------------------------------------------------------------------- font
# A 5x7 bitmap font. '#' is ink, '.' is clear.
FONT = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    ".": [".....", ".....", ".....", ".....", ".....", ".....", "..#.."],
    ",": [".....", ".....", ".....", ".....", "..#..", "..#..", ".#..."],
    "'": ["..#..", "..#..", ".....", ".....", ".....", ".....", "....."],
    "-": [".....", ".....", ".....", ".###.", ".....", ".....", "....."],
    ":": [".....", "..#..", ".....", ".....", ".....", "..#..", "....."],
    ";": [".....", "..#..", ".....", ".....", ".....", "..#..", ".#..."],
    "%": ["#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"],
    "+": [".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."],
    "/": ["....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."],
    "(": ["...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."],
    ")": [".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."],
    "&": [".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    "=": [".....", ".....", ".###.", ".....", ".###.", ".....", "....."],
    '"': [".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."],
}


def draw_glyph(x, y, ch, s, c):
    g = FONT.get(ch, FONT[" "])
    for r in range(7):
        for col in range(5):
            if g[r][col] == "#":
                fill_rect(x + col * s, y + r * s, s, s, c)


def text_w(s, scale):
    if not s:
        return 0
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, c, center=False):
    up = s.upper()
    cx = x - text_w(up, scale) // 2 if center else x
    for ch in up:
        draw_glyph(cx, y, ch, scale, c)
        cx += 6 * scale


def wrap(s, max_w, scale):
    words = s.split(" ")
    lines = []
    cur = ""
    for w in words:
        test = w if cur == "" else cur + " " + w
        if text_w(test, scale) <= max_w or cur == "":
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur != "":
        lines.append(cur)
    return lines


def draw_block(x, y, s, scale, c, max_w, lh):
    lines = wrap(s, max_w, scale)
    for i, ln in enumerate(lines):
        draw_text(x, y + i * lh, ln, scale, c)
    return y + len(lines) * lh

# ------------------------------------------------------------- story icons
# Each icon draws inside a box (x, y, w, h) at the top of its card.


def icon_tower(x, y, w, h):
    """Lead illustration: the PIF Tower in Riyadh's KAFD, struck mid-facade."""
    fill_rect(x, y, w, h, PANEL)
    rect(x, y, w, h, INK, 2)
    # Skyline of smaller KAFD towers behind.
    fill_rect(x + 14, y + 120, 34, 150, TINT)
    fill_rect(x + 56, y + 90, 30, 180, TINT)
    fill_rect(x + 330, y + 110, 34, 160, TINT)
    fill_rect(x + 372, y + 150, 26, 120, TINT)
    # The PIF Tower: tall, tapering, glassy.
    tower = [
        (x + 130, y + 270), (x + 150, y + 40), (x + 250, y + 40),
        (x + 270, y + 270),
    ]
    fill_poly(tower, BLUE)
    poly_outline(tower, INK)
    # Glass floor lines.
    for i in range(1, 9):
        yy = y + 40 + i * 26
        line(x + 138 + i * 2, yy, x + 262 - i * 2, yy, SKY)
    # Impact burst and smoke halfway up the facade.
    burst(x + 252, y + 132, 16, RED)
    fill_circle(x + 272, y + 112, 9, SMOKE)
    fill_circle(x + 288, y + 100, 12, SMOKE)
    fill_circle(x + 306, y + 112, 8, SMOKE)
    # Small drone silhouette diving in from the right.
    fill_poly(
        [(x + 380, y + 96), (x + 344, y + 88), (x + 352, y + 96), (x + 344, y + 104)],
        INK,
    )
    line(x + 352, y + 84, x + 342, y + 78, INK)
    line(x + 352, y + 108, x + 342, y + 114, INK)
    # Ground line and caption.
    hline(x + 8, y + 270, w - 16, INK, 2)
    draw_text(x + w // 2, y + h - 42, "PIF TOWER - KAFD, RIYADH", 2, INK, center=True)
    draw_text(x + w // 2, y + h - 20, "2ND HIT IN FIVE DAYS", 2, RED, center=True)


def icon_rocket(x, y, w, h):
    """Shenzhou-24: Long March rocket climbing, stars, Tiangong ring."""
    fill_rect(x, y, w, h, TINT)
    # Stars.
    for sx, sy in [(14, 6), (200, 8), (w - 14, 10), (w - 40, 34), (170, 50)]:
        fill_circle(x + sx, y + sy, 1, INK)
    # Tiangong ring (station) top right.
    circle(x + w - 30, y + 14, 8, BLUE)
    fill_rect(x + w - 42, y + 12, 24, 3, BLUE)
    # Rocket body.
    fill_poly(
        [(x + 18, y + 22), (x + 28, y + 2), (x + 38, y + 22)],
        RED,
    )
    fill_rect(x + 18, y + 22, 20, 18, INK)
    fill_rect(x + 23, y + 27, 10, 8, SKY)
    fill_poly([(x + 18, y + 34), (x + 8, y + 44), (x + 18, y + 42)], RED)
    fill_poly([(x + 38, y + 34), (x + 48, y + 44), (x + 38, y + 42)], RED)
    # Flame and smoke.
    fill_poly([(x + 22, y + 40), (x + 28, y + 54), (x + 34, y + 40)], ORANGE)
    fill_circle(x + 20, y + 56, 3, SMOKE)
    fill_circle(x + 34, y + 57, 3, SMOKE)
    draw_text(x + 62, y + 12, "TIANGONG", 1, GRAY)
    draw_text(x + 62, y + 24, "1ST PAKISTANI", 1, INK)
    draw_text(x + 62, y + 36, "IN ORBIT", 1, INK)


def icon_tanker(x, y, w, h):
    """Oil tankers burning in the Strait of Hormuz."""
    fill_rect(x, y, w, h, TINT)
    # Sea.
    hline(x + 8, y + 50, w - 16, SKY, 2)
    hline(x + 8, y + 55, w - 16, SKY, 2)
    # Tanker hull.
    fill_poly(
        [(x + 30, y + 36), (x + 220, y + 36), (x + 204, y + 48), (x + 46, y + 48)],
        INK,
    )
    fill_rect(x + 90, y + 26, 44, 10, INK)
    fill_rect(x + 140, y + 20, 8, 6, INK)
    # Flames and smoke above the deck.
    fill_poly([(x + 40, y + 26), (x + 47, y + 12), (x + 54, y + 26)], RED)
    fill_poly([(x + 58, y + 26), (x + 66, y + 8), (x + 74, y + 26)], ORANGE)
    fill_poly([(x + 78, y + 26), (x + 85, y + 14), (x + 92, y + 26)], RED)
    fill_circle(x + 180, y + 16, 5, SMOKE)
    fill_circle(x + 192, y + 10, 6, SMOKE)
    fill_circle(x + 204, y + 16, 4, SMOKE)
    draw_text(x + 14, y + 2, "STRAIT OF HORMUZ", 1, GRAY)


def icon_cyber(x, y, w, h):
    """CIA unclassified system breached: a cracked monitor and lock."""
    fill_rect(x, y, w, h, TINT)
    # Monitor.
    fill_rect(x + 50, y + 6, 120, 40, PANEL)
    rect(x + 50, y + 6, 120, 40, INK, 2)
    fill_rect(x + 100, y + 46, 18, 6, INK)
    fill_rect(x + 80, y + 52, 58, 3, INK)
    # Crack across the screen.
    line_w(x + 64, y + 12, x + 96, y + 28, 2, RED)
    line_w(x + 96, y + 28, x + 120, y + 16, 2, RED)
    line_w(x + 96, y + 28, x + 110, y + 40, 2, RED)
    # Padlock, open.
    rect(x + 122, y + 28, 24, 16, BLUE, 2)
    line(x + 127, y + 28, x + 127, y + 20, BLUE)
    line(x + 141, y + 28, x + 141, y + 20, BLUE)
    line(x + 127, y + 20, x + 141, y + 20, BLUE)
    draw_text(x + 58, y + 12, "CIA", 2, RED)
    draw_text(x + 180, y + 20, "BREACH", 2, RED)


def icon_chart(x, y, w, h):
    """Nvidia shares fall after Huang's comeback rally fades."""
    fill_rect(x, y, w, h, TINT)
    # Falling line with arrowhead.
    line_w(x + 20, y + 8, x + w // 3, y + 18, 3, GREEN)
    line_w(x + w // 3, y + 18, x + 2 * w // 3, y + 32, 3, RED)
    line_w(x + 2 * w // 3, y + 32, x + w - 70, y + 46, 3, RED)
    fill_poly(
        [(x + w - 70, y + 46), (x + w - 86, y + 44), (x + w - 76, y + 56)],
        RED,
    )
    # Grid.
    hline(x + 16, y + 30, w - 32, SMOKE, 1)
    hline(x + 16, y + 50, w - 32, SMOKE, 1)
    draw_text(x + 18, y + 52, "NVIDIA", 1, INK)
    draw_text(x + w - 42, y + 52, "DOWN", 1, RED)


def icon_flame(x, y, w, h):
    """Hong Kong fire, one year on: a memorial flame over the tower block."""
    fill_rect(x, y, w, h, TINT)
    # Tower block.
    fill_rect(x + 60, y + 22, 80, 36, INK)
    for r in range(2):
        for c in range(4):
            fill_rect(x + 68 + c * 18, y + 28 + r * 14, 9, 7, PAPER)
    # Memorial flame above the roof.
    fill_poly([(x + 84, y + 22), (x + 100, y + 2), (x + 116, y + 22)], ORANGE)
    fill_poly([(x + 91, y + 22), (x + 100, y + 10), (x + 109, y + 22)], RED)
    # "168" and caption.
    draw_text(x + 170, y + 22, "168", 3, RED)
    draw_text(x + 170, y + 46, "ONE YEAR ON", 1, GRAY)


# ------------------------------------------------------------------ cards
def card(x, y, w, h, headline, body, icon):
    fill_rect(x, y, w, h, PANEL)
    rect(x, y, w, h, INK, 2)
    icon(x + 12, y + 10, w - 24, 60)
    head_y = y + 82
    head_end = draw_block(x + 14, head_y, headline, 2, INK, w - 28, 19)
    draw_block(x + 14, head_end + 6, body, 2, INK, w - 28, 18)


# -------------------------------------------------------------- the poster
# Masthead.
draw_text(512, 28, "THE WORLD IN ONE PICTURE", 5, INK, center=True)
# Date, in red, directly under the masthead.
draw_text(512, 74, "WEDNESDAY 25 NOVEMBER 2026", 3, RED, center=True)
# Double rule under the date.
hline(28, 106, 968, INK, 2)
hline(28, 111, 968, INK, 1)

# Lead story: text on the left, tower illustration on the right.
draw_text(28, 134, "LEAD STORY", 2, RED)
draw_block(28, 158, "HOUTHI DRONE HITS RIYADH'S TALLEST TOWER AGAIN", 3, INK, 532, 27)
draw_block(
    28,
    248,
    "A Houthi drone struck the 80-storey PIF Tower in Riyadh on Tuesday, the second hit in five days. Saudi civil defence said 11 people were injured, two critically. The Saudi-led coalition vowed a decisive response as the war with Yemen's Houthis widens.",
    2,
    INK,
    532,
    19,
)
hline(28, 388, 532, RED, 2)
draw_text(28, 400, "11 INJURED - 2 CRITICAL - 2ND HIT IN 5 DAYS", 2, RED)
draw_text(28, 424, "COALITION VOWS DECISIVE RESPONSE", 2, RED)
icon_tower(584, 124, 412, 356)

# Divider before the rest of the day's news.
hline(28, 492, 968, INK, 2)

# Row one: three stories.
card(
    28,
    506,
    312,
    236,
    "SHENZHOU-24 LIFTS OFF WITH FIRST PAKISTANI IN ORBIT",
    "China launched Shenzhou-24 on Wednesday. Zeeshan Ali is the first Pakistani in orbit.",
    icon_rocket,
)
card(
    356,
    506,
    312,
    236,
    "OIL TANKERS BURN IN STRAIT OF HORMUZ",
    "Iran said three tankers struck naval mines and caught fire. Tehran ruled out US talks.",
    icon_tanker,
)
card(
    684,
    506,
    312,
    236,
    "CIA UNCLASSIFIED SYSTEM BREACHED",
    "Hackers breached a CIA unclassified system. Officials said no classified data was hit.",
    icon_cyber,
)

# Row two: two wider stories.
card(
    28,
    756,
    474,
    236,
    "NVIDIA SHARES FALL AS HUANG COMEBACK RALLY FADES",
    "Nvidia shares dropped on Wednesday as doubts returned days after Jensen Huang's reinstatement.",
    icon_chart,
)
card(
    522,
    756,
    474,
    236,
    "HONG KONG REMEMBERS ITS FIRE DEAD, ONE YEAR ON",
    "A year after 168 people died in the Hong Kong tower fire, survivors returned to charred homes.",
    icon_flame,
)

# Footer.
draw_text(512, 1004, "THE WORLD IN ONE PICTURE - 25 NOVEMBER 2026", 1, GRAY, center=True)

# --------------------------------------------------------------- PNG out
def png_chunk(type_b, data):
    td = type_b + data
    return (
        struct.pack(">I", len(data))
        + td
        + struct.pack(">I", crc32(td) & 0xFFFFFFFF)
    )


def encode_png():
    raw = bytearray(H * (1 + W * 3))
    for y in range(H):
        raw[y * (1 + W * 3)] = 0
        raw[y * (1 + W * 3) + 1 : (y + 1) * (1 + W * 3)] = px[y * W * 3 : (y + 1) * W * 3]
    idat = zlib.compress(bytes(raw), 9)
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", ihdr)
        + png_chunk(b"IDAT", idat)
        + png_chunk(b"IEND", b"")
    )


out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
os.makedirs(out_dir, exist_ok=True)
with open(os.path.join(out_dir, "entry.png"), "wb") as f:
    f.write(encode_png())
