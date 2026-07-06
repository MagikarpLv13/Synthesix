# T-014 — Pool de tabs moteurs + fin des vols de focus

- **Statut** : done (2026-07-06, AI-20260706-007)
- **Priorité** : P2 · **Effort** : moyen
- **Outil recommandé** : Claude
- **Dépendances** : T-012 (attentes réécrites), T-010 (annulation)

## Objectif

Réduire le churn de tabs pendant une recherche multi-variantes (jusqu'à 24
créations/fermetures aujourd'hui) et supprimer les vols de focus répétés.

## Contexte

- `SearchEngine.navigate` (`search_engine.py:136-163`) :
  `browser.get(url, new_tab=True)` pour **chaque** moteur × variante, puis
  `main_tab.bring_to_front()` à chaque ouverture — la fenêtre de l'utilisateur
  clignote et le focus est volé pendant toute la recherche.
- Chaque tab = un renderer : 24 créations/fermetures par recherche coûtent
  cher et laissent des fenêtres visibles défiler.
- `search_orchestrator._run_engines` crée une instance moteur par
  (moteur × variante) via les factories.

## Fichiers concernés

- `search_engine.py` : `navigate`, `close_tab`, cycle de vie du tab.
- `search_orchestrator.py` : `_run_engines` (réutilisation d'instance moteur
  par moteur, les variantes deviennent des navigations successives du même
  tab quand la concurrence le permet).
- `tests/test_search_orchestrator.py`.

## Étapes

1. Introduire un `TabLease` simple : le moteur demande un tab au début de
   `search()`, le rend à la fin ; le pool (dict moteur→tab, borné par
   `engine_concurrency`) réutilise `tab.get(url)` au lieu de
   `browser.get(url, new_tab=True)` quand un tab est déjà loué pour ce moteur.
2. Supprimer le `main_tab.bring_to_front()` par navigation
   (`search_engine.py:150-156`). Le seul `bring_to_front` légitime reste celui
   des challenges anti-robot (résolution manuelle).
3. Nettoyage garanti : à la fin de la recherche (succès, erreur, annulation),
   fermer tous les tabs du pool (`finally` au niveau orchestrateur).
4. Vérifier l'interaction avec la pagination (Bing/Brave naviguent déjà le
   même tab — inchangé).
5. Mesurer avec T-006 : nombre de créations de tabs par recherche 6 variantes
   × 4 moteurs avant/après (attendu : 24 → ≤ 4-8).

## Critères d'acceptation

- Une recherche multi-variantes ne crée pas plus de tabs que
  `min(engine_concurrency, moteurs actifs)` (+ challenges éventuels).
- Aucun `bring_to_front` hors résolution de challenge pendant une recherche.
- Aucun tab moteur résiduel après succès, échec ou annulation.
- Suite orchestrateur verte.

## Commandes de test

```powershell
.venv\Scripts\python.exe -m unittest tests.test_search_orchestrator tests.test_engines
```

Smoke réel : recherche 4 moteurs multi-variantes, observer la fenêtre (pas de
clignotement de focus), vérifier fermeture des tabs.

## Réalisation (2026-07-06)

- `search_engine.py` : `EngineTabPool` (dict moteur→tab ; `navigate()` réutilise
  `tab.get(url)` si le tab vit, sinon `browser.get(url, new_tab=True)` ;
  compteurs T-006 `engine_tab_open`/`engine_tab_reuse` ; `close_all()` ferme et
  désenregistre `ACTIVE_ENGINE_TAB_TARGETS`). `SearchEngine.navigate` passe par
  le pool quand `tab_pool` est posé ; le `main_tab.bring_to_front()` par
  navigation est supprimé (seuls restent ceux des challenges DDG/Brave). Le
  `finally` de `search()` appelle `release_tab()` : tab rendu au pool s'il lui
  appartient, fermé sinon (couvre les tabs ouverts hors pool).
- `search_orchestrator.py` : `_run_engines` restructuré — une instance moteur
  et une tâche asyncio par moteur ; les variantes sont des navigations
  successives du même tab (sérialisées par moteur, sémaphore
  `engine_concurrency` acquis par variante). Bookkeeping par variante
  incrémental : le budget T-010 annule les tâches moteur restantes et marque
  `timeout` uniquement les variantes non enregistrées. `finally` →
  `pool.close_all()` (succès, échec, annulation).
- Clés d'erreur `engine [variant N]`, statuts coverage, retries par variante
  et pagination Bing/Brave/DDG (même tab) inchangés.
- Tests : `test_selected_query_variants_...` mis à jour (2 instances, appels
  séquentiels) ; +3 tests pool (réutilisation 1 tab/moteur + 0
  `bring_to_front` + désenregistrement, 1 tab par moteur, échec de variante
  puis réutilisation). Suites : `test_search_orchestrator` + `test_engines` +
  `test_search_engine_errors` (72 OK), `unittest discover` (336 OK).
- Non exécuté : smoke réel multi-variantes (fenêtre sans clignotement,
  mesure `engine_tab_open` ≤ moteurs actifs) — au premier run interactif.
- Résiduel : la création initiale d'un tab par moteur peut encore voler le
  focus une fois (plus de refocus compensatoire) ; disparaît avec T-040.

## Risques

- État résiduel entre variantes sur un même tab (cookies de session moteur,
  scroll) : acceptable — même profil qu'aujourd'hui ; la navigation remplace
  le document.
- Un moteur bloqué en challenge monopolise son tab : le budget global (T-010)
  et la libération en `finally` bornent le coût.
- Devient partiellement obsolète si T-040 (navigateur de recherche séparé)
  arrive vite ; le pool reste utile dans les deux cas (il vit côté instance de
  recherche).
