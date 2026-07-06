# T-010 — Deadline globale de recherche + résultats partiels

- **Statut** : todo
- **Priorité** : P0 · **Effort** : moyen
- **Outil recommandé** : Claude
- **Dépendances** : T-050 recommandé (FakeTab pour les tests), pas bloquant

## Objectif

Une recherche ne doit jamais dépasser un budget de temps global configurable
(défaut proposé : 120 s). À l'échéance : annulation des tâches moteurs
restantes, retour des résultats déjà obtenus, statut `timeout` dans la
couverture pour les moteurs interrompus.

## Contexte

`_run_engines` (`search_orchestrator.py:309-396`) lance jusqu'à
variantes × moteurs tâches sous un sémaphore (`engine_concurrency`, défaut 4).
Chaque tentative dispose de `engine_search_timeout` (90 s) et il y a jusqu'à
`engine_retry_attempts` retries : pire cas réaliste = plusieurs minutes sans
plafond global (ex. 6 variantes × 4 moteurs lents). Le timer `wait_for` ne
démarre qu'après acquisition du sémaphore, donc la file d'attente s'additionne.

## Fichiers concernés

- `search_orchestrator.py` : `_run_engines`, `SearchRunResult`.
- `settings.py` : nouveau `search_total_budget`
  (`SYNTHESIX_SEARCH_TOTAL_BUDGET`, défaut 120.0).
- `tests/test_search_orchestrator.py`.

## Étapes

1. Ajouter le réglage `search_total_budget` dans `AppSettings`.
2. Dans `_run_engines`, remplacer le `asyncio.gather` par
   `asyncio.wait(tasks, timeout=budget)` ; pour les tâches `pending` :
   `task.cancel()`, attendre leur terminaison (`gather(return_exceptions=True)`),
   consigner `TimeoutError("search budget exceeded")` comme erreur moteur et
   `{"status": "timeout"}` dans la couverture.
3. Vérifier le chemin d'annulation : `SearchEngine.search` ferme le tab dans
   `finally` ; s'assurer qu'aucun `except Exception` n'avale `CancelledError`
   (elle hérite de `BaseException` en 3.10 — vérifier chaque handler des
   moteurs et de `_search_engine_with_retries`).
4. Conserver la règle actuelle « tous en échec ⇒ exception » mais la baser sur
   les moteurs *terminés* : si le budget expire alors que certains ont réussi,
   retourner les résultats partiels.
5. Journaliser clairement : budget, moteurs interrompus.

## Critères d'acceptation

- Un moteur simulé qui dort 999 s n'empêche pas le retour ≤ budget + 5 s.
- Les résultats des moteurs rapides sont présents ; la couverture marque les
  lents en `timeout`.
- Aucun tab moteur laissé ouvert après annulation (assert sur FakeTab.closed).
- Suite `tests.test_search_orchestrator` verte.

## Commandes de test

```powershell
.venv\Scripts\python.exe -m unittest tests.test_search_orchestrator
.venv\Scripts\python.exe -m unittest tests.test_search_engine_errors
```

## Risques

- Annulation pendant une résolution manuelle de captcha (DDG attend jusqu'à
  75 s) : le budget global doit rester > aux timeouts de challenge, sinon on
  coupe l'utilisateur en pleine résolution. Documenter la relation entre
  `search_total_budget`, `duckduckgo_robot_timeout` et `brave_results_timeout`
  dans `settings.py`.
