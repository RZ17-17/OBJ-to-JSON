#!/usr/bin/env python3
"""Create Forge 1.20.1 block-model JSON from OBJ using per-group vertex bounds.

Minecraft vanilla JSON only supports cuboids, not arbitrary OBJ triangles. This
converter preserves separate OBJ object/group bounds as a cuboid approximation;
it does not claim lossless mesh conversion.
"""
import json, pathlib, sys

def convert(src, dst, texture):
    vertices = []
    groups = []
    current_name = pathlib.Path(src).stem
    current_faces = []
    def flush():
        nonlocal current_faces
        if current_faces:
            groups.append((current_name, current_faces))
        current_faces = []
    for raw in pathlib.Path(src).read_text(encoding="utf-8", errors="replace").splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        p = s.split()
        if p[0] == "v" and len(p) >= 4:
            vertices.append(tuple(float(x) for x in p[1:4]))
        elif p[0] in ("o", "g"):
            flush()
            current_name = " ".join(p[1:]) or pathlib.Path(src).stem
        elif p[0] == "f" and len(p) >= 4:
            # OBJ face vertex indices are global and may be negative.
            ids = []
            for item in p[1:]:
                idx = int(item.split("/")[0])
                ids.append(idx - 1 if idx > 0 else len(vertices) + idx)
            current_faces.extend(i for i in ids if 0 <= i < len(vertices))
    flush()
    if not vertices:
        raise SystemExit(f"No vertices in {src}")
    mins = [min(v[i] for v in vertices) for i in range(3)]
    maxs = [max(v[i] for v in vertices) for i in range(3)]
    dims = [maxs[i]-mins[i] for i in range(3)]
    if any(d <= 1e-8 for d in dims):
        raise SystemExit("Degenerate OBJ bounds")
    scale = min(16.0/d for d in dims)
    offset = [(16.0-d*scale)/2 for d in dims]
    elements = []
    for name, ids in groups:
        if not ids:
            continue
        verts = [vertices[i] for i in ids]
        lo = [min(v[i] for v in verts) for i in range(3)]
        hi = [max(v[i] for v in verts) for i in range(3)]
        a = [max(0.0, min(16.0, (lo[i]-mins[i])*scale+offset[i])) for i in range(3)]
        b = [max(0.0, min(16.0, (hi[i]-mins[i])*scale+offset[i])) for i in range(3)]
        if any(b[i]-a[i] < 0.01 for i in range(3)):
            continue
        elements.append({"name": name[:64], "from":[round(x,4) for x in a],
            "to":[round(x,4) for x in b],
            "faces":{f:{"texture":"#all"} for f in ("north","south","east","west","up","down")}})
    if not elements:
        raise SystemExit(f"No face groups found in {src}; refusing to emit placeholder model")
    data = {"credit":"Generated from OBJ group bounds; cuboid approximation, not lossless mesh.",
            "textures":{"all":texture,"particle":texture}, "elements":elements}
    out = pathlib.Path(dst)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2)+"\n", encoding="utf-8")
    print(f"{dst}: {len(elements)} cuboid elements; source bounds {dims}")
if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("Usage: obj_bounds_to_block_json.py input.obj output.json namespace:block/texture")
    convert(*sys.argv[1:])
