# T-054 — Sonde légère et observations structurées

- **Statut** : done (2026-07-16)
- **Priorité** : P1
- **Effort** : élevé
- **Outil recommandé** : Les deux
- **Dépendances** : T-020, T-053

## Objectif

Ouvrir une page dans un onglet Zendriver dédié, extraire un état léger et
enregistrer une observation structurée sans générer systématiquement une
archive visuelle ou MHTML.

## Contexte

Les archives complètes existantes sont adaptées aux preuves, mais trop lourdes
pour une vérification périodique. La sonde doit collecter un texte normalisé,
des métadonnées, des métriques et un diagnostic d'extraction.

## Fichiers concernés

- nouveau module de sonde sous `investigations/`
- `browser/service.py`
- `investigations/migrations.py`
- `investigations/models.py`
- `investigations/repository.py`
- `investigations/service.py`
- tests unitaires et FakeTab

## Étapes

1. Ajouter `page_monitor_observations`.
2. Définir le schéma JSON versionné des métadonnées et métriques.
3. Implémenter l'extracteur `generic_page`.
4. Exécuter les sélecteurs personnalisés de façon bornée.
5. Comparer nombres, textes, listes et états avec l'observation précédente.
6. Marquer explicitement `missing`, `unavailable` ou `error`, jamais zéro.
7. Retourner un déclencheur d'archive lorsque le changement est significatif.

## Critères d'acceptation

- Une sonde réussie n'écrit ni PNG, ni MHTML.
- Les valeurs absentes sont distinguées des valeurs numériques nulles.
- Chaque observation porte URL finale, horodatage, durée, hash, données et
  erreurs d'extraction.
- Une page dynamique peut produire une observation partielle exploitable.
- Le texte utilise la normalisation déjà employée par les archives.

## Commandes de test

```powershell
.venv\Scripts\python.exe -m unittest tests.test_monitoring tests.test_browser_service tests.test_investigations
git diff --check
```

## Risques

- Les pages nécessitant authentification, consentement ou challenge doivent
  rester en erreur explicite.
- Les sélecteurs CSS tiers sont fragiles et ne constituent pas un contrat de
  plateforme.

## Résultat

La migration v19 ajoute les observations versionnées. `PageMonitorProbe` ouvre
un onglet dédié, attend que Zendriver ait quitté `about:blank`, exécute une
seule extraction composite bornée, normalise le texte avec le pipeline des
archives et ferme l'onglet. Les métriques texte, nombre, liste et état sont
comparées à la précédente observation ; un changement significatif expose
`archive_recommended`. Les valeurs absentes, indisponibles et en erreur restent
explicites. Un smoke Brave headless sur `https://example.com/` a produit une
observation partielle valide en 389 ms sans artefact lourd.
