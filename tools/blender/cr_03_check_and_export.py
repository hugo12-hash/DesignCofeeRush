"""Coffee Rush — 03 · Contrôler puis exporter un asset en GLB.

Sélectionne le <Nom>_ROOT (créé par cr_02_new_asset.py) puis Run Script.

Contrôles (règles §4 à §10) :
  - ROOT à l'origine, sans rotation ni échelle ;
  - noms simples en anglais, pas de « .001 » ;
  - transformations appliquées (échelle 1, pas d'échelle négative) ;
  - triangles par MeshPart ≤ 20 000 (limite Roblox) ;
  - matériaux de la bibliothèque officielle uniquement, UV présentes si texture ;
  - pas de caméra ni de lumière dans l'asset ;
  - pivot au centre de la base, au sol (si cr_pivot = SOL_CENTRE).

Livraison dans assets/<Catégorie>/CR_<Catégorie>_<Nom>/ :
  CR_<Catégorie>_<Nom>_V01.glb, textures/ (copie des textures), fiche_technique.json + .md,
  preview.png (si le rendu est possible).
Les erreurs bloquent l'export (sauf FORCE_EXPORT = True) ; les avertissements non.
"""
import datetime
import json
import os
import re
import shutil
from pathlib import Path

import bpy
from mathutils import Vector

REPO_DIR = r""
FORCE_EXPORT = False
RENDER_PREVIEW = True
TRI_LIMIT = 20000          # limite Roblox par MeshPart
TRI_WARN = 5000            # au-delà : vérifier que la complexité est justifiée (§10)
TOL = 0.01                 # tolérance en studs


def find_repo():
    candidates = []
    if REPO_DIR:
        candidates.append(Path(REPO_DIR))
    if os.environ.get("CR_DESIGN_REPO"):
        candidates.append(Path(os.environ["CR_DESIGN_REPO"]))
    try:
        candidates.append(Path(__file__).resolve().parents[2])
    except (NameError, IndexError):
        pass
    for text in bpy.data.texts:
        if text.filepath:
            candidates.extend(Path(bpy.path.abspath(text.filepath)).resolve().parents)
    if bpy.data.filepath:
        candidates.extend(Path(bpy.data.filepath).resolve().parents)
    for c in candidates:
        if (c / "materials" / "materials.json").exists():
            return c
    raise RuntimeError("Repo DesignCofeeRush introuvable : renseigne REPO_DIR en haut du script.")


def descendants(obj):
    out = []
    for c in obj.children:
        out.append(c)
        out.extend(descendants(c))
    return out


def get_root():
    obj = bpy.context.active_object
    while obj is not None and not obj.name.endswith("_ROOT"):
        obj = obj.parent
    if obj is None:
        roots = [o for o in bpy.data.objects if o.name.endswith("_ROOT") and o.parent is None]
        if len(roots) == 1:
            obj = roots[0]
    if obj is None:
        raise RuntimeError("Sélectionne l'objet <Nom>_ROOT de l'asset (ou un de ses enfants).")
    return obj


def triangles(obj, depsgraph):
    ev = obj.evaluated_get(depsgraph)
    me = ev.to_mesh()
    try:
        tris = sum(len(p.vertices) - 2 for p in me.polygons)
        verts = [ev.matrix_world @ v.co for v in me.vertices]
        has_uv = len(me.uv_layers) > 0
    finally:
        ev.to_mesh_clear()
    return tris, verts, has_uv


def check(root, repo):
    errors, warnings = [], []
    lib = json.loads((repo / "materials" / "materials.json").read_text(encoding="utf-8"))
    official = {m["id"] for m in lib["materiaux"]}

    for key in ("cr_category", "cr_name", "cr_version"):
        if key not in root:
            errors.append(f"Propriété {key} absente du ROOT : crée l'asset avec cr_02_new_asset.py.")
    if root.location.length > TOL:
        errors.append(f"Le ROOT doit être à l'origine (actuellement {tuple(round(v, 3) for v in root.location)}).")
    if any(abs(a) > 1e-4 for a in root.rotation_euler) or any(abs(s - 1) > 1e-4 for s in root.scale):
        errors.append("Le ROOT ne doit avoir ni rotation ni échelle.")

    depsgraph = bpy.context.evaluated_depsgraph_get()
    inv = root.matrix_world.inverted()
    parts, all_pts, mats_used, images = [], [], set(), set()
    for o in descendants(root):
        if o.type in ("CAMERA", "LIGHT"):
            errors.append(f"{o.name} : pas de caméra ni de lumière dans un asset.")
            continue
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", o.name):
            errors.append(f"Nom « {o.name} » : lettres/chiffres/_ uniquement, en anglais, sans « .001 ».")
        if o.type != "MESH":
            continue
        if any(s < 0 for s in o.scale):
            errors.append(f"{o.name} : échelle négative (faces inversées dans Roblox). Applique l'échelle.")
        elif any(abs(s - 1) > 1e-4 for s in o.scale):
            warnings.append(f"{o.name} : échelle non appliquée {tuple(round(s, 3) for s in o.scale)} (Ctrl+A > Scale).")
        tris, verts, has_uv = triangles(o, depsgraph)
        if tris > TRI_LIMIT:
            errors.append(f"{o.name} : {tris} triangles > {TRI_LIMIT} (limite Roblox par MeshPart).")
        elif tris > TRI_WARN:
            warnings.append(f"{o.name} : {tris} triangles — justifié par sa taille / sa proximité caméra ?")
        all_pts.extend(inv @ v for v in verts)
        slot_mats = [s.material for s in o.material_slots]
        if not slot_mats or any(m is None for m in slot_mats):
            warnings.append(f"{o.name} : emplacement de matériau vide.")
        textured = False
        for m in filter(None, slot_mats):
            mats_used.add(m.name)
            if m.name not in official:
                warnings.append(f"{o.name} : matériau « {m.name} » hors bibliothèque officielle (§7 : à proposer avant usage).")
            if getattr(m, "node_tree", None):
                for n in m.node_tree.nodes:
                    if n.type == "TEX_IMAGE" and n.image:
                        textured = True
                        images.add(n.image)
        if textured and not has_uv:
            errors.append(f"{o.name} : matériau texturé mais aucune UV.")
        parts.append({"nom": o.name, "parent": o.parent.name if o.parent else None, "triangles": tris,
                      "materiaux": [m.name for m in slot_mats if m]})

    if not parts:
        errors.append("Aucun mesh enfant du ROOT.")
        return errors, warnings, parts, None, mats_used, images

    mn = Vector((min(p.x for p in all_pts), min(p.y for p in all_pts), min(p.z for p in all_pts)))
    mx = Vector((max(p.x for p in all_pts), max(p.y for p in all_pts), max(p.z for p in all_pts)))
    bbox = {"min": [round(v, 3) for v in mn], "max": [round(v, 3) for v in mx],
            "largeur_x": round(mx.x - mn.x, 3), "profondeur_y": round(mx.y - mn.y, 3), "hauteur_z": round(mx.z - mn.z, 3)}
    if root.get("cr_pivot", "SOL_CENTRE") == "SOL_CENTRE":
        if abs(mn.z) > TOL:
            errors.append(f"Pivot SOL_CENTRE : la base doit être à Z = 0 (actuellement {mn.z:.3f}).")
        cx, cy = (mn.x + mx.x) / 2, (mn.y + mx.y) / 2
        if abs(cx) > 0.05 or abs(cy) > 0.05:
            warnings.append(f"Pivot SOL_CENTRE : asset décentré de ({cx:.2f}, {cy:.2f}) par rapport au ROOT.")
    return errors, warnings, parts, bbox, mats_used, images


def render_preview(root, path, bbox):
    scene = bpy.context.scene
    saved = (scene.camera, scene.render.engine, scene.render.filepath, scene.render.film_transparent,
             scene.render.resolution_x, scene.render.resolution_y)
    cam_data = bpy.data.cameras.new("CR_TMP_PreviewCam")
    cam = bpy.data.objects.new("CR_TMP_PreviewCam", cam_data)
    scene.collection.objects.link(cam)
    hidden = []
    try:
        keep = {root} | set(descendants(root))
        for o in scene.objects:
            if o not in keep and o is not cam and not o.hide_render:
                o.hide_render = True
                hidden.append(o)
        size = max(bbox["largeur_x"], bbox["profondeur_y"], bbox["hauteur_z"])
        center = Vector([(a + b) / 2 for a, b in zip(bbox["min"], bbox["max"])])
        center = root.matrix_world @ center
        cam_data.type = "ORTHO"
        cam_data.ortho_scale = size * 1.6
        direction = Vector((0.75, -1.0, 0.6)).normalized()  # 3/4 avant (face avant vers -Y)
        cam.location = center + direction * size * 4
        cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
        cam_data.clip_end = size * 20
        scene.camera = cam
        scene.render.engine = "BLENDER_WORKBENCH"
        scene.display.shading.light = "STUDIO"
        scene.display.shading.color_type = "MATERIAL"
        scene.render.film_transparent = True
        scene.render.resolution_x = scene.render.resolution_y = 1024
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        return True
    except Exception as exc:  # rendu impossible (ex. pas de GPU) : on n'arrête pas l'export
        print("Aperçu non rendu :", exc)
        return False
    finally:
        for o in hidden:
            o.hide_render = False
        (scene.camera, scene.render.engine, scene.render.filepath, scene.render.film_transparent,
         scene.render.resolution_x, scene.render.resolution_y) = saved
        bpy.data.objects.remove(cam, do_unlink=True)
        bpy.data.cameras.remove(cam_data)


def export(root, repo, parts, bbox, mats_used, images, warnings):
    cat, name, ver = root["cr_category"], root["cr_name"], int(root["cr_version"])
    base = f"CR_{cat}_{name}"
    folder = repo / "assets" / cat / base
    (folder / "textures").mkdir(parents=True, exist_ok=True)
    glb = folder / f"{base}_V{ver:02d}.glb"

    for o in bpy.context.selected_objects:
        o.select_set(False)
    objs = [root] + descendants(root)
    hidden_state = {}
    for o in objs:
        if o.type == "MESH" and o.data.users == 1:
            o.data.name = o.name  # noms de mesh = noms des composants dans le GLB
        hidden_state[o] = o.hide_get()
        o.hide_set(False)
        o.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB", use_selection=True,
                              export_yup=True, export_apply=True, export_cameras=False,
                              export_lights=False, export_extras=False)
    for o, h in hidden_state.items():
        o.hide_set(h)

    tex_files = []
    for img in images:
        src = Path(bpy.path.abspath(img.filepath)) if img.filepath else None
        if src and src.exists():
            shutil.copy2(src, folder / "textures" / src.name)
            tex_files.append(src.name)
    preview = folder / "preview.png"
    has_preview = render_preview(root, preview, bbox) if RENDER_PREVIEW else False

    sheet = {
        "fichier": glb.name, "categorie": cat, "nom": name, "version": f"V{ver:02d}",
        "date_export": datetime.date.today().isoformat(), "unite": "stud (1 unité Blender = 1 stud)",
        "axes_blender": "Z haut, X largeur, Y profondeur, face avant vers -Y",
        "dimensions_studs": {"largeur_x": bbox["largeur_x"], "profondeur_y": bbox["profondeur_y"], "hauteur_z": bbox["hauteur_z"]},
        "encombrement_total": {"min": bbox["min"], "max": bbox["max"]},
        "pivot": root.get("cr_pivot", "SOL_CENTRE"),
        "nombre_de_meshparts": len(parts), "triangles_total": sum(p["triangles"] for p in parts),
        "composants": parts, "materiaux": sorted(mats_used), "textures": sorted(tex_files),
        "apercu": "preview.png" if has_preview else None, "avertissements": warnings,
    }
    (folder / "fiche_technique.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False), encoding="utf-8")
    md = [f"# {base} — fiche technique", "",
          f"- Fichier : `{glb.name}` · exporté le {sheet['date_export']}",
          f"- Dimensions (studs) : **L {bbox['largeur_x']} × P {bbox['profondeur_y']} × H {bbox['hauteur_z']}**",
          f"- Encombrement total : min {bbox['min']} · max {bbox['max']}",
          f"- Pivot : {sheet['pivot']} (origine du ROOT)",
          f"- MeshParts : {len(parts)} · triangles : {sheet['triangles_total']}",
          f"- Matériaux : {', '.join(sheet['materiaux']) or '—'}",
          f"- Textures : {', '.join(sheet['textures']) or 'aucune (intégrées au GLB si présentes)'}", "",
          "| Composant | Parent | Triangles | Matériaux |", "|---|---|---|---|"]
    md += [f"| {p['nom']} | {p['parent']} | {p['triangles']} | {', '.join(p['materiaux'])} |" for p in parts]
    if warnings:
        md += ["", "## Avertissements", ""] + [f"- {w}" for w in warnings]
    if has_preview:
        md += ["", "![aperçu](preview.png)"]
    (folder / "fiche_technique.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return glb


def main():
    repo = find_repo()
    root = get_root()
    errors, warnings, parts, bbox, mats_used, images = check(root, repo)
    print(f"\n=== Coffee Rush · contrôle de {root.name} ===")
    if bbox:
        print(f"Dimensions : L {bbox['largeur_x']} × P {bbox['profondeur_y']} × H {bbox['hauteur_z']} studs · "
              f"{len(parts)} MeshParts · {sum(p['triangles'] for p in parts)} triangles")
    for e in errors:
        print("  ERREUR  ", e)
    for w in warnings:
        print("  ATTENTION", w)
    if errors and not FORCE_EXPORT:
        print("Export annulé : corrige les erreurs (ou FORCE_EXPORT = True).")
        return
    glb = export(root, repo, parts, bbox, mats_used, images, warnings)
    print("Exporté :", glb)


if __name__ == "__main__":
    main()
