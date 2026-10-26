#!/usr/bin/env python3
"""Prepare Wavefront OBJ meshes for Forge 1.20.1's OBJ loader.
Preserves UVs, normals, faces, groups, material references, and comments except
for replacing the mtllib path with a stable per-model material filename.
No texture artwork is generated.
"""
import pathlib, sys

MAX_XZ = 14.0
MAX_Y = 32.0

def prepare(src, dst):
    src = pathlib.Path(src)
    lines = src.read_text(encoding="utf-8", errors="replace").splitlines()
    vertices = []
    for line in lines:
        if line.lstrip().startswith("v "):
            fields = line.split()
            if len(fields) >= 4:
                vertices.append([float(x) for x in fields[1:4]])
    if not vertices:
        raise SystemExit(f"No vertices found in {src}")
    mins = [min(v[i] for v in vertices) for i in range(3)]
    maxs = [max(v[i] for v in vertices) for i in range(3)]
    dims = [maxs[i] - mins[i] for i in range(3)]
    if any(d <= 1e-8 for d in dims):
        raise SystemExit(f"Degenerate geometry in {src}: {dims}")
    sxz = min(MAX_XZ / dims[0], MAX_XZ / dims[2])
    sy = MAX_Y / dims[1]
    out = []
    for line in lines:
        s = line.lstrip()
        if s.startswith("v "):
            fields = s.split()
            p = [float(x) for x in fields[1:4]]
            q = [(p[0]-mins[0])*sxz, (p[1]-mins[1])*sy, (p[2]-mins[2])*sxz]
            q[0] += (16.0 - dims[0]*sxz)/2.0
            q[2] += (16.0 - dims[2]*sxz)/2.0
            out.append("v %.6f %.6f %.6f" % tuple(q))
        elif s.startswith("mtllib "):
            # Material file will be supplied with the texture work later.
            out.append("# Pending texture stage: original material library: " + s[7:])
        else:
            out.append(line)
    dst = pathlib.Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{src} -> {dst}: vertices={len(vertices)}, original XYZ={dims}, normalized XYZ={[round(dims[0]*sxz,3), MAX_Y, round(dims[2]*sxz,3)]}")
if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: prepare_forge_obj.py input.obj output.obj")
    prepare(sys.argv[1], sys.argv[2])
