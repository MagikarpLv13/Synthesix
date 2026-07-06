# T-002 — Cache `get_settings()`

- **Statut** : done (2026-07-06, Claude)
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

## Résultat (2026-07-06)

- Approche retenue différente du plan initial (meilleure) : au lieu de
  `lru_cache` + invalidations manuelles dans ~30 sites de test `patch.dict`,
  cache invalidé par **signature d'environnement** (`SYNTHESIX_*` triés +
  `os.getcwd()`, car `base_dir` défaut = `.`). Résultat : un seul objet
  `AppSettings` par environnement stable, et les tests existants
  (patch.dict, chdir) restent corrects **sans aucune modification**.
- `reload_settings()` fourni pour forcer un rebuild explicite.
- `--debug-html` (`apply_cli_runtime_overrides`) : aucun changement requis —
  la modification d'env change la signature, rebuild automatique.
- Tests : 3 nouveaux cas `SettingsCacheTestCase` + **suite complète
  `discover` : 307 tests OK**.
