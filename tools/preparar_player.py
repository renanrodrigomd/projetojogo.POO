"""Fatia Jogadorspriteandandodireita.png em quadros individuais (12)."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

src, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
arr = np.array(Image.open(src).convert("RGBA"))
solid = arr[:, :, 3] > 128
lab, n = ndimage.label(solid)
areas = ndimage.sum(solid, lab, range(1, n + 1))
figs = [i + 1 for i, a in enumerate(areas) if a > 3000]
figs.sort(key=lambda i: np.where(lab == i)[1].mean())
# cada pixel visível pertence à figura sólida mais próxima
keep_lab = np.where(np.isin(lab, figs), lab, 0)
_, (iy, ix) = ndimage.distance_transform_edt(keep_lab == 0, return_indices=True)
owner = keep_lab[iy, ix]
visible = arr[:, :, 3] > 0
frames = []
for f in figs:
    c = arr.copy()
    c[~((owner == f) & visible)] = 0
    frames.append(c)
ys = [np.where(f[:, :, 3] > 0)[0] for f in frames]
top = min(y.min() for y in ys); bot = max(y.max() for y in ys) + 1
# ancora no centro de massa do corpo (estável) para o personagem não "tremer"
cxs = [np.where(f[:, :, 3] > 0)[1].mean() for f in frames]
half = 110
for k, (f, cx) in enumerate(zip(frames, cxs)):
    x0 = int(round(cx)) - half
    canvas = np.zeros((bot - top, 2 * half, 4), np.uint8)
    for xx in range(2 * half):
        sx = x0 + xx
        if 0 <= sx < f.shape[1]:
            canvas[:, xx] = f[top:bot, sx]
    assert canvas[:, 0, 3].max() == 0 and canvas[:, -1, 3].max() == 0, k
    Image.fromarray(canvas).save(out / f"andando_{k:02d}.png")
print(len(frames), canvas.shape)
