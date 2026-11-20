"""Coffee Rush — 01 · Préparer une scène Blender de modélisation.

Ce que fait le script (sans rien supprimer de la scène) :
  1. Unités : 1 unité Blender = 1 stud Roblox (Unit System = None, rotations en degrés),
     comme le recommande la doc Roblox « Blender ».
  2. Importe le mannequin R15 de référence dans la collection REF_CoffeeRush,
     pieds au sol, face avant vers -Y, non sélectionnable et exclu du rendu.
  3. Ajoute des repères de hauteur (plan de travail, hanche, coude, épaule, yeux)
     tirés de standards/ergonomie.json.
  4. Crée ou met à jour les matériaux officiels (materials/materials.json).
     Si des textures existent dans materials/<ID>/, elles sont branchées automatiquement.

Utilisation : Blender > onglet Scripting > ouvrir ce fichier > Run Script.
Le script peut être relancé : il met à jour au lieu de dupliquer.
"""
import json
import os
from pathlib import Path

import bpy

# Chemin du repo DesignCofeeRush sur ton PC. Laisse vide si le script est ouvert
# directement depuis le dossier tools/blender du repo.
REPO_DIR = r""

REF_COLLECTION = "REF_CoffeeRush"
MANNEQUIN_NAME = "REF_R15_Mannequin"


# --------------------------------------------------------------------------- utils
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
            p = Path(bpy.path.abspath(text.filepath)).resolve()
            candidates.extend(p.parents)
    if bpy.data.filepath:
        candidates.extend(Path(bpy.data.filepath).resolve().parents)
    for c in candidates:
        if (c / "materials" / "materials.json").exists():
            return c
    raise RuntimeError("Repo DesignCofeeRush introuvable : renseigne REPO_DIR en haut du script.")


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_to_linear_rgba(h):
    h = h.lstrip("#")
    return tuple(srgb_to_linear(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)) + (1.0,)


def ensure_collection(name, parent=None):
    col = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    parent = parent or bpy.context.scene.collection
    if col.name not in parent.children:
        parent.children.link(col)
    return col


# --------------------------------------------------------------------------- 1. unités
def setup_units():
    us = bpy.context.scene.unit_settings
    us.system = "NONE"
    us.system_rotation = "DEGREES"
    us.scale_length = 1.0
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                for space in area.spaces:
                    if space.type == "VIEW_3D":
                        space.overlay.grid_scale = 1.0
                        space.clip_end = max(space.clip_end, 2000)


# --------------------------------------------------------------------------- 2. mannequin
def import_mannequin(repo, ref_col):
    old = bpy.data.objects.get(MANNEQUIN_NAME)
    if old is not None:
        bpy.data.objects.remove(old, do_unlink=True)
    path = repo / "references" / "character" / "R15" / "CR_REF_R15_Mannequin.obj"
    before = set(bpy.data.objects)
    # Réglages d'import OBJ recommandés par Roblox : Forward Z, Up Y, Scale 1.
    # Résultat : pieds à Z = 0 et face avant du mannequin vers -Y (convention Coffee Rush).
    bpy.ops.wm.obj_import(filepath=str(path), forward_axis="Z", up_axis="Y", global_scale=1.0)
    new = [o for o in bpy.data.objects if o not in before]
    if not new:
        raise RuntimeError("Import du mannequin impossible : " + str(path))
    obj = new[0]
    obj.name = MANNEQUIN_NAME
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    ref_col.objects.link(obj)
    # Applique la rotation d'import pour que le mesh soit propre (rotation 0, échelle 1).
    with bpy.context.temp_override(selected_editable_objects=[obj], active_object=obj, object=obj):
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.location = (-4.0, 0.0, 0.0)  # à côté de l'asset, pour comparer les hauteurs (déplaçable)
    obj.lock_scale = (True, True, True)  # on peut le déplacer, jamais le redimensionner
    obj.hide_render = True
    obj.display_type = "SOLID"
    obj.color = (0.64, 0.70, 0.61, 1.0)
    obj["cr_note"] = "Référence R15 Roblox (6,87 studs). Ne jamais redimensionner."
    return obj


# --------------------------------------------------------------------------- 3. repères
def make_guides(repo, ref_col):
    erg = json.loads((repo / "standards" / "ergonomie.json").read_text(encoding="utf-8"))
    meas = json.loads((repo / "references" / "character" / "R15" / "r15_measurements.json").read_text(encoding="utf-8"))
    h = meas["hauteurs_depuis_le_sol"]
    guides = [
        ("GUIDE_PlanDeTravail", erg["plan_de_travail"]["hauteur_dessus"]),
        ("GUIDE_Hanche", meas["humanoid"]["HipHeight"]),
        ("GUIDE_Coude", h["coude"]),
        ("GUIDE_Epaule", h["epaule"]),
        ("GUIDE_Yeux", h["yeux_estime"]),
    ]
    guide_col = ensure_collection("REF_Guides", ref_col)
    for name, z in guides:
        full = f"{name}_{z:.2f}".replace(".", "_")
        for o in list(guide_col.objects):
            if o.name.startswith(name + "_"):
                bpy.data.objects.remove(o, do_unlink=True)
        mesh = bpy.data.meshes.new(full)
        s = 6.0
        mesh.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)])
        o = bpy.data.objects.new(full, mesh)
        o.location.z = z
        o.display_type = "WIRE"
        o.hide_select = True
        o.hide_render = True
        guide_col.objects.link(o)


# --------------------------------------------------------------------------- 4. matériaux
def setup_materials(repo):
    lib = json.loads((repo / "materials" / "materials.json").read_text(encoding="utf-8"))
    report = []
    for m in lib["materiaux"]:
        mat = bpy.data.materials.get(m["id"]) or bpy.data.materials.new(m["id"])
        mat.use_fake_user = True
        mat.use_nodes = True
        nt = mat.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        out.location = (400, 0)
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
        color = hex_to_linear_rgba(m["couleur_de_base"])
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = m["roughness"]
        bsdf.inputs["Metallic"].default_value = m["metallic"]
        mat.diffuse_color = color
        if "transparence" in m:
            bsdf.inputs["Alpha"].default_value = 1.0 - m["transparence"]
            if hasattr(mat, "surface_render_method"):
                mat.surface_render_method = "BLENDED"
        # textures éventuelles
        folder = repo / "materials" / m["id"]
        found = []
        y = 300
        for suffix in ("Color", "Roughness", "Metalness", "Normal"):
            f = folder / f"{m['id']}_{suffix}.png"
            if not f.exists():
                continue
            img = bpy.data.images.load(str(f), check_existing=True)
            if suffix != "Color":
                img.colorspace_settings.name = "Non-Color"
            tex = nt.nodes.new("ShaderNodeTexImage")
            tex.image = img
            tex.location = (-500, y)
            y -= 280
            if suffix == "Color":
                nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
            elif suffix == "Roughness":
                nt.links.new(tex.outputs["Color"], bsdf.inputs["Roughness"])
            elif suffix == "Metalness":
                nt.links.new(tex.outputs["Color"], bsdf.inputs["Metallic"])
            else:
                nm = nt.nodes.new("ShaderNodeNormalMap")
                nm.location = (-200, y + 280)
                nt.links.new(tex.outputs["Color"], nm.inputs["Color"])
                nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
            found.append(suffix)
        report.append(f"  {m['id']:<20} textures : {', '.join(found) if found else 'aucune (couleur unie)'}")
    return report


def main():
    repo = find_repo()
    setup_units()
    ref_col = ensure_collection(REF_COLLECTION)
    import_mannequin(repo, ref_col)
    make_guides(repo, ref_col)
    report = setup_materials(repo)
    print("\n=== Coffee Rush · scène prête ===")
    print("Repo :", repo)
    print("Mannequin R15 importé (6,87 studs, face avant -Y) + repères de hauteur.")
    print("Matériaux officiels :")
    print("\n".join(report))


if __name__ == "__main__":
    main()
