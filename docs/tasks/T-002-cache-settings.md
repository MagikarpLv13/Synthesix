# T-002 — Cache `get_settings()`

- **Statut** : todo
- **Priorité** : P1 · **Effort** : faible
- **Outil recommandé** : Codex
- **Dépendances** : aucune

## Objectif

Arrêter de reconstruire `AppSettings` (~40 lectures d'environnement +
résolutions de chemins) à chaque appel, y compris dans des boucles à 100 ms.

## Contexte

`get_settings()` (`settings.py:113`) reconstruit l'objet à chaque appel. Il
est appelé dans les boucles d'attente moteurs (`search_engine.py:213`,
`duckduckgo.py:189-193`, `brave.py:246`) et à chaque tick de
`wait_for_home_action`. Les tests s'appuient sur des variables d'environnement
modifiées en cours de suite : il faut un point d'invalidation explicite.

## Fichiers concernés

- `settings.py` : `get_settings`, nouvelle fonction `reload_settings()`.
- `tests/test_settings.py` et tout test qui patche `SYNTHESIX_*` (grep
  `os.environ` + `SYNTHESIX_` dans `tests/`) : appeler `reload_settings()`
  (ou `get_settings.cache_clear()`) dans `setUp`/`tearDown`.

## Étapes

1. Décorer `get_settings` avec `functools.lru_cache(maxsize=1)`.
2. Ajouter `reload_settings()` qui fait `cache_clear()` puis retourne
   `get_settings()`.
3. Adapter `apply_cli_runtime_overrides` (`main.py`) : il modifie
   `os.environ["SYNTHESIX_DEBUG_HTML"]` — appeler `reload_settings()` après.
4. Adapter les tests qui modifient l'environnement.
5. Grep des usages restants pour vérifier qu'aucun code ne dépend d'une
   relecture dynamique de l'environnement en cours d'exécution.

## Critères d'acceptation

- Un seul objet `AppSettings` construit par processus en fonctionnement normal.
- `--debug-html` fonctionne toujours (override CLI pris en compte).
- Suite complète verte.

## Commandes de test

```powershell
.venv\Scripts\python.exe -m unittest tests.test_settings
.venv\Scripts\python.exe -m unittest discover
```

## Risques

- Test qui oublie l'invalidation ⇒ fuite d'état entre tests. Mitigation :
  helper unique `reload_settings()` utilisé partout, documenté dans le
  docstring de `get_settings`.
