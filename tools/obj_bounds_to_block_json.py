#!/usr/bin/env python3
"""Convert OBJ mesh into Forge 1.20.1 vanilla block-model JSON approximations.

This emits cuboid elements for each OBJ object's axis-aligned bounds. It is a
safe, valid Minecraft model JSON fallback, NOT a lossless mesh conversion.
OBJ textures are not changed; texture bindings must match the existing assets.
"""
import json, pathlib, sys

def convert(src, dst, texture):
    vertices = []
    groups = []
    name = pathlib.Path(src).stem
    current = {"name": name, "verts": []}
    for raw in pathlib.Path(src).read_text(encoding="utf-8", errors="replace").splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        p = s.split()
        if p[0] == "v" and len(p) >= 4:
            v = tuple(float(x) for x in p[1:4])
            vertices.append(v)
            current["verts"].append(v)
        elif p[0] in ("o", "g") and current["verts"]:
            groups.append(current)
            current = {"name": " ".join(p[1:]) or name, "verts": []}
    if current["verts"]:
        groups.append(current)
    if not vertices:
        raise SystemExit(f"No vertices in {src}")
    mins = [min(v[i] for v in vertices) for i in range(3)]
    maxs = [max(v[i] for v in vertices) for i in range(3)]
    dims = [maxs[i]-mins[i] for i in range(3)]
    if any(d <= 1e-8 for d in dims):
        raise SystemExit("Degenerate OBJ bounds")
    # Normalize bounds into a 16x16x16 block space; geometry is represented
    # as one cuboid per named OBJ group, so this is an intentionally simplified fallback.
    scale = min(16.0/d for d in dims)
    offset = [(16.0-d*scale)/2 for d in dims]
    elements = []
    for g in groups:
        if not g["verts"]:
            continue
        lo = [min(v[i] for v in g["verts"]) for i in range(3)]
        hi = [max(v[i] for v in g["verts"]) for i in range(3)]
        a = [max(0.0, min(16.0, (lo[i]-mins[i])*scale+offset[i])) for i in range(3)]
        b = [max(0.0, min(16.0, (hi[i]-mins[i])*scale+offset[i])) for i in range(3)]
        if any(b[i]-a[i] < 0.01 for i in range(3)):
            continue
        elements.append({
            "name": g["name"][:64],
            "from": [round(x,4) for x in a],
            "to": [round(x,4) for x in b],
            "faces": {face: {"texture": "#all"} for face in
                      ("north","south","east","west","up","down")}
        })
    if not elements:
        elements = [{"from":[1,0,1],"to":[15,16,15],
                     "faces":{f:{"texture":"#all"} for f in ("north","south","east","west","up","down")}}]
    data = {"credit":"Generated from OBJ bounds; simplified cuboid approximation.",
            "textures":{"all":texture,"particle":texture}, "elements":elements}
    pathlib.Path(dst).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(dst).write_text(json.dumps(data, indent=2)+"\n", encoding="utf-8")
    print(f"{dst}: {len(elements)} cuboid elements; normalized OBJ bounds {dims}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("Usage: obj_bounds_to_block_json.py input.obj output.json namespace:block/texture")
    convert(*sys.argv[1:])
