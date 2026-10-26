#!/usr/bin/env python3
"""Voxel-surface approximation of OBJ files into paired lower/upper Minecraft block JSON models."""
import json, math, pathlib, sys

def convert(src, lower, upper, texture):
    verts=[]; faces=[]
    for raw in pathlib.Path(src).read_text(encoding="utf-8", errors="replace").splitlines():
        p=raw.strip().split()
        if not p or p[0].startswith("#"): continue
        if p[0]=="v" and len(p)>=4: verts.append(tuple(map(float,p[1:4])))
        elif p[0]=="f" and len(p)>=4:
            ids=[]
            for t in p[1:]:
                i=int(t.split("/")[0]); i=i-1 if i>0 else len(verts)+i
                if 0<=i<len(verts): ids.append(i)
            for j in range(1,len(ids)-1): faces.append((verts[ids[0]],verts[ids[j]],verts[ids[j+1]]))
    if not verts or not faces: raise SystemExit("No usable faces: "+src)
    lo=[min(v[i] for v in verts) for i in range(3)]; hi=[max(v[i] for v in verts) for i in range(3)]
    dims=[hi[i]-lo[i] for i in range(3)]
    scale=min(14/max(dims[0],1e-9),32/max(dims[1],1e-9),14/max(dims[2],1e-9))
    off=[(16-dims[0]*scale)/2,0,(16-dims[2]*scale)/2]; occ=[set(),set()]
    def put(v):
        x=(v[0]-lo[0])*scale+off[0]; y=(v[1]-lo[1])*scale; z=(v[2]-lo[2])*scale+off[2]
        if 0<=x<16 and 0<=y<32 and 0<=z<16: occ[min(1,int(y//16))].add((int(x),int(y)%16,int(z)))
    for a,b,c in faces:
        longest=max(math.dist(a,b),math.dist(b,c),math.dist(c,a))*scale
        n=max(1,min(256,math.ceil(longest*2)))
        for i in range(n+1):
            u=i/n
            for j in range(n-i+1):
                v=j/n; w=1-u-v
                put(tuple(a[q]*w+b[q]*u+c[q]*v for q in range(3)))
    def boxes(cells):
        cells=set(cells); out=[]
        while cells:
            x,y,z=min(cells); x2=x
            while (x2+1,y,z) in cells: x2+=1
            y2=y
            while all((xx,y2+1,z) in cells for xx in range(x,x2+1)): y2+=1
            z2=z
            while all((xx,yy,z2+1) in cells for xx in range(x,x2+1) for yy in range(y,y2+1)): z2+=1
            for xx in range(x,x2+1):
                for yy in range(y,y2+1):
                    for zz in range(z,z2+1): cells.discard((xx,yy,zz))
            out.append(([x,y,z],[x2+1,y2+1,z2+1]))
        return out
    for path,k in ((lower,0),(upper,1)):
        elements=[{"from":a,"to":b,"faces":{f:{"texture":"#all"} for f in ("north","south","east","west","up","down")}} for a,b in boxes(occ[k])]
        data={"credit":"OBJ surface voxel approximation; pair lower and upper models for a two-block machine.","textures":{"all":texture,"particle":texture},"elements":elements}
        pathlib.Path(path).parent.mkdir(parents=True,exist_ok=True); pathlib.Path(path).write_text(json.dumps(data,separators=(",",":"))+"\n")
        print(path, len(elements), "cuboids from",len(faces),"triangles")
if __name__=="__main__":
    if len(sys.argv)!=5: raise SystemExit("source.obj lower.json upper.json namespace:block/texture")
    convert(*sys.argv[1:])
