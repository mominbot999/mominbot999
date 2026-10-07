"""Chinese ink-wash (shan shui) landscape background, 1920x1080, drawn through the VectorCraft MCP server."""
import json, math, random, sys
from vc import VC

W, H = 1920, 1080
OUT = sys.argv[1]
random.seed(8)
v = VC()

def oid(txt):
    try:
        d = json.loads(txt)
    except Exception:
        return None
    return d.get("id") or (d.get("ids") or [None])[0]

def path(pts, fill=None, stroke="none", sw=None, closed=True, opacity=None, blur=None):
    a = {"points": [[round(x, 2), round(y, 2)] for x, y in pts], "closed": closed, "stroke": stroke}
    a["fill"] = fill if fill is not None else "none"
    if sw is not None: a["strokeWidth"] = sw
    i = oid(v.call("draw_path", **a))
    finish(i, opacity, blur)
    return i

def shape(fill, opacity=None, blur=None, stroke="none", **kw):
    i = oid(v.call("draw_shape", fill=fill, stroke=stroke, **kw))
    finish(i, opacity, blur)
    return i

def finish(i, opacity, blur):
    if opacity is not None:
        v.call("run_command", command="transparency.set", params={"ids": [i], "opacity": opacity})
    if blur:
        v.call("apply_effect", ids=[i], effect="blur.gaussian", params={"radius": blur})

def vgrad(y0, y1, stops):
    return {"gradient": {"kind": "linear", "start": [W / 2, y0], "end": [W / 2, y1],
                         "stops": [{"offset": o, "color": c, "opacity": op} for o, c, op in stops]}}

def ridge(x0, x1, base, peaks, step=6):
    """Ridgeline: sum of soft peaks (cx, height, width) plus fine noise."""
    ph = [random.uniform(0, 6.28) for _ in range(3)]
    pts = []
    x = x0
    while x <= x1:
        y = base
        for cx, h, w in peaks:
            y -= h * math.exp(-((x - cx) / w) ** 2)
        y += 6 * math.sin(x / 37 + ph[0]) + 3 * math.sin(x / 13 + ph[1]) + 1.5 * math.sin(x / 5 + ph[2])
        pts.append((x, y))
        x += step
    return pts

# --- canvas -----------------------------------------------------------------
v.call("run_command", command="artboard.setProps", params={"index": 0, "x": 0, "y": 0, "width": W, "height": H, "name": "Shan Shui"})

# rice-paper sky
shape(vgrad(0, H, [(0, "#efe4cc", 1), (0.55, "#f5ecd8", 1), (1, "#e9dcc0", 1)]), shape="rectangle", x=0, y=0, width=W, height=H)
# faint paper fibres
for _ in range(70):
    x, y = random.uniform(0, W), random.uniform(0, H)
    L, ang = random.uniform(30, 160), random.uniform(-0.3, 0.3)
    path([(x, y), (x + L * math.cos(ang), y + L * math.sin(ang))], stroke="#c9b48e", sw=0.6, closed=False, opacity=18)

# vermilion sun with glow
shape("#e8a07a", opacity=35, blur=40, shape="ellipse", x=1270, y=130, width=280, height=280)
shape(vgrad(170, 370, [(0, "#d9452b", 1), (1, "#c23a24", 1)]), opacity=88, shape="ellipse", x=1320, y=180, width=180, height=180)

# --- mountains, far to near ---------------------------------------------------
layers = [
    # base, peaks, top colour, opacity, blur
    (620, [(250, 260, 140), (520, 180, 120), (1050, 230, 160), (1700, 300, 150)], "#9aa3a0", 55, 6),
    (700, [(120, 230, 110), (760, 330, 120), (900, 250, 90), (1480, 260, 140), (1880, 200, 120)], "#6f7a78", 70, 3),
    (800, [(380, 420, 115), (470, 300, 70), (1180, 280, 150), (1600, 360, 110)], "#3e4746", 85, 1.5),
]
for base, peaks, col, op, blur in layers:
    pts = ridge(-20, W + 20, base, peaks)
    top = min(y for _, y in pts)
    path(pts + [(W + 20, H), (-20, H)],
         fill=vgrad(top, base + 60, [(0, col, 1), (0.6, col, 0.75), (1, "#f2e8d2", 0)]),
         opacity=op, blur=blur)
    # mist band at the foot of each range
    shape("#f6eedc", opacity=80, blur=30, shape="rectangle", x=-50, y=base - 40, width=W + 100, height=90)

# ink texture strokes (cun) on the nearest peak
for _ in range(26):
    x = random.uniform(300, 520); y = random.uniform(420, 700)
    path([(x, y), (x + random.uniform(-14, 6), y + random.uniform(20, 55))], stroke="#1f2524", sw=random.uniform(1, 2.6), closed=False, opacity=45)

# foreground cliff, lower left
cliff = ridge(-20, 980, 1000, [(90, 380, 140), (330, 200, 160), (600, 90, 120), (-200, -120, 1)], step=5)
cliff = [(x, y + max(0, x - 640) ** 2 / 900) for x, y in cliff]
path(cliff + [(980, H + 200), (-20, H + 200)], fill=vgrad(600, H, [(0, "#1d2221", 1), (1, "#2e3533", 0.9)]), opacity=95)

# pavilion on the cliff
px, py = 250, 793
for y_, w_ in [(py, 120), (py - 34, 90)]:
    path([(px - w_ / 2 - 14, y_), (px, y_ - 30), (px + w_ / 2 + 14, y_), (px + w_ / 2 + 22, y_ - 9), (px, y_ - 40), (px - w_ / 2 - 22, y_ - 9)], fill="#141817")
for dx in (-42, 42):
    shape("#141817", shape="rectangle", x=px + dx - 3, y=py, width=6, height=40)
shape("#a8321f", shape="rectangle", x=px - 46, y=py + 34, width=92, height=7)
path([(px, py - 74), (px, py - 90)], stroke="#141817", sw=3, closed=False)

# pine on the cliff edge
tx, ty = 560, 905
path([(tx, ty), (tx - 10, ty - 80), (tx + 8, ty - 160), (tx - 6, ty - 240)], stroke="#141817", sw=9, closed=False)
for k, (bx, by, L, d) in enumerate([(tx - 8, ty - 90, 120, -1), (tx + 6, ty - 150, 150, 1), (tx - 4, ty - 220, 100, -1), (tx + 2, ty - 245, 80, 1)]):
    path([(bx, by), (bx + d * L * 0.5, by - 18), (bx + d * L, by - 6)], stroke="#141817", sw=4, closed=False)
    for j in range(3):
        cx = bx + d * L * (0.45 + 0.28 * j); cy = by - 16 + random.uniform(-6, 6)
        shape("#253b2f", opacity=90, shape="ellipse", x=cx - 34, y=cy - 13, width=68, height=26)

# --- plum blossom branch, top left --------------------------------------------
def branch(p0, p1, w0, w1):
    (x0, y0), (x1, y1) = p0, p1
    a = math.atan2(y1 - y0, x1 - x0) + math.pi / 2
    mx, my = (x0 + x1) / 2 + random.uniform(-12, 12), (y0 + y1) / 2 + random.uniform(-12, 12)
    nx, ny = math.cos(a), math.sin(a)
    wm = (w0 + w1) / 2
    path([(x0 + nx * w0, y0 + ny * w0), (mx + nx * wm, my + ny * wm), (x1 + nx * w1, y1 + ny * w1),
          (x1 - nx * w1, y1 - ny * w1), (mx - nx * wm, my - ny * wm), (x0 - nx * w0, y0 - ny * w0)], fill="#2a1d18")

tips = []
def grow(x, y, ang, L, w, depth):
    x2, y2 = x + L * math.cos(ang), y + L * math.sin(ang)
    branch((x, y), (x2, y2), w, w * 0.62)
    tips.append((x2, y2))
    if random.random() < 0.6: tips.append(((x + x2) / 2, (y + y2) / 2))
    if depth:
        grow(x2, y2, ang + random.uniform(-0.55, -0.15), L * 0.72, w * 0.62, depth - 1)
        if random.random() < 0.8:
            grow(x2, y2, ang + random.uniform(0.2, 0.6), L * 0.6, w * 0.55, depth - 1)

grow(-30, 40, 0.38, 260, 15, 4)
for x, y in tips:
    for _ in range(random.choice([1, 1, 2])):
        cx, cy, r = x + random.uniform(-10, 10), y + random.uniform(-10, 10), random.uniform(9, 14)
        for p in range(5):
            a = p * 2 * math.pi / 5 + random.uniform(-0.1, 0.1)
            shape("#d4404a", opacity=82, shape="ellipse", x=cx + r * 0.75 * math.cos(a) - r * 0.6, y=cy + r * 0.75 * math.sin(a) - r * 0.6, width=r * 1.2, height=r * 1.2)
        shape("#f3d36b", shape="ellipse", x=cx - 2.5, y=cy - 2.5, width=5, height=5)

# --- birds ---------------------------------------------------------------------
for bx, by, s in [(1060, 260, 1.0), (1110, 290, 0.8), (990, 300, 0.7), (1160, 240, 0.6), (1030, 340, 0.55)]:
    path([(bx - 16 * s, by - 4 * s), (bx - 7 * s, by - 6 * s), (bx, by + 2 * s), (bx + 7 * s, by - 6 * s), (bx + 16 * s, by - 4 * s)],
         stroke="#1b1f1e", sw=2.2 * s, closed=False)

# --- river with a fishing boat ------------------------------------------------------
for i in range(9):
    y = 935 + i * 15; x = random.uniform(820, 1500)
    path([(x, y), (x + random.uniform(90, 260), y)], stroke="#8c958f", sw=1.2, closed=False, opacity=45)
bx, by = 1180, 960
path([(bx - 70, by), (bx + 70, by), (bx + 52, by + 14), (bx - 52, by + 14)], fill="#1c2120")
path([(bx + 10, by), (bx + 10, by - 34)], stroke="#1c2120", sw=3, closed=False)
path([(bx - 4, by - 30), (bx + 10, by - 44), (bx + 24, by - 30)], fill="#1c2120")
path([(bx + 20, by - 20), (bx + 110, by - 70)], stroke="#1c2120", sw=1.6, closed=False)

# --- calligraphy and seal, right edge ------------------------------------------------
v.call("add_text", text="山\n水\n清\n音", x=1780, y=520, font="WenQuanYi Zen Hei", size=58, color="#1a1a1a")
shape("#b8301e", opacity=92, shape="rectangle", x=1772, y=820, width=74, height=74, radius=6)
v.call("add_text", text="墨韵", x=1781, y=869, font="WenQuanYi Zen Hei", size=28, color="#f6ead2")

v.call("save_file", path=OUT + ".vectorcraft")
print(v.call("export", path=OUT + ".svg", format="svg", outlineText=True))
print(v.call("export", path=OUT + ".png", format="png"))
print(v.call("export", path=OUT + "@2x.png", format="png", options={"scale": 2}))
