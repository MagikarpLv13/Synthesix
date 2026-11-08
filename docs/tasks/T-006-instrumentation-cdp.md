# T-006 — Instrumentation compteurs CDP + budget par tick

- **Statut** : done (2026-07-06, Claude)
- **Priorité** : P1 · **Effort** : faible-moyen
- **Outil recommandé** : Claude
- **Dépendances** : aucune (à faire AVANT les optimisations de phase 1-3 pour
  disposer d'une mesure de référence)

## Objectif

Mesurer objectivement le trafic CDP (nombre d'appels, catégories, octets JS
évalués, durées) pour valider chaque optimisation par un avant/après, et
verrouiller le gain par un test de budget.

## Contexte

La review a estimé ~8-30 appels CDP/s à vide selon le nombre de tabs
(`wait_for_home_action`, `main.py:2280-2357`) et ~15-20 Ko de JS ré-évalués
par tab externe par tick (`_install_and_consume_save_overlay`). Ces chiffres
doivent être mesurés, pas estimés, avant de refactorer.

## Fichiers concernés

- Nouveau : `observability.py` (compteurs process-wide, simple dict +
  `logging`).
- `main.py` : incréments aux points d'appel (`_open_tabs`, chaque helper
  `evaluate`), dump périodique en `--verbose`.
- `search_engine.py`, `duckduckgo.py`, `brave.py` : incréments dans les
  boucles d'attente.
- Nouveau test : `tests/test_cdp_budget.py`.

## Étapes

1. Créer `observability.py` : `count(category)`, `observe_bytes(category, n)`,
   `snapshot()`, `reset()`. Zéro dépendance, thread-safe simple.
2. Instrumenter : catégories `targets_poll`, `eval_home`, `eval_overlay`,
   `eval_settings`, `eval_page`, `eval_engine_wait`, `get_content`,
   `screenshot`. Compter aussi `len(script)` pour les evaluates.
3. En `--verbose` : log d'un snapshot toutes les 10 s (appels/s par catégorie,
   Ko évalués/s).
4. Test budget : simuler N ticks de `wait_for_home_action` avec FakeBrowser
   (2 tabs home+externe) et affirmer un plafond d'appels par tick (fixer le
   plafond à la valeur mesurée actuelle ; les tâches suivantes l'abaisseront).
5. Consigner la mesure de référence (idle, 1 home + 2 externes, 60 s) dans la
   note de clôture de la tâche et dans `PROJECT_STATE.md`.

## Critères d'acceptation

- `python main.py --verbose` affiche les compteurs périodiques.
- `tests/test_cdp_budget.py` échoue si un changement futur augmente le nombre
  d'appels par tick au-delà du plafond consigné.
- Surcoût nul en mode non verbeux (compteurs O(1), pas d'allocation notable).

## Commandes de test

```powershell
.venv\Scripts\python.exe -m unittest tests.test_cdp_budget
.venv\Scripts\python.exe -m unittest discover
```

## Risques

- Instrumentation oubliée sur un nouveau point d'appel : accepté, le budget
  par tick couvre le chemin chaud principal.
- Dépend de FakeBrowser minimal : si T-050 n'est pas encore fait, créer ici un
  fake local minimal et le déplacer vers `tests/fakes.py` lors de T-050.

## Résultat (2026-07-06)

- Nouveau module `observability.py` : `count`, `observe_bytes`, `snapshot`,
  `reset`, `maybe_log_snapshot` (dump DEBUG toutes les 10 s, no-op sinon).
- Instrumenté : `main.py` (`targets_poll`, `eval_home` + octets payloads,
  `eval_overlay` ×2 + octets bundle/contexte, `eval_settings`, `eval_page`,
  `screenshot`, dump périodique dans `wait_for_home_action`) ;
  `search_engine.py` (`eval_engine_wait`, `get_content` + octets) ;
  `duckduckgo.py`, `brave.py` (`eval_engine_wait` des boucles d'attente).
- Nouveau `tests/test_cdp_budget.py` : verrouille la baseline par tick à vide
  (topologie 1 home + 1 externe + 1 page enquête) :
  **1 inventaire targets + 6 evaluates par tick idle**
  (2 settings, 1 home, 2 overlay, 1 page) ; le tick qui rend une action home
  saute la boucle overlay/page. `eval_home` transfère les payloads
  history+investigations à chaque tick (à faire tomber à 0 en régime stable
  par T-003).
- Tests : `test_cdp_budget`, `test_main`, `test_engines`,
  `test_search_engine_errors` → 75 OK.
- Non exécuté : mesure 60 s sur session navigateur réelle (nécessite un run
  interactif) — la baseline verrouillée par le test fait référence ;
  compléter au premier smoke réel de la phase 1.
