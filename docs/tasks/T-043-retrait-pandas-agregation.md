# T-043 — Retrait de pandas de l'agrégation (optionnel)

- **Statut** : todo
- **Priorité** : P3 · **Effort** : moyen
- **Outil recommandé** : Codex
- **Dépendances** : T-015 (golden files : filet de sécurité sur les résultats)

## Objectif

Remplacer pandas par du Python pur dans le pipeline de résultats (listes de
< 200 dicts) : démarrage plus rapide (~1 s d'import), une dépendance lourde
en moins, code d'agrégation lisible.

## Contexte

pandas ne sert qu'à : `aggregate_search_results`
(`search_orchestrator.py:70-183` — concat, drop_duplicates, groupby/idxmax,
apply ligne à ligne), aux DataFrames retournés par les moteurs
(`search_engine.py:52`), et à `generate_html_report` (`utils.py:417`).
Volumes réels : dizaines à centaines de lignes. Les `apply(axis=1)` et
groupby sont du sucre coûteux à ce volume ; l'import pandas pèse sur le
démarrage de `python main.py`.

À ne faire que si la fenêtre est calme : c'est un refactor de confort, pas un
correctif.

## Fichiers concernés

- `search_orchestrator.py` : `aggregate_search_results` (retourner une
  `list[dict]` triée + un petit conteneur pour `attrs` actuels
  `query_coverage`/`search_context`).
- `search_engine.py` : `search()` retourne `list[dict]`.
- `utils.py` : `generate_html_report` consomme la liste.
- `main.py` : points de consommation de `SearchRunResult.results` (déjà des
  tuples de dicts — vérifier).
- `requirements.txt` : retirer pandas (vérifier qu'aucun autre module ne
  l'importe : grep `import pandas`).
- Tests : `test_search_orchestrator`, `test_scoring`, `test_utils`.

## Étapes

1. Écrire l'équivalent pur Python de l'agrégation (dédup par
   (title, link, desc, source, engine, variant), meilleur score par lien via
   dict, sources jointes, tri stable) — comportement bit-à-bit identique sur
   les golden files.
2. Adapter moteurs + rapport ; supprimer l'import.
3. Comparer avant/après sur fixtures : mêmes résultats, même ordre, mêmes
   scores (test de parité temporaire pendant la migration).
4. Mesurer le temps de démarrage avant/après (consigner).

## Critères d'acceptation

- Parité exacte des résultats/scores/ordre sur les fixtures T-015.
- pandas absent de `requirements.txt` et des imports.
- Démarrage mesurablement plus rapide (consigné).

## Commandes de test

```powershell
.venv\Scripts\python.exe -m unittest tests.test_search_orchestrator tests.test_scoring tests.test_utils
.venv\Scripts\python.exe -m unittest discover
```

## Risques

- Différences subtiles de tri/dédup (stabilité, NaN/None) : le test de parité
  temporaire est obligatoire avant suppression du chemin pandas.
- Toucher `search_orchestrator.py` en même temps que T-010/T-014 : interdit —
  séquencer après la phase 1.
