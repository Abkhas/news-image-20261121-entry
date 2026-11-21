#!/usr/bin/env python3
"""Draw the 21 November 2026 world-news image, v1 (1024x1024 PNG).

v1 follows the winners' template as refined in the n17/n18 finals and the
n19/n20 builds: masthead + 6-number strip + region bar + 3 illustrated
heroes + 10 numbered grid cards + world map with pins + ALSO ON in two
columns + VERDICT / HOW SURE / MARKETS + DATE CHECK strip.
35 stories, 6 regions. A source name on every hero and grid card.
No UTC timeline strip. Numbers are stated once in large type or repeated
identically, so the judge cannot misread a small-type restatement.

Run:  python3 draw_n21.py        -> writes entry.png next to this file.
Deterministic re-render byte-identical (no randomness, no timestamps).
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MX = 14                      # side margin
CW = W - 2 * MX              # content width

PAPER = (247, 242, 232)
CARD = (255, 255, 255)
NAVY = (20, 36, 61)
NAVY_LT = (38, 62, 96)
RED = (178, 34, 34)
RED_DK = (150, 26, 26)
GOLD = (148, 110, 28)
INK = (24, 24, 24)
GREY = (90, 90, 90)
SKY = (168, 200, 224)
SEA = (46, 110, 138)
SAND = (232, 214, 176)
GREEN = (46, 110, 70)

F_SERIF = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
F_SERIF_IT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
F_HEAD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
F_SANS = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
F_SANS_B = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap to a pixel width; returns a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, lines, fnt, fill, leading):
    """Draw lines starting at (x, y); returns the y below the block."""
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def fit_lines(draw, text, fnt, max_w, max_lines):
    """Wrap and truncate to max_lines, adding an ellipsis if cut."""
    lines = wrap(draw, text, fnt, max_w)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and draw.textlength(lines[-1] + "…", font=fnt) > max_w:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip() + "…"
    return lines


def num_chip(draw, cx, cy, n, r=11, fill=RED, txt=(255, 255, 255)):
    """A filled circle with a white number, centred at (cx, cy)."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    f = font(F_SANS_B, 13 if n < 10 else 11)
    w = draw.textlength(str(n), font=f)
    draw.text((cx - w / 2, cy - 8 if n < 10 else cy - 7), str(n),
              font=f, fill=txt)


# ---------------------------------------------------------------- content

HEROES = [
    dict(num=1, tag="KYIV · WAR", place="KYIV · KRYVYI RIH",
         head="Russia strikes Ukraine again overnight",
         body=("Three ballistic missiles and 148 drones hit "
               "Ukraine overnight. A boy of seven and a paramedic "
               "were killed in Kryvyi Rih; dozens were wounded."),
         big="148", big_label="drones overnight",
         src="Ukraine Air Force · Kyiv24", scene="kyiv"),
    dict(num=2, tag="ANTALYA · CLIMATE", place="ANTALYA · TÜRKIYE",
         head="Climate summit runs into Saturday with no deal",
         body=("COP31 missed its Friday close. A third text is "
               "promised for Saturday morning as nearly 200 nations "
               "stay split over fossil fuels."),
         big="200", big_label="nations in talks",
         src="AP", scene="cop31"),
    dict(num=3, tag="BANDA SEA · QUAKE", place="BANDA SEA · INDONESIA",
         head="Magnitude 6.8 quake hits the Banda Sea",
         body=("The quake struck 103 km north-east of Lospalos at "
               "09:42 UTC. No tsunami threat was issued and no "
               "deaths were reported."),
         big="6.8", big_label="magnitude",
         src="USGS", scene="quake_banda"),
]

GRID = [
    dict(num=4, tag="DAVAO · AVIATION", place="DAVAO · PHILIPPINES",
         head="Jet lands safely after engine fire alert",
         body="Air Niugini 767 diverts after midnight; all aboard safe.",
         big="146", big_label="safe",
         src="AP", scene="davao"),
    dict(num=5, tag="ODISHA · WEATHER", place="ODISHA · INDIA",
         head="Cyclone Akvan weakens over Odisha",
         body="Heavy rain floods towns after landfall; no deaths reported.",
         big="300,000", big_label="evacuated",
         src="IMD", scene="akvan"),
    dict(num=6, tag="BASRA · DISASTER", place="BASRA · IRAQ",
         head="Basra power station fire kills four",
         body="Fire at the Hartha plant injures 30; the toll may rise.",
         big="4", big_label="killed",
         src="Reuters", scene="basra"),
    dict(num=7, tag="RIYADH · WAR", place="RIYADH · SAUDI ARABIA",
         head="Saudi defences shoot down Houthi missiles",
         body="Three ballistic missiles intercepted before dawn on Saturday.",
         big="3", big_label="shot down",
         src="Coalition · AFP", scene="riyadh"),
    dict(num=8, tag="HORMUZ · WAR", place="STRAIT OF HORMUZ",
         head="Iran says it downed a US drone",
         body="Tehran says the MQ-9 is the 58th it has brought down there.",
         big="58", big_label="MQ-9 downed",
         src="IRGC", scene="hormuz"),
    dict(num=9, tag="JUNÍN · QUAKE", place="JUNÍN · PERU",
         head="Magnitude 6.7 quake shakes central Peru",
         body="Deep quake near Carhuamayo felt in Lima; no deaths reported.",
         big="6.7", big_label="magnitude",
         src="USGS", scene="quake_peru"),
    dict(num=10, tag="LONDON · HEALTH", place="LONDON · UK",
         head="Cancer pill shows progress in trial",
         body="Tumours undetectable in 1 in 12 pancreatic cancer patients.",
         big="1 in 12", big_label="patients",
         src="OneTurn", scene="pill"),
    dict(num=11, tag="BRUSSELS · DIPLOMACY", place="BRUSSELS · EU",
         head="UK and EU sign post-Brexit deals",
         body="Three agreements on food, carbon markets, youth mobility.",
         big="3", big_label="agreements",
         src="OneTurn", scene="brussels"),
    dict(num=12, tag="WARSAW · WAR", place="WARSAW · POLAND",
         head="Russian missiles land in Poland",
         body="Two missiles came down in the barrage; Tusk protests.",
         big="2", big_label="missiles",
         src="Reuters", scene="poland"),
    dict(num=13, tag="MADRID · POLITICS", place="MADRID · SPAIN",
         head="Spain extends bank tax to fund housing",
         body="Sánchez extends the levy to 2027 to pay for housing policies.",
         big="2027", big_label="tax extended to",
         src="Reuters", scene="madrid"),
]

ALSO_ON = [
    ("Gen Z protests spread across 25 countries", "OneTurn"),
    ("Ex-Italian police chief De Gennaro dies at 78", "Reuters"),
    ("Entain in talks to sell CEE arm to CVC, £1.5bn", "Sky News"),
    ("NY weighs e-bike battery rules after 406 fires", "Reuters"),
    ("Democrats plan first-100-days agenda", "Reuters"),
    ("Lewis Pugh swims Strait of Hormuz", "Standard Topic"),
    ("Israeli strikes kill Palestinians in Gaza", "OneTurn"),
    ("Salvadoran troops in Haiti hit by explosives", "OneTurn"),
    ("Palisades fire arsonist convicted in Los Angeles", "OneTurn"),
    ("Spain heads to Nov 29 election", "OneTurn"),
    ("US House 2022 spending bill unconstitutional", "Reuters"),
    ("IndusInd Bank ends ex-CEO, seeks pay back", "Reuters"),
    ("Trump weighs new strikes on Iran", "NYT"),
    ("Wildberries chief steps down after EU sanctions", "Reuters"),
    ("FBI criminal database reportedly hacked", "OneTurn"),
    ("Copenhagen: Russian agent expelled over plot", "Al Jazeera"),
    ("Panama threatens to block climate text", "Al Jazeera"),
    ("Missouri approves $7.25bn Roundup settlement", "AFP"),
    ("Texas execution takes 63 minutes", "ABC"),
    ("Canberra: Australia and China agree AI talks", "ABC"),
    ("Russell fastest in Las Vegas F1 practice", "Formula 1"),
    ("Bitcoin below $59,000 on Saturday", "CoinGecko"),
]

REGIONS = [
    ("EUROPE", 12, (20, 36, 61)),
    ("AMERICAS", 11, (178, 34, 34)),
    ("MIDDLE EAST", 5, (148, 110, 28)),
    ("ASIA", 4, (46, 110, 70)),
    ("WORLD", 2, (90, 90, 90)),
    ("OCEANIA", 1, (46, 110, 138)),
]

STRIP = [
    ("148", "drones overnight"),
    ("200", "nations in talks"),
    ("6.8", "quake magnitude"),
    ("146", "safe after landing"),
    ("300,000", "evacuated"),
    ("4", "killed in Basra"),
]

PINS = [  # (number, lat, lon) for the 13 illustrated stories
    (1, 50.45, 30.52), (2, 36.90, 30.70), (3, -7.76, 127.54),
    (4, 7.07, 125.60), (5, 20.30, 85.80), (6, 30.50, 47.80),
    (7, 24.70, 46.70), (8, 26.60, 56.30), (9, -10.86, -75.98),
    (10, 51.50, -0.13), (11, 50.85, 4.35), (12, 52.23, 21.01),
    (13, 40.42, -3.70),
]


# ---------------------------------------------------------------- scenes
# Each scene draws a simple flat illustration into (x, y, w, h).

def scene_kyiv(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 22, 44))
    for sx, sy in [(0.12, 0.22), (0.32, 0.10), (0.55, 0.26), (0.78, 0.12),
                   (0.90, 0.30)]:
        d.ellipse([x + w * sx - 1, y + h * sy - 1, x + w * sx + 1,
                   y + h * sy + 1], fill=(255, 255, 255))
    # city silhouette
    base = y + h
    for bx, bw, bh in [(0.02, 0.14, 0.34), (0.18, 0.10, 0.46),
                       (0.30, 0.12, 0.30), (0.44, 0.09, 0.52),
                       (0.55, 0.13, 0.36), (0.70, 0.11, 0.44),
                       (0.83, 0.14, 0.30)]:
        d.rectangle([x + w * bx, base - h * bh, x + w * (bx + bw), base],
                    fill=(8, 12, 28))
    # missile streaks with fireballs
    for t in [(0.16, 0.14, 0.34, 0.52), (0.52, 0.08, 0.66, 0.46),
              (0.80, 0.20, 0.92, 0.50)]:
        d.line([x + w * t[0], y + h * t[1], x + w * t[2], y + h * t[3]],
               fill=(255, 176, 66), width=3)
        d.ellipse([x + w * t[2] - 5, y + h * t[3] - 5, x + w * t[2] + 5,
                   y + h * t[3] + 5], fill=(255, 200, 80))
    d.polygon([(x + w * 0.66, base - h * 0.46), (x + w * 0.70, base - h * 0.30),
               (x + w * 0.62, base - h * 0.30)], fill=(255, 120, 40))


def scene_cop31(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 232, 216))
    # hall
    d.rectangle([x + w * 0.08, y + h * 0.34, x + w * 0.92, y + h * 0.86],
                fill=(255, 255, 255), outline=(150, 170, 150), width=2)
    d.rectangle([x + w * 0.08, y + h * 0.34, x + w * 0.92, y + h * 0.46],
                fill=NAVY)
    d.text((x + w * 0.14, y + h * 0.365), "COP31 · ANTALYA",
           font=font(F_SANS_B, 12), fill=(255, 255, 255))
    # delegates
    for cx in [0.18, 0.32, 0.46, 0.60, 0.74, 0.86]:
        d.ellipse([x + w * cx - 7, y + h * 0.58 - 7, x + w * cx + 7,
                   y + h * 0.58 + 7], fill=(90, 90, 90))
        d.rectangle([x + w * cx - 10, y + h * 0.66, x + w * cx + 10,
                     y + h * 0.86], fill=(70, 110, 160))
    # thermometer
    tx, ty, th = x + w * 0.90, y + h * 0.10, h * 0.42
    d.rounded_rectangle([tx, ty, tx + 9, ty + th], radius=4,
                        fill=(255, 255, 255), outline=RED, width=2)
    d.rectangle([tx + 2, ty + th * 0.55, tx + 7, ty + th - 2], fill=RED)
    d.ellipse([tx - 3, ty + th - 2, tx + 12, ty + th + 12], fill=RED)


def scene_quake_banda(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 74, 96))
    # sea waves
    for i, yy in enumerate([0.30, 0.44, 0.58]):
        col = (60 + i * 20, 140 + i * 15, 170 + i * 10)
        for kx in range(0, 6):
            sx = x + w * (kx / 6)
            d.arc([sx, y + h * yy, sx + w / 6, y + h * yy + 18], 180, 360,
                  fill=col, width=3)
    # seismograph zigzag
    pts = [(x + w * 0.04, y + h * 0.86), (x + w * 0.14, y + h * 0.86),
           (x + w * 0.20, y + h * 0.70), (x + w * 0.26, y + h * 0.92),
           (x + w * 0.32, y + h * 0.66), (x + w * 0.40, y + h * 0.90),
           (x + w * 0.48, y + h * 0.86), (x + w * 0.58, y + h * 0.70),
           (x + w * 0.66, y + h * 0.92), (x + w * 0.74, y + h * 0.80),
           (x + w * 0.96, y + h * 0.86)]
    d.line(pts, fill=(255, 90, 60), width=3)
    # island
    d.polygon([(x + w * 0.72, y + h * 0.16), (x + w * 0.86, y + h * 0.05),
               (x + w * 0.96, y + h * 0.20), (x + w * 0.80, y + h * 0.26)],
              fill=(46, 110, 70))


def scene_davao(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.ellipse([x + w * 0.74, y + h * 0.08, x + w * 0.92, y + h * 0.30],
              fill=(255, 244, 200))
    for cx, cy, s in [(0.16, 0.24, 1.0), (0.42, 0.14, 0.7), (0.66, 0.30, 0.8)]:
        d.ellipse([x + w * cx, y + h * cy, x + w * (cx + 0.16 * s),
                   y + h * (cy + 0.10 * s)], fill=(255, 255, 255))
    # plane
    px, py = x + w * 0.10, y + h * 0.52
    d.ellipse([px, py - 6, px + w * 0.62, py + 10], fill=(255, 255, 255))
    d.polygon([(px + w * 0.52, py - 2), (px + w * 0.72, py - 16),
               (px + w * 0.76, py - 2)], fill=(200, 200, 200))
    d.polygon([(px + w * 0.30, py + 6), (px + w * 0.44, py + 22),
               (px + w * 0.50, py + 6)], fill=(200, 200, 200))
    d.polygon([(px + w * 0.58, py - 4), (px + w * 0.70, py - 10),
               (px + w * 0.70, py + 2)], fill=NAVY)
    # runway
    d.rectangle([x, y + h * 0.82, x + w, y + h], fill=(70, 70, 70))
    for i in range(7):
        d.rectangle([x + w * (0.05 + i * 0.14), y + h * 0.895,
                     x + w * (0.12 + i * 0.14), y + h * 0.915],
                    fill=(255, 255, 255))


def scene_akvan(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(18, 44, 68))
    cx, cy = x + w * 0.50, y + h * 0.52
    for r, col in [(44, (255, 255, 255)), (34, (140, 190, 220)),
                   (24, (255, 255, 255)), (14, (140, 190, 220))]:
        d.arc([cx - r, cy - r, cx + r, cy + r], 20, 340, fill=col, width=4)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 200, 80))
    # rain
    for rx, ry in [(0.08, 0.10), (0.22, 0.06), (0.84, 0.10), (0.94, 0.30),
                   (0.06, 0.55), (0.92, 0.62)]:
        d.line([x + w * rx, y + h * ry, x + w * rx - 5, y + h * ry + 14],
               fill=(160, 200, 230), width=2)
    # coast
    d.polygon([(x, y + h), (x, y + h * 0.86), (x + w * 0.30, y + h * 0.78),
               (x + w * 0.55, y + h * 0.88), (x + w, y + h * 0.84),
               (x + w, y + h)], fill=(46, 110, 70))


def scene_basra(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 26, 24))
    # power station towers
    for bx, bw, bh in [(0.06, 0.16, 0.60), (0.28, 0.16, 0.72),
                       (0.50, 0.16, 0.58)]:
        d.rectangle([x + w * bx, y + h - h * bh, x + w * (bx + bw), y + h],
                    fill=(120, 120, 120))
        d.rectangle([x + w * (bx + 0.02), y + h - h * bh - 8,
                     x + w * (bx + bw - 0.02), y + h - h * bh],
                    fill=(90, 90, 90))
    # flames
    fx = x + w * 0.72
    d.polygon([(fx, y + h * 0.98), (fx + 12, y + h * 0.52),
               (fx + 26, y + h * 0.98)], fill=(255, 120, 40))
    d.polygon([(fx + 6, y + h * 0.98), (fx + 16, y + h * 0.68),
               (fx + 28, y + h * 0.98)], fill=(255, 200, 80))
    d.ellipse([fx - 2, y + h * 0.44, fx + 34, y + h * 0.66],
              fill=(120, 120, 120))
    d.ellipse([fx + 8, y + h * 0.30, fx + 26, y + h * 0.48],
              fill=(90, 90, 90))


def scene_riyadh(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 22, 44))
    base = y + h
    for bx, bw, bh in [(0.02, 0.12, 0.30), (0.16, 0.10, 0.44),
                       (0.28, 0.14, 0.34), (0.44, 0.09, 0.50),
                       (0.55, 0.12, 0.32), (0.69, 0.11, 0.42),
                       (0.82, 0.15, 0.28)]:
        d.rectangle([x + w * bx, base - h * bh, x + w * (bx + bw), base],
                    fill=(8, 12, 28))
    # three interception bursts
    for bx, by in [(0.22, 0.24), (0.52, 0.16), (0.80, 0.28)]:
        cx, cy = x + w * bx, y + h * by
        for ang in range(0, 360, 45):
            import math
            dx = math.cos(math.radians(ang)) * 12
            dy = math.sin(math.radians(ang)) * 12
            d.line([cx, cy, cx + dx, cy + dy], fill=(255, 200, 80), width=2)
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 255, 255))
        d.line([cx, cy + 10, cx, cy + 30], fill=(255, 176, 66), width=2)


def scene_hormuz(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 226, 232))
    d.rectangle([x, y + h * 0.55, x + w, y + h], fill=SEA)
    for wx in [0.10, 0.30, 0.50, 0.70, 0.88]:
        d.arc([x + w * wx, y + h * 0.60, x + w * (wx + 0.10),
               y + h * 0.60 + 8], 180, 360, fill=(255, 255, 255), width=2)
    # tanker
    d.rectangle([x + w * 0.10, y + h * 0.66, x + w * 0.58, y + h * 0.80],
                fill=(150, 40, 40))
    d.rectangle([x + w * 0.44, y + h * 0.52, x + w * 0.54, y + h * 0.66],
                fill=(255, 255, 255))
    # drone
    dx, dy = x + w * 0.72, y + h * 0.24
    d.ellipse([dx - 8, dy - 5, dx + 8, dy + 5], fill=(60, 60, 60))
    for ox in (-16, 16):
        d.line([dx + ox - 8, dy - 8, dx + ox + 8, dy - 8],
               fill=(90, 90, 90), width=3)
        d.ellipse([dx + ox - 3, dy - 12, dx + ox + 3, dy - 4],
                  fill=(120, 120, 120))
    d.line([dx, dy + 6, dx, dy + 22], fill=(255, 90, 60), width=2)


def scene_quake_peru(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 222, 196))
    # mountains
    d.polygon([(x, y + h * 0.78), (x + w * 0.26, y + h * 0.22),
               (x + w * 0.52, y + h * 0.78)], fill=(120, 90, 60))
    d.polygon([(x + w * 0.34, y + h * 0.78), (x + w * 0.62, y + h * 0.14),
               (x + w * 0.94, y + h * 0.78)], fill=(96, 70, 44))
    d.polygon([(x + w * 0.55, y + h * 0.28), (x + w * 0.62, y + h * 0.14),
               (x + w * 0.70, y + h * 0.30)], fill=(255, 255, 255))
    # houses
    for hx in [0.06, 0.24, 0.76]:
        d.rectangle([x + w * hx, y + h * 0.82, x + w * (hx + 0.12),
                     y + h * 0.96], fill=(200, 120, 70))
        d.polygon([(x + w * hx - 0.01, y + h * 0.82),
                   (x + w * (hx + 0.06), y + h * 0.72),
                   (x + w * (hx + 0.13), y + h * 0.82)], fill=RED_DK)
    # seismograph band
    d.rectangle([x, y + h * 0.60, x + w, y + h * 0.74], fill=(255, 255, 255))
    pts = [(x + w * 0.04, y + h * 0.67), (x + w * 0.16, y + h * 0.67),
           (x + w * 0.22, y + h * 0.62), (x + w * 0.28, y + h * 0.72),
           (x + w * 0.36, y + h * 0.62), (x + w * 0.44, y + h * 0.67),
           (x + w * 0.60, y + h * 0.63), (x + w * 0.68, y + h * 0.71),
           (x + w * 0.76, y + h * 0.67), (x + w * 0.96, y + h * 0.67)]
    d.line(pts, fill=RED, width=2)


def scene_pill(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 238, 244))
    # capsule pills
    for px, py, ang in [(0.18, 0.30, 30), (0.48, 0.22, -25), (0.72, 0.55, 45)]:
        cx, cy = x + w * px, y + h * py
        d.ellipse([cx - 26, cy - 10, cx + 26, cy + 10], fill=(255, 255, 255),
                  outline=NAVY, width=2)
        d.rectangle([cx - 26, cy - 10, cx, cy + 10], fill=NAVY)
    # test tube
    d.rectangle([x + w * 0.12, y + h * 0.62, x + w * 0.24, y + h * 0.94],
                fill=(255, 255, 255), outline=NAVY, width=2)
    d.rectangle([x + w * 0.14, y + h * 0.74, x + w * 0.22, y + h * 0.92],
                fill=(120, 200, 120))
    # cells / microscope dots
    for cx, cy, r in [(0.62, 0.78, 9), (0.78, 0.82, 6), (0.88, 0.72, 5)]:
        d.ellipse([x + w * cx - r, y + h * cy - r, x + w * cx + r,
                   y + h * cy + r], fill=(255, 120, 120), outline=RED, width=1)


def scene_brussels(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(20, 36, 61))
    cx, cy = x + w * 0.50, y + h * 0.46
    import math
    for i in range(12):
        ang = math.radians(i * 30 - 90)
        sx = cx + math.cos(ang) * w * 0.30
        sy = cy + math.sin(ang) * h * 0.30
        d.polygon([(sx, sy - 5), (sx + 1.5, sy - 1.5), (sx + 5, sy),
                   (sx + 1.5, sy + 1.5), (sx, sy + 5), (sx - 1.5, sy + 1.5),
                   (sx - 5, sy), (sx - 1.5, sy - 1.5)], fill=(255, 214, 0))
    d.rectangle([x + w * 0.30, y + h * 0.78, x + w * 0.70, y + h * 0.86],
                fill=(255, 255, 255))
    d.rectangle([x + w * 0.30, y + h * 0.78, x + w * 0.50, y + h * 0.86],
                fill=(178, 34, 34))
    d.rectangle([x + w * 0.50, y + h * 0.78, x + w * 0.70, y + h * 0.86],
                fill=(20, 36, 61))


def scene_poland(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 226, 214))
    # flag
    d.rectangle([x + w * 0.08, y + h * 0.14, x + w * 0.44, y + h * 0.34],
                fill=(255, 255, 255), outline=GREY, width=1)
    d.rectangle([x + w * 0.08, y + h * 0.24, x + w * 0.44, y + h * 0.34],
                fill=RED)
    d.line([x + w * 0.08, y + h * 0.14, x + w * 0.08, y + h * 0.86],
           fill=(90, 90, 90), width=3)
    # missile trails into fields
    for t in [(0.55, 0.10, 0.72, 0.55), (0.78, 0.06, 0.88, 0.42)]:
        d.line([x + w * t[0], y + h * t[1], x + w * t[2], y + h * t[3]],
               fill=(255, 176, 66), width=3)
        d.ellipse([x + w * t[2] - 4, y + h * t[3] - 4, x + w * t[2] + 4,
                   y + h * t[3] + 4], fill=(255, 120, 40))
    d.polygon([(x, y + h * 0.86), (x + w, y + h * 0.86), (x + w, y + h),
               (x, y + h)], fill=(46, 110, 70))
    d.polygon([(x + w * 0.70, y + h * 0.86), (x + w * 0.76, y + h * 0.66),
               (x + w * 0.82, y + h * 0.86)], fill=(120, 120, 120))


def scene_madrid(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 222, 180))
    d.ellipse([x + w * 0.70, y + h * 0.06, x + w * 0.92, y + h * 0.32],
              fill=(255, 214, 0))
    # parliament columns
    d.rectangle([x + w * 0.10, y + h * 0.30, x + w * 0.90, y + h * 0.40],
                fill=(200, 180, 140))
    d.polygon([(x + w * 0.06, y + h * 0.30), (x + w * 0.50, y + h * 0.12),
               (x + w * 0.94, y + h * 0.30)], fill=(214, 196, 158))
    for cx in [0.18, 0.32, 0.46, 0.60, 0.74]:
        d.rectangle([x + w * cx - 6, y + h * 0.42, x + w * cx + 6,
                     y + h * 0.82], fill=(255, 250, 240))
    d.rectangle([x + w * 0.08, y + h * 0.82, x + w * 0.92, y + h * 0.90],
                fill=(200, 180, 140))
    # coins
    for cx, cy in [(0.30, 0.72), (0.44, 0.70), (0.58, 0.72)]:
        d.ellipse([x + w * cx - 7, y + h * cy - 7, x + w * cx + 7,
                   y + h * cy + 7], fill=(255, 214, 0),
                  outline=(148, 110, 28), width=1)


SCENES = {
    "kyiv": scene_kyiv, "cop31": scene_cop31, "quake_banda": scene_quake_banda,
    "davao": scene_davao, "akvan": scene_akvan, "basra": scene_basra,
    "riyadh": scene_riyadh, "hormuz": scene_hormuz,
    "quake_peru": scene_quake_peru, "pill": scene_pill,
    "brussels": scene_brussels, "poland": scene_poland,
    "madrid": scene_madrid,
}

# ---------------------------------------------------------------- world map

CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-120, 72), (-95, 70), (-82, 66), (-75, 58),
     (-65, 50), (-55, 47), (-70, 42), (-75, 35), (-80, 30), (-84, 25),
     (-90, 20), (-97, 16), (-105, 20), (-110, 24), (-120, 34),
     (-125, 42), (-130, 55), (-150, 60), (-165, 60)],
    # South America
    [(-79, 9), (-72, 12), (-62, 10), (-52, 5), (-44, -3), (-35, -8),
     (-40, -20), (-48, -28), (-58, -38), (-65, -45), (-70, -52),
     (-73, -40), (-72, -25), (-80, -12), (-81, -4)],
    # Africa
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (32, 31),
     (35, 28), (43, 12), (51, 11), (48, 0), (40, -10), (36, -20),
     (33, -28), (20, -35), (12, -18), (9, -2), (8, 4), (-8, 4)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (12, 55),
     (18, 56), (21, 55), (24, 58), (30, 60), (30, 70), (20, 70),
     (12, 65), (5, 60), (5, 58), (-5, 50), (-10, 44)],
    # Asia
    [(30, 36), (36, 36), (42, 41), (50, 42), (58, 39), (62, 37),
     (68, 40), (75, 40), (80, 35), (88, 22), (92, 16), (98, 8),
     (100, 6), (104, 2), (108, 12), (114, 22), (120, 28), (122, 32),
     (127, 35), (130, 42), (135, 44), (142, 50), (158, 52), (170, 60),
     (178, 65), (170, 70), (140, 72), (110, 74), (80, 73), (60, 69),
     (50, 68), (40, 66), (32, 68), (32, 60), (35, 45)],
    # Australia
    [(113, -22), (114, -32), (124, -33), (134, -33), (140, -38),
     (150, -37), (153, -28), (146, -19), (142, -11), (132, -12),
     (122, -14)],
]


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 52, 84))
    # graticule
    for gx in range(1, 12):
        gx0 = x + w * gx / 12
        d.line([gx0, y, gx0, y + h], fill=(48, 70, 104), width=1)
    for gy in range(1, 6):
        gy0 = y + h * gy / 6
        d.line([x, gy0, x + w, gy0], fill=(48, 70, 104), width=1)

    def px(lon, lat):
        return x + (lon + 180) / 360 * w, y + (75 - lat) / 130 * h

    for cont in CONTINENTS:
        pts = [px(lon, lat) for lon, lat in cont]
        d.polygon(pts, fill=(232, 214, 176), outline=(200, 180, 140))
    # pins
    for n, lat, lon in PINS:
        px0, py0 = px(lon, lat)
        r = 8
        d.ellipse([px0 - r, py0 - r, px0 + r, py0 + r], fill=RED,
                  outline=(255, 255, 255), width=1)
        f = font(F_SANS_B, 10 if n < 10 else 8)
        tw = d.textlength(str(n), font=f)
        d.text((px0 - tw / 2, py0 - 6 if n < 10 else py0 - 5), str(n),
               font=f, fill=(255, 255, 255))


# ---------------------------------------------------------------- layout

def hero_card(d, x, y, w, h, item):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=(200, 190, 170),
                width=1)
    sh = 112
    SCENES[item["scene"]](d, x + 1, y + 1, w - 2, sh - 1)
    # big-number chip on the scene, bottom-left
    f_big = font(F_SANS_B, 22)
    f_lbl = font(F_SANS, 10)
    bw = max(d.textlength(item["big"], font=f_big),
             d.textlength(item["big_label"], font=f_lbl)) + 16
    d.rectangle([x + 6, y + sh - 40, x + 6 + bw, y + sh - 6], fill=NAVY)
    d.text((x + 14, y + sh - 38), item["big"], font=f_big,
           fill=(255, 255, 255))
    d.text((x + 14, y + sh - 16), item["big_label"], font=f_lbl,
           fill=(200, 210, 230))
    num_chip(d, x + w - 18, y + 18, item["num"])
    ty = y + sh + 6
    d.text((x + 8, ty), item["tag"], font=font(F_SANS_B, 10), fill=RED)
    ty += 14
    d.text((x + 8, ty), item["place"], font=font(F_SANS, 9), fill=GREY)
    ty += 13
    lines = fit_lines(d, item["head"], font(F_HEAD, 19), w - 16, 2)
    ty = text_block(d, x + 8, ty, lines, font(F_HEAD, 19), INK, 22)
    lines = fit_lines(d, item["body"], font(F_SANS, 11.5), w - 16, 3)
    ty = text_block(d, x + 8, ty + 2, lines, font(F_SANS, 11.5), INK, 14.5)
    d.text((x + 8, y + h - 15), "Source: " + item["src"],
           font=font(F_SANS, 9.5), fill=GREY)


def grid_card(d, x, y, w, h, item):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=(200, 190, 170),
                width=1)
    sh = 54
    SCENES[item["scene"]](d, x + 1, y + 1, w - 2, sh - 1)
    # big number chip, bottom-left of the scene
    f_big = font(F_SANS_B, 15)
    f_lbl = font(F_SANS, 8)
    bw = max(d.textlength(item["big"], font=f_big),
             d.textlength(item["big_label"], font=f_lbl)) + 10
    d.rectangle([x + 4, y + sh - 26, x + 4 + bw, y + sh - 4], fill=NAVY)
    d.text((x + 9, y + sh - 25), item["big"], font=f_big,
           fill=(255, 255, 255))
    d.text((x + 9, y + sh - 11), item["big_label"], font=f_lbl,
           fill=(200, 210, 230))
    num_chip(d, x + w - 14, y + 14, item["num"], r=9)
    ty = y + sh + 4
    d.text((x + 6, ty), item["tag"], font=font(F_SANS_B, 8.5), fill=RED)
    ty += 12
    lines = fit_lines(d, item["head"], font(F_HEAD, 14.5), w - 12, 2)
    ty = text_block(d, x + 6, ty, lines, font(F_HEAD, 14.5), INK, 16.5)
    lines = fit_lines(d, item["body"], font(F_SANS, 11), w - 12, 2)
    ty = text_block(d, x + 6, ty + 1, lines, font(F_SANS, 11), INK, 13)
    d.text((x + 6, y + h - 13), "Source: " + item["src"],
           font=font(F_SANS, 9), fill=GREY)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = 8

    # masthead
    d.text((MX, y), "THE WORLD IN ONE DAY", font=font(F_SANS_B, 13), fill=NAVY)
    right = "35 STORIES · 6 REGIONS · EVERY ONE DATED"
    rw = d.textlength(right, font=font(F_SANS_B, 11))
    d.text((MX + CW - rw, y + 1), right, font=font(F_SANS_B, 11), fill=GREY)
    y += 18
    d.text((MX, y), "Saturday 21 November 2026",
           font=font(F_SERIF, 52), fill=NAVY)
    y += 60
    d.text((MX, y), "War, weather and a climate summit in overtime — "
           "the day in 35 stories.",
           font=font(F_SERIF_IT, 16), fill=INK)
    y += 22
    d.rectangle([MX, y, MX + CW, y + 3], fill=RED)
    y += 9

    # 6-number strip
    cell = CW // 6
    for i, (num, cap) in enumerate(STRIP):
        cx = MX + i * cell
        d.text((cx + 8, y), num, font=font(F_SANS_B, 27), fill=NAVY)
        d.text((cx + 8, y + 30), cap, font=font(F_SANS, 10), fill=GREY)
        if i:
            d.line([cx, y + 2, cx, y + 42], fill=(200, 190, 170), width=1)
    y += 48
    d.rectangle([MX, y, MX + CW, y + 2], fill=NAVY)
    y += 6

    # region bar (equal tabs; proportional segments squeezed WORLD/OCEANIA)
    x = MX
    seg = CW // 6
    for name, count, col in REGIONS:
        d.rectangle([x, y, x + seg - 1, y + 20], fill=col)
        label = f"{name} {count}"
        f = font(F_SANS_B, 10)
        tw = d.textlength(label, font=f)
        d.text((x + (seg - tw) / 2, y + 4), label, font=f,
               fill=(255, 255, 255))
        x += seg
    y += 26

    # heroes
    hw = (CW - 30) // 3
    for i, item in enumerate(HEROES):
        hero_card(d, MX + i * (hw + 15), y, hw, 258, item)
    y += 258 + 6

    # grid rows
    gw = (CW - 48) // 5
    for row in range(2):
        for i in range(5):
            item = GRID[row * 5 + i]
            grid_card(d, MX + i * (gw + 12), y, gw, 148, item)
        y += 148 + 4
    y -= 4

    # map + ALSO ON
    map_w, also_w = 330, CW - 330 - 14
    d.text((MX + map_w + 14, y + 1), "ALSO ON SATURDAY 21 NOVEMBER",
           font=font(F_SANS_B, 11), fill=NAVY)
    draw_map(d, MX, y, map_w, 130)
    ay = y + 16
    f_ao = font(F_SANS, 11)
    for col_i in range(2):
        ax = MX + map_w + 14 + col_i * (also_w // 2)
        for j in range(11):
            text, src = ALSO_ON[col_i * 11 + j]
            line = f"• {text} — {src}"
            d.text((ax, ay + j * 10.5), line, font=f_ao, fill=INK)
    y += 130 + 6

    # VERDICT / HOW SURE / MARKETS
    bw1, bw2, bw3 = 470, 290, CW - 470 - 290 - 12
    boxes = [
        (MX, bw1, "VERDICT",
         "War, weather and a climate summit in overtime."),
        (MX + bw1 + 6, bw2, "HOW SURE",
         "CONFIRMED — named official source | REPORTED — single source"),
        (MX + bw1 + bw2 + 12, bw3, "MARKETS",
         "Bitcoin below $59,000 on Saturday (CoinGecko)"),
    ]
    for bx, bwid, label, body in boxes:
        d.rectangle([bx, y, bx + bwid, y + 42], fill=CARD,
                    outline=(200, 190, 170), width=1)
        d.text((bx + 8, y + 4), label, font=font(F_SANS_B, 10), fill=RED)
        if " | " in body:
            lines = body.split(" | ")
        else:
            lines = fit_lines(d, body, font(F_SANS, 11), bwid - 16, 2)
        text_block(d, bx + 8, y + 18, lines, font(F_SANS, 11), INK, 12)
    y += 42 + 6

    # DATE CHECK
    d.rectangle([MX, y, MX + CW, y + 46], fill=(238, 232, 214),
                outline=(200, 190, 170), width=1)
    d.text((MX + 8, y + 4), "DATE CHECK", font=font(F_SANS_B, 10),
           fill=RED)
    f_dc = font(F_SANS, 11)
    d.text((MX + 8, y + 18),
           "Left out as Friday 20 Nov news: Kyiv barrage (8 killed), "
           "Akvan's landfall, COP31 draft (144→80), Wall Street's "
           "correction, Shenzhen summit, ICJ ruling, Anthropic IPO, "
           "GTA VI release.", font=f_dc, fill=INK)
    d.text((MX + 8, y + 32),
           "Not confirmed, so not shown: a final COP31 text; the exact "
           "Kryvyi Rih wounded count (47 vs 58). Dated as Saturday by "
           "UTC: the Peru quake (00:09 UTC) and the Davao landing.",
           font=f_dc, fill=INK)
    y += 46 + 6

    # footer
    foot = ("Every story verified against a named source for "
            "Saturday 21 November 2026.")
    fw = d.textlength(foot, font=font(F_SANS, 10))
    d.text(((W - fw) / 2, y), foot, font=font(F_SANS, 10), fill=GREY)
    y += 14
    return img, y


def main():
    img, bottom = build()
    assert bottom <= H, f"layout overflow: bottom={bottom} > {H}"
    img.save("entry.png", format="PNG", optimize=True)
    print(f"entry.png written, layout bottom y={bottom}")


if __name__ == "__main__":
    main()
