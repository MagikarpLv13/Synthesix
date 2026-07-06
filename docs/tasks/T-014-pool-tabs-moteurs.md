# T-014 — Pool de tabs moteurs + fin des vols de focus

- **Statut** : todo
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

## Risques

- État résiduel entre variantes sur un même tab (cookies de session moteur,
  scroll) : acceptable — même profil qu'aujourd'hui ; la navigation remplace
  le document.
- Un moteur bloqué en challenge monopolise son tab : le budget global (T-010)
  et la libération en `finally` bornent le coût.
- Devient partiellement obsolète si T-040 (navigateur de recherche séparé)
  arrive vite ; le pool reste utile dans les deux cas (il vit côté instance de
  recherche).
