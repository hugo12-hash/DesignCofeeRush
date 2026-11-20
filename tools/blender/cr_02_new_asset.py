"""Coffee Rush — 02 · Démarrer un nouvel asset.

Crée l'objet racine <Nom>_ROOT (un Empty) à l'origine, au niveau du sol,
avec les informations utilisées à l'export (catégorie, nom, version, type de pivot).
Tous les composants de l'asset (Body, FrontPanel, Feet…) doivent être enfants de ce ROOT.

Utilisation : renseigne les 4 valeurs ci-dessous puis Run Script.
"""
import re

import bpy

CATEGORY = "Kitchen"          # Kitchen, Furniture, Building, Decor, Prop…
NAME = "EspressoMachine"      # PascalCase, en anglais, sans espace
VERSION = 1                   # V01
PIVOT = "SOL_CENTRE"          # SOL_CENTRE (meuble posé au sol / sur un plan) ou LIBRE (module, objet mural…)

COLLECTION = "ASSET"


def main():
    for label, value in (("CATEGORY", CATEGORY), ("NAME", NAME)):
        if not re.fullmatch(r"[A-Z][A-Za-z0-9]*", value):
            raise ValueError(f"{label} doit être en PascalCase anglais sans espace (reçu : {value!r})")
    root_name = f"{NAME}_ROOT"
    if bpy.data.objects.get(root_name):
        raise ValueError(f"{root_name} existe déjà dans la scène.")
    col = bpy.data.collections.get(COLLECTION) or bpy.data.collections.new(COLLECTION)
    if col.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(col)
    root = bpy.data.objects.new(root_name, None)
    root.empty_display_type = "ARROWS"
    root.empty_display_size = 1.0
    root["cr_category"] = CATEGORY
    root["cr_name"] = NAME
    root["cr_version"] = VERSION
    root["cr_pivot"] = PIVOT
    col.objects.link(root)
    for o in bpy.context.selected_objects:
        o.select_set(False)
    root.select_set(True)
    bpy.context.view_layer.objects.active = root
    print(f"{root_name} créé → export prévu : CR_{CATEGORY}_{NAME}_V{VERSION:02d}.glb")
    print("Rappel : face avant vers -Y, Z vers le haut, 1 unité = 1 stud.")


if __name__ == "__main__":
    main()
