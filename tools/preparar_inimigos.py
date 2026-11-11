"""Gera assets/enemys/frames/<conjunto>/NN.png a partir das folhas de sprites.

Uso: python preparar_inimigos.py <pasta assets/enemys>
- Folhas com alfa: cada figura = componente conexo sólido (alfa > 128).
- Folhas RGB com "xadrez" falso de fundo: o fundo cinza/branco ligado às
  bordas é removido por flood-fill.
Todos os quadros de um conjunto saem com o mesmo tamanho de tela e com os
pés alinhados, para a animação não tremer.
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

MAX_ALTURA = 420
base = Path(sys.argv[1])
saida = base / "frames"


def remover_fundo_xadrez(rgb):
    """Transparente tudo que é cinza-claro neutro e conectado à borda."""
    a = rgb.astype(int)
    neutro = (a.max(2) - a.min(2) <= 6) & (a.min(2) >= 185)
    lab, n = ndimage.label(neutro)
    borda = set(np.unique(np.concatenate(
        [lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    fundo = np.isin(lab, list(borda))
    # fundos "ilhados" (entre pernas etc.): neutros grandes não ligados à borda
    for i in range(1, n + 1):
        if i not in borda and (lab == i).sum() > 400:
            fundo |= lab == i
    out = np.dstack([rgb, np.where(fundo, 0, 255).astype(np.uint8)])
    # suaviza a borda: 1px de erosão do alfa elimina o halo claro
    solid = ndimage.binary_erosion(out[:, :, 3] > 0, iterations=1)
    out[:, :, 3] = np.where(solid, 255, 0)
    return out


def figuras(arr, area_min, linhas=None):
    solid = arr[:, :, 3] > 128
    lab, n = ndimage.label(solid)
    areas = ndimage.sum(solid, lab, range(1, n + 1))
    ids = [i + 1 for i, a in enumerate(areas) if a > area_min]
    cent = {i: np.argwhere(lab == i).mean(0) for i in ids}
    ys = sorted(cent[i][0] for i in ids)
    # agrupa por linha: salto grande em y começa nova linha
    ordem, linha = [], []
    for i in sorted(ids, key=lambda i: cent[i][0]):
        if linha and cent[i][0] - cent[linha[-1]][0] > arr.shape[0] / 8:
            ordem += sorted(linha, key=lambda j: cent[j][1]); linha = []
        linha.append(i)
    ordem += sorted(linha, key=lambda j: cent[j][1])
    keep = np.where(np.isin(lab, ids), lab, 0)
    dist, (iy, ix) = ndimage.distance_transform_edt(keep == 0, return_indices=True)
    dono = np.where(dist <= 14, keep[iy, ix], 0)  # ignora poeira longe da figura
    vis = arr[:, :, 3] > 0
    res = []
    for i in ordem:
        c = arr.copy(); c[~((dono == i) & vis)] = 0; res.append(c)
    return res


def salvar(nome, quadros, base_fixa=True):
    pasta = saida / nome; pasta.mkdir(parents=True, exist_ok=True)
    for f in pasta.glob("*.png"): f.unlink()
    caixas = []
    for q in quadros:
        ys, xs = np.where(q[:, :, 3] > 0)
        caixas.append((ys.min(), ys.max() + 1, xs.min(), xs.max() + 1,
                       xs.mean()))
    alt = max(c[1] - c[0] for c in caixas)
    meia = int(max(max(c[4] - c[2], c[3] - c[4]) for c in caixas)) + 2
    esc = min(1.0, MAX_ALTURA / alt)
    for k, (q, c) in enumerate(zip(quadros, caixas)):
        tela = np.zeros((alt, 2 * meia, 4), np.uint8)
        y1 = c[1]; y0 = y1 - alt
        x0 = int(round(c[4])) - meia
        for xx in range(2 * meia):
            sx = x0 + xx
            if 0 <= sx < q.shape[1]:
                col = q[max(y0, 0):y1, sx]
                tela[alt - col.shape[0]:, xx] = col
        img = Image.fromarray(tela)
        if esc < 1:  # folhas enormes: reduz uma vez aqui, não a cada partida
            img = img.resize((round(img.width * esc), round(img.height * esc)),
                             Image.LANCZOS)
        img.save(pasta / f"{k:02d}.png", optimize=True)
    print(nome, len(quadros), (alt, 2 * meia))


def carregar(nome, bg=False):
    im = Image.open(base / nome)
    if bg:
        return remover_fundo_xadrez(np.array(im.convert("RGB")))
    return np.array(im.convert("RGBA"))

# --- Robô terrestre (as folhas "andando" olham para o lado oposto ao nome) ---
salvar("terrestre_andando_esq", figuras(carregar("Roboandandodireita.png"), 5000))
salvar("terrestre_andando_dir", figuras(carregar("Roboandandoesquerda.png"), 5000))
salvar("terrestre_parado_esq", figuras(carregar("Rob#U00f4terrestreesquerda.png", True), 20000))
salvar("terrestre_parado_dir", figuras(carregar("Roboterrestredireita.png", True), 20000))
# --- Drone ---
salvar("drone_dir", figuras(carregar("dronedireita.png", True), 3000))
salvar("drone_esq", figuras(carregar("droneesquerda.png", True), 3000))
# --- Blindado (tank.png olha para a esquerda) ---
salvar("blindado_esq", figuras(carregar("tank.png"), 300))
# --- Explosivo ---
salvar("explosivo", figuras(carregar("robo.png"), 300))
