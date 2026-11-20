# 02 · Ergonomie et gameplay

> **Validé le 20/11/2026 :** taille d'avatar imposée (le mannequin R15 est la seule référence) et grille de **5 studs**.
> **Reste à valider :** les autres valeurs. Les valeurs ci-dessous sont dérivées du mannequin R15 et
> du jeu actuel. Elles sont aussi dans `standards/ergonomie.json` (lu par les scripts Blender).
> Tant que `statut` n'indique pas « validé », elles servent de repères, pas de règles.

## Hauteurs

| Élément | Valeur proposée | Pourquoi |
|---|---|---|
| Dessus de plan de travail | **3,85** | Valeur déjà utilisée dans le jeu (3,855). Entre la hanche (3,51) et le coude (4,47) : les mains « tombent » sur le plan. |
| Haut d'une machine posée sur le plan | ≤ 6,3 (≈ 2,45 au-dessus du plan) | Reste sous la hauteur des yeux : en 1re personne on voit par-dessus. |
| Zone d'interaction (poignées, boutons, portes de four) | entre 3,0 et 5,7 | Du bout des doigts à l'épaule. |
| Étagère interactive la plus haute | 5,7 | Épaule. Au-dessus = décoratif uniquement. |
| Poignée / bouton : plus petit côté visible | ≥ 0,4 | Règle « pas de poignées minuscules » ; à vérifier en vue du dessus (rush). |
| Plafond intérieur | ≥ 15 | Tête 6,87 + saut 7,2 = 14,07. Inutile si le saut est désactivé. |

## Circulation

| Élément | Valeur proposée | Pourquoi |
|---|---|---|
| Allée minimale | **10** | Recommandation Roblox : 2 joueurs se croisent. Deux mannequins = 7,55 de large. |
| Allée principale (4 joueurs) | 15 | Un joueur peut doubler deux autres. |
| Porte | 10 de large, 10 de haut minimum | Recommandation Roblox. |

## Grille des comptoirs — validée : 5 studs

- Tous les meubles de cuisine ont une largeur multiple de **5 studs** (5, 10, 15…), comme les kits modulaires recommandés par Roblox.
- Une allée de 10 = 2 cases ; deux mannequins côte à côte (7,55) y passent.
- Pivot commun à toute la famille des comptoirs (centre de la base pour un module posé au sol).
- À adapter côté jeu : les scripts actuels utilisent des cases de 4,55 et des barrières de 5,05.

## Points d'attention gameplay

- Le saut par défaut (7,2) permet de monter sur un plan de travail de 3,85. Le jeu le gère déjà (barrières invisibles, saut coupé en rush).
- Deux caméras à satisfaire : **1re personne** (hors rush) et **vue du dessus** (rush). Un asset doit être lisible dans les deux : silhouette claire vue de dessus, zones interactives visibles de face.
- Collisions : boîtes simples pour tout ce que le joueur touche, aucune collision pour la décoration (voir doc 03).
