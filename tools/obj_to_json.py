#!/usr/bin/env python3
"""Convert Wavefront OBJ geometry to a loss-minimizing JSON mesh representation.
This is generic mesh JSON, not Minecraft's vanilla block-model JSON format.
"""
import json, pathlib, re, sys

def convert(src):
    vertices, texcoords, normals, objects, materials = [], [], [], [], []
    current = {"name": pathlib.Path(src).stem, "faces": []}
    mtllib = []
    for raw in pathlib.Path(src).read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        tag, vals = parts[0], parts[1:]
        if tag == "v" and len(vals) >= 3:
            vertices.append([float(x) for x in vals[:3]])
        elif tag == "vt" and len(vals) >= 2:
            texcoords.append([float(x) for x in vals[:2]])
        elif tag == "vn" and len(vals) >= 3:
            normals.append([float(x) for x in vals[:3]])
        elif tag == "mtllib":
            mtllib.extend(vals)
        elif tag in ("o", "g"):
            name = " ".join(vals).strip()
            if current["faces"]:
                objects.append(current)
            if name:
                current = {"name": name, "faces": []}
        elif tag == "usemtl":
            materials.append(" ".join(vals))
        elif tag == "f" and len(vals) >= 3:
            face = []
            for v in vals:
                fields = v.split("/")
                def idx(s, size):
                    if not s: return None
                    n = int(s)
                    return n - 1 if n > 0 else size + n
                face.append({
                    "vertex": idx(fields[0], len(vertices)),
                    "uv": idx(fields[1], len(texcoords)) if len(fields) > 1 else None,
                    "normal": idx(fields[2], len(normals)) if len(fields) > 2 else None
                })
            # Keep original polygon topology; consumers can triangulate as needed.
            current["faces"].append(face)
    if current["faces"]:
        objects.append(current)
    return {
        "format": "obj-to-json-mesh-v1",
        "source": pathlib.Path(src).name,
        "coordinate_system": "Wavefront OBJ coordinates; units as authored",
        "vertices": vertices,
        "texture_coordinates": texcoords,
        "normals": normals,
        "objects": objects,
        "material_libraries": mtllib,
        "material_names_seen": list(dict.fromkeys(materials)),
        "notes": [
            "Geometry and polygon faces are preserved in this generic JSON representation.",
            "MTL and image textures are referenced by name only; copy their source files separately.",
            "This is not directly loadable as a Minecraft 1.20.1 block model JSON. Minecraft's vanilla model format supports cuboid elements, not arbitrary OBJ polygon meshes."
        ]
    }

def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: obj_to_json.py input.obj output.json")
    data = convert(sys.argv[1])
    pathlib.Path(sys.argv[2]).write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {sys.argv[2]}: {len(data['vertices'])} vertices, {sum(len(o['faces']) for o in data['objects'])} faces")
if __name__ == "__main__":
    main()
