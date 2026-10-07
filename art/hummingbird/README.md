# Hummingbird (Pen tool)

The hummingbird stencil from `reference.png`, redrawn in VectorCraft with the **Pen tool**: 22 closed
shapes and 786 anchor points, filled `#1a1a1a`.

| File | What |
|---|---|
| `hummingbird.svg` | Vector (800 × 712) |
| `hummingbird.png`, `hummingbird@4x.png` | 800 × 712 and 3200 × 2848 |
| `hummingbird.vectorcraft` | Editable VectorCraft document |
| `reference.png` | The source picture |
| `reference-trace.svg` | Image Trace of the source, used as the outline to follow |
| `pen_bird.py` | The script that drives the tools (needs `../vc.py`) |

How it was drawn, all through `pointer_gesture`:

1. **Pen**: click for each corner anchor, click-drag for each curved anchor, click the first anchor to close.
   Each shape starts on a corner anchor.
2. **Anchor Point tool** (Shift+C): drag individual handles where a curve needs uneven handles or a cusp.

The result overlaps the source picture by 97.7% of pixels (98.9% against the trace).

Regenerate from this folder: `VECTORCRAFT_CLI=/path/to/vectorcraft-cli PYTHONPATH=.. python3 pen_bird.py out/hummingbird`
