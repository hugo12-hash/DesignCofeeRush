"""Coffee Rush — construire les textures officielles à partir des textures sources.

Pour chaque matériau de tools/textures/sources.json :
  - Color     : texture source recalée sur la couleur de la palette (moyenne en espace Lab),
                en gardant le motif (bois, joints, veinage) ; redimensionnée si besoin.
  - Normal    : générée à partir du relief estimé (luminance), format OpenGL (Y+), sans couture.
  - Roughness : roughness de base du matériau ± variation (creux et joints plus mats).
Les sources sont copiées dans materials/<ID>/source/ pour garder une trace.

Usage :
  python tools/textures/cr_build_textures.py <dossier_des_sources>
  ex. python tools/textures/cr_build_textures.py "C:/Users/hugo1/Documents/Roblox MAP/assets/textures"
Dépendances : pip install numpy pillow scipy
"""
import json
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, sobel

REPO = Path(__file__).resolve().parents[2]


# ----------------------------------------------------------------- couleurs (sRGB <-> Lab)
def _lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _delin(c):
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.clip(c, 0, None) ** (1 / 2.4) - 0.055)


M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
WHITE = np.array([0.95047, 1.0, 1.08883])


def rgb_to_lab(rgb):
    xyz = _lin(rgb) @ M.T / WHITE
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def lab_to_rgb(lab):
    fy = (lab[..., 0] + 16) / 116
    fx, fz = fy + lab[..., 1] / 500, fy - lab[..., 2] / 200
    f = np.stack([fx, fy, fz], -1)
    xyz = np.where(f ** 3 > 0.008856, f ** 3, (f - 16 / 116) / 7.787) * WHITE
    return np.clip(_delin(xyz @ np.linalg.inv(M).T), 0, 1)


def hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)]) / 255


# ----------------------------------------------------------------- cartes
def recolor(rgb, target_hex, contrast=1.0):
    lab = rgb_to_lab(rgb)
    mean = lab.reshape(-1, 3).mean(0)
    target = rgb_to_lab(hex_rgb(target_hex)[None, None, :])[0, 0]
    out = (lab - mean) * contrast + target
    return lab_to_rgb(out)


def height_from(rgb, invert, blur):
    h = rgb_to_lab(rgb)[..., 0] / 100
    if invert:
        h = 1 - h
    h = gaussian_filter(h, blur, mode="wrap")
    h = (h - h.min()) / max(h.max() - h.min(), 1e-6)
    return h


def normal_from(h, strength):
    dx = sobel(h, axis=1, mode="wrap")
    dy = sobel(h, axis=0, mode="wrap")
    n = np.stack([-dx * strength, dy * strength, np.ones_like(h)], -1)  # OpenGL : Y vers le haut
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return (n * 0.5 + 0.5)


def save(arr, path, mode="RGB"):
    img = Image.fromarray((np.clip(arr, 0, 1) * 255).round().astype(np.uint8), mode)
    img.save(path, optimize=True)


def build(src_dir, cfg):
    lib = {m["id"]: m for m in json.loads((REPO / "materials" / "materials.json").read_text(encoding="utf-8"))["materiaux"]}
    report = []
    for mid, c in cfg["materiaux"].items():
        mat = lib[mid]
        src = Path(src_dir) / c["source"]
        img = Image.open(src).convert("RGB")
        res = min(c.get("resolution", 1024), img.width)
        if img.size != (res, res):
            img = img.resize((res, res), Image.LANCZOS)
        rgb = np.asarray(img).astype(float) / 255
        out = REPO / "materials" / mid
        (out / "source").mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, out / "source" / src.name)

        color = recolor(rgb, mat["couleur_de_base"], c.get("contraste", 1.0))
        save(color, out / f"{mid}_Color.png")
        h = height_from(rgb, c.get("relief_inverse", False), c.get("flou", 1.0))
        maps = ["Color"]
        if "Normal" in mat["cartes_attendues"]:
            save(normal_from(h, c.get("force_normal", 4.0)), out / f"{mid}_Normal.png")
            maps.append("Normal")
        if "Roughness" in mat["cartes_attendues"]:
            r = mat["roughness"] + c.get("variation_roughness", 0.1) * (0.5 - h)
            save(np.clip(r, 0.02, 1.0), out / f"{mid}_Roughness.png", "L")
            maps.append("Roughness")
        report.append(f"{mid:<20} {res}px  {', '.join(maps)}  ← {c['source']}")
    return report


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cfg = json.loads((Path(__file__).parent / "sources.json").read_text(encoding="utf-8"))
    print("\n".join(build(sys.argv[1], cfg)))


if __name__ == "__main__":
    main()
