# 05 · Pipeline Blender → GLB → Roblox Studio

## 1. Préparer la scène (une fois par fichier .blend)

Blender > *Scripting* > ouvrir `tools/blender/cr_01_scene_setup.py` > **Run Script**.
(Si le script n'est pas ouvert depuis le repo, renseigner `REPO_DIR` en haut du fichier.)

Résultat :
- Unités : *Unit System = None*, rotations en degrés → **1 unité Blender = 1 stud**.
- Collection `REF_CoffeeRush` : mannequin R15 (échelle verrouillée, exclu du rendu et de l'export) + repères de hauteur `GUIDE_…`.
- Les matériaux officiels, avec leurs textures si elles sont dans `materials/`.

## 2. Créer l'asset

Renseigner `CATEGORY`, `NAME`, `VERSION`, `PIVOT` dans `cr_02_new_asset.py` puis Run Script.
Un Empty `<Nom>_ROOT` est créé à l'origine. **Tous les composants sont ses enfants.**

Conventions (§5, §6) :
- Z en haut, X = largeur, Y = profondeur, **face avant vers −Y** (vue de face Blender = pavé num. 1).
- Pivot `SOL_CENTRE` : la base de l'asset à Z = 0, centrée sur l'origine. `LIBRE` pour un module ou un objet mural (pivot au point d'accroche, identique pour toute la famille).
- Composants nommés en anglais, simples : `Body`, `FrontPanel`, `DripTray`, `Buttons`, `Display`, `Portafilter`, `Feet`, `Details`.
- Appliquer l'échelle (Ctrl+A > Scale) ; jamais d'échelle négative.
- Bevels discrets sur les arêtes importantes, pas de subdivision inutile, normales vérifiées (overlay *Face Orientation*).

## 3. Contrôler et exporter

Sélectionner le ROOT > `cr_03_check_and_export.py` > Run Script.

| Contrôle | Bloquant |
|---|---|
| ROOT à l'origine, sans rotation ni échelle | oui |
| Noms en lettres/chiffres/_ , pas de `.001` | oui |
| Échelle négative | oui |
| > 20 000 triangles sur un composant | oui |
| Matériau texturé sans UV | oui |
| Caméra ou lumière dans l'asset | oui |
| Pivot SOL_CENTRE : base pas à Z = 0 | oui |
| Échelle non appliquée, > 5 000 triangles, matériau hors bibliothèque, slot vide, asset décentré | avertissement |

Livraison dans `assets/<Catégorie>/CR_<Catégorie>_<Nom>/` : GLB (textures intégrées), `textures/` (copies), `fiche_technique.json` + `.md`, `preview.png`.

## 4. Importer dans Studio

*Fichier > Importer 3D* (Import 3D), choisir le GLB :
- **File Geometry > Scale Unit = Stud** ← indispensable.
- File Transform > World Forward = Front, World Up = Top.
- Upload to Roblox : activé. Insert Using Scene Position : selon besoin.
Puis : Anchored, CollisionFidelity, CastShadow selon [doc 03](03_ROBLOX_TECHNIQUE.md), et conversion en paquet si l'asset est réutilisé.

## ⚠️ Orientation à vérifier une fois (test à faire)

L'exporteur glTF de Blender convertit automatiquement les axes : **−Y Blender devient +Z dans le GLB** (vérifié sur un export de test).
Or dans Roblox la face avant d'une pièce (LookVector) est **−Z**, et les bâtiments de la ville sont orientés façade vers −Z.
Si l'importeur Roblox ne retourne pas l'objet, nos assets arriveraient donc **dos** à la convention Roblox.

Test : exporter un cube avec un petit marqueur sur sa face −Y, l'importer avec les réglages ci-dessus, comparer au `LookVector` de la MeshPart.
Selon le résultat, on fige une des deux règles :
- l'importeur gère déjà → rien à changer ;
- sinon → tourner le ROOT de 180° autour de Z à l'export (option à ajouter au script) ou accepter une rotation de 180° à la pose dans Studio.
