# 03 · Contraintes techniques Roblox

Synthèse (reformulée) du parcours officiel « Art environnemental » de Roblox et de la doc d'import, appliquée à Coffee Rush.
Liens en bas de page.

## Limites dures

| Sujet | Valeur | Conséquence pour Coffee Rush |
|---|---|---|
| Triangles par MeshPart | **20 000** (au-delà, Studio simplifie automatiquement et le résultat se dégrade) | Le script d'export bloque au-delà, avertit dès 5 000. |
| Taille de texture | **1024 × 1024 max** ; plus on s'en approche, plus c'est coûteux | 1024 pour les grandes surfaces répétées, 512 ou moins pour les petits objets. |
| Cartes PBR (SurfaceAppearance / MaterialVariant) | 4 : ColorMap, MetalnessMap, NormalMap, RoughnessMap, en PNG | Nos noms : `<ID>_Color/_Metalness/_Normal/_Roughness.png`. Pas de Metalness pour un matériau non métallique (§8). |
| Un matériau par triangle | Un mesh multi-matériaux = plusieurs surfaces | Séparer les composants par matériau quand c'est utile (§4, §5). |

## Modèle modulaire (murs, comptoirs, sols)

- Pivot identique pour toute une famille : coin avant-bas ou point d'accroche logique.
- Grille de placement de 5 studs dans l'exemple Roblox ; chaque module fait au moins 5 × 5 et ses grandes dimensions sont des multiples du plus petit module.
- Un gros élément = un Model avec plusieurs MeshParts nommés clairement (ex. `UpperTrim`, `LowerTrim`, `Wall`) : chacun garde son matériau, sa collision, son rendu.
- Tester les modules sous plusieurs angles : une géométrie qui se chevauche trahit un pivot incohérent.

## Props (machines, tasses, chaises…)

- Pivot logique pour la pose : à la base pour ce qui est posé, à l'arrière pour ce qui est accroché au mur.
- Juste assez de géométrie pour que la silhouette soit reconnaissable.
- Réutiliser les mêmes textures / trim sheets que les modules pour rester cohérent ; éviter les détails uniques qui se remarquent quand ils se répètent.

## Textures

- **Répétables** : sans couture en X et Y, détails répartis uniformément (un élément trop marquant révèle la répétition).
- **Trim sheet** : carrée, bandes qui se répètent sur un axe, partagée par toute une famille d'assets.
- Les MeshParts texturées ont besoin d'UV faites dans Blender.
- Un seul paquet SurfaceAppearance partagé par tous les assets qui ont la même disposition UV.

## Réglages des pièces dans Studio

| Propriété | Règle Coffee Rush |
|---|---|
| Anchored | Activé partout sauf objets physiques voulus. |
| CanCollide | Désactivé sur toute la déco que le joueur ne touche pas. |
| CanTouch | Activé seulement si un script écoute Touched. |
| CastShadow | Désactivé sur les petits détails et objets peu visibles. |
| DoubleSided | Désactivé (double le coût), sauf feuillage fin. |
| CollisionFidelity | `Box` pour les blocs simples, `Hull` quand Box déborde de la forme, jamais `PreciseConvexDecomposition` sans raison. |
| RenderFidelity | `Automatic` par défaut, `Performance` pour la végétation. |

## Performances

- Chaque mesh unique = au moins un appel de rendu. Un même objet importé deux fois = deux assets différents. → Importer **une fois**, réutiliser via des **paquets** (packages), mettre à jour le paquet plutôt que réimporter.
- Fusionner des meshes réduit les appels de rendu mais fait perdre le contrôle par pièce : à faire en fin de production seulement.
- Transparences superposées (vitres, feuillages) = surcoût important : les limiter.
- Outils : Microprofiler et Scene Analysis.

## Import dans Studio (GLB)

Réglages recommandés par Roblox pour un fichier venant de Blender :
- **File Geometry > Scale Unit = Stud** (sinon un fichier en mètres est agrandi ≈ ×3,57 — c'est probablement l'origine de l'échelle « ×3,5 » des anciens modèles).
- File Transform : World Forward = Front, World Up = Top.
- Insert Using Scene Position : activé si l'on veut garder la position Blender.
- Upload to Roblox : activé pour obtenir un id réutilisable.

## Sources

- Roblox — [Greybox your environment](https://create.roblox.com/docs/fr-fr/tutorials/curriculums/environmental-art/greybox-your-environment) · [Develop polished assets](https://create.roblox.com/docs/fr-fr/tutorials/curriculums/environmental-art/develop-polished-assets) · [Assemble an asset library](https://create.roblox.com/docs/fr-fr/tutorials/curriculums/environmental-art/assemble-an-asset-library) · [Construct your world](https://create.roblox.com/docs/fr-fr/tutorials/curriculums/environmental-art/construct-your-world) · [Optimize your experience](https://create.roblox.com/docs/fr-fr/tutorials/curriculums/environmental-art/optimize-your-experience)
- Roblox — [Blender (réglages import/export)](https://create.roblox.com/docs/en-us/art/blender) · [3D Importer](https://create.roblox.com/docs/en-us/art/modeling/3d-importer) · [Onboarding artists (limite 20 000 triangles)](https://create.roblox.com/docs/vi-vn/onboarding/artists)
