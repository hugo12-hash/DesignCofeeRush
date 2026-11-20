# 04 · Matériaux et textures

La liste des 10 matériaux officiels (§7 des règles) est dans [`materials/materials.json`](../materials/materials.json).
Chaque matériau a son dossier `materials/<ID>/` où déposer ses textures.

| ID | Couleur de base | Type | Cartes attendues | État |
|---|---|---|---|---|
| WOOD_OAK_LIGHT | Bois clair #D6B58C | répétable | Color, Roughness, Normal | textures à fournir |
| WOOD_OAK_RIBBED | Bois clair #D6B58C | répétable (lames verticales) | Color, Roughness, Normal | textures à fournir |
| TILE_FOREST_GREEN | Vert forêt #355B49 | répétable | Color, Roughness, Normal | textures à fournir |
| MARBLE_CREAM | Crème #F2EBDD | répétable | Color, Roughness | textures à fournir |
| FLOOR_BEIGE_STONE | Beige chaud #C5AD91 | répétable | Color, Roughness, Normal | textures à fournir |
| SAGE_PAINT | Vert sauge #A3B39B | répétable | Color, Roughness | textures à fournir |
| FABRIC_WARM_BEIGE | Beige chaud #C5AD91 | répétable | Color, Normal | textures à fournir |
| METAL_MATTE_BLACK | Métal noir #303331 | uni | — | couleur unie |
| CERAMIC_OFF_WHITE | Blanc cassé #F7F4EC | uni | — | couleur unie |
| GLASS_CLEAR | Blanc cassé #F7F4EC, transparent | uni | — | couleur unie |

Roughness, metallic et taille de répétition dans le JSON = **propositions** à valider.

## Déposer une texture

1. Nommer le fichier `<ID>_<Carte>.png`, carte ∈ `Color`, `Roughness`, `Normal`, `Metalness`.
   Ex. `materials/WOOD_OAK_LIGHT/WOOD_OAK_LIGHT_Color.png`.
2. PNG, carré, puissance de 2, **1024 px maximum** (limite Roblox). 512 suffit souvent pour un style low-poly.
3. Normal map au format OpenGL (Y+), celui de Blender et de Roblox.
4. Pas de Metalness pour un matériau non métallique.
5. Relancer `cr_01_scene_setup.py` : les textures présentes sont branchées automatiquement sur le matériau Blender.

## Règles (rappel §7 et §8)

- Ne pas inventer de matériau par asset. Un nouveau besoin → proposer un ID, une description, une couleur de la palette, et attendre la validation avant de l'ajouter à `materials.json`.
- Répétables : sans couture, motif discret, échelle cohérente (même nombre de studs par répétition sur tous les assets).
- Assets spécifiques : UV propres, textures orientées, résolution proportionnée à la taille à l'écran.
- Dans Roblox : un **MaterialVariant** (MaterialService, `StudsPerTile`) pour les grandes surfaces répétées, un **SurfaceAppearance** (paquet partagé) pour les MeshParts avec UV dédiées.
