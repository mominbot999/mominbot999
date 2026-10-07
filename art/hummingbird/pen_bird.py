"""Redraw the traced hummingbird with the Pen tool, then refine handles with the Anchor Point tool.

Pointer gestures only, the way a person draws it: the outlines come from trace.svg (VectorCraft's Image
Trace of the source picture), used as the reference to follow.

  Pen:          click = corner anchor, drag = smooth anchor (symmetric handles), click the first anchor = close.
  Anchor Point: drag a handle = move it on its own (uneven handles, cusps); drag an anchor = pull out handles.

Drawn at S x scale so the tools' 4-5 pt hit tolerances are a fraction of a source pixel, then scaled back.
"""
import json, math, re, sys
from vc import VC

S = 20
W, H = 800, 712
OUT = sys.argv[1]
EPS = 0.01  # source px: handle shorter than this counts as none

def parse(d):
    toks = re.findall(r"[MLCZ]|-?[\d.]+(?:e-?\d+)?", d)
    i, anchors, cmd = 0, [], None
    while i < len(toks):
        t = toks[i]
        if t in "MLCZ":
            cmd = t; i += 1
            if t == "Z": continue
        n = {"M": 2, "L": 2, "C": 6}[cmd]
        v = [float(x) for x in toks[i:i + n]]; i += n
        if cmd in "ML":
            anchors.append({"p": (v[0], v[1]), "in": None, "out": None})
        else:
            anchors[-1]["out"] = (v[0], v[1])
            anchors.append({"p": (v[4], v[5]), "in": (v[2], v[3]), "out": None})
        if cmd == "M": cmd = "L"
    a0, an = anchors[0], anchors[-1]
    if len(anchors) > 1 and math.dist(a0["p"], an["p"]) < 1e-6:
        a0["in"] = an["in"]; anchors.pop()
    for a in anchors:  # normalise: no handle -> the anchor itself
        for k in ("in", "out"):
            if a[k] is None or math.dist(a[k], a["p"]) < EPS:
                a[k] = a["p"]
    return anchors

def has(a, k): return math.dist(a[k], a["p"]) >= EPS
def refl(p, h): return (2 * p[0] - h[0], 2 * p[1] - h[1])
def sc(pt): return {"x": round(pt[0] * S, 4), "y": round(pt[1] * S, 4)}
def click(pt): return [{"kind": "down", **sc(pt)}, {"kind": "up", **sc(pt)}]
def drag(a, b): return [{"kind": "down", **sc(a)}, {"kind": "drag", **sc(b)}, {"kind": "up", **sc(b)}]

# Start each shape on a corner anchor when it has one: the first click and the closing click then need no handles.
def rotate(anchors):
    for k, a in enumerate(anchors):
        if not has(a, "in") and not has(a, "out"):
            return anchors[k:] + anchors[:k]
    return anchors

svg = open("reference-trace.svg").read()
paths = [rotate(parse(d)) for d in re.findall(r'<path d="([^"]+)"', svg)]

v = VC()
v.call("run_command", command="artboard.setProps", params={"index": 0, "x": 0, "y": 0, "width": W * S, "height": H * S, "name": "Hummingbird"})
v.call("set_paint", fill="#1a1a1a", stroke="none")
stats = {"pen click": 0, "pen drag": 0, "anchor-point drags": 0}

for anchors in paths:
    # --- Pen ---
    v.call("select_tool", tool="pen")
    v.call("run_command", command="select.none")
    placed = []  # handles each anchor has after the Pen: (in, out)
    for k, a in enumerate(anchors):
        if k == 0 or (not has(a, "in") and not has(a, "out")):
            v.call("pointer_gesture", events=click(a["p"])); stats["pen click"] += 1
            placed.append((a["p"], a["p"]))
        else:
            out = a["out"] if has(a, "out") else refl(a["p"], a["in"])
            v.call("pointer_gesture", events=drag(a["p"], out)); stats["pen drag"] += 1
            placed.append((refl(a["p"], out), out))
    v.call("pointer_gesture", events=click(anchors[0]["p"]))  # close
    # --- Anchor Point tool: make every handle exactly match the reference ---
    v.call("select_tool", tool="anchorPoint")
    a0 = anchors[0]
    if has(a0, "in") or has(a0, "out"):  # the start anchor: pull handles out of it
        out = a0["out"] if has(a0, "out") else refl(a0["p"], a0["in"])
        v.call("pointer_gesture", events=drag(a0["p"], out)); stats["anchor-point drags"] += 1
        placed[0] = (refl(a0["p"], out), out)
    for a, (pin, pout) in zip(anchors, placed):
        if math.dist(pout, a["out"]) >= EPS:
            v.call("pointer_gesture", events=drag(pout, a["out"])); stats["anchor-point drags"] += 1
        if math.dist(pin, a["in"]) >= EPS:
            v.call("pointer_gesture", events=drag(pin, a["in"])); stats["anchor-point drags"] += 1

v.call("select_tool", tool="selection")
v.call("run_command", command="select.all")
v.call("run_command", command="object.group")
v.call("transform", scale=100 / S, origin=[0, 0])
v.call("run_command", command="artboard.setProps", params={"index": 0, "x": 0, "y": 0, "width": W, "height": H})
v.call("run_command", command="select.none")
v.call("save_file", path=OUT + ".vectorcraft")
v.call("export", path=OUT + ".svg", format="svg")
v.call("export", path=OUT + ".png", format="png")
v.call("export", path=OUT + "@4x.png", format="png", options={"scale": 4})
d = json.loads(v.call("inspect_document"))
print(json.dumps(stats), "shapes:", len(paths), "objects:", d["objects"], "undo steps:", len(d["history"]))
