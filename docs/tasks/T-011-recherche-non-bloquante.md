# T-011 — Recherche non bloquante + annulation

- **Statut** : todo
- **Priorité** : P0 · **Effort** : moyen-élevé
- **Outil recommandé** : Claude
- **Dépendances** : T-001 (file d'actions), T-010 (annulation propre)

## Objectif

La boucle d'actions ne doit jamais être gelée par une recherche : l'utilisateur
peut continuer à sauvegarder des pages, capturer, et peut annuler la recherche
en cours.

## Contexte

Dans `main()` (`main.py`), chaque action `search`/retry fait
`await perform_search(...)` inline : pendant toute la durée (jusqu'à plusieurs
minutes aujourd'hui, ≤ budget après T-010), plus aucun tick de
`wait_for_home_action`, donc plus aucune action consommée. Combiné au scalaire
écrasable (corrigé par T-001), des clics étaient perdus. Il n'existe aucun
moyen d'annuler une recherche.

## Fichiers concernés

- `main.py` : handlers d'action `search`/`retry` dans `main()`,
  `wait_for_home_action` (aucun changement attendu), nouvel état
  `active_search_task`.
- `index.html` + `assets/synthesix-ui.js` (source `frontend/`) : bouton/état
  « Annuler la recherche » sur la home (peut être un lot séparé T-011b si le
  frontend dépasse l'effort prévu).
- `tests/test_main.py`.

## Étapes

1. Extraire le traitement d'une action de recherche dans une coroutine
   `_run_search_action(...)` qui gère aussi les statuts home
   (`_set_home_status`) en fin de tâche.
2. Dans le handler : si une recherche est déjà active ⇒ statut « une recherche
   est déjà en cours » (une seule recherche à la fois, choix assumé) ; sinon
   `active_search_task = asyncio.create_task(_run_search_action(...))` et
   retour immédiat à la boucle de poll.
3. Nouvelle action `cancel_search` (home) : `active_search_task.cancel()` ;
   le `finally` des moteurs ferme les tabs ; statut « Recherche annulée ».
4. Fin de tâche : callback `add_done_callback` ou attente dans la boucle pour
   consigner les exceptions non gérées (aucune exception silencieuse).
5. Frontend home : état visuel « recherche en cours… / Annuler » branché sur
   l'action existante de statut (si trop large, scinder en T-011b avec le
   build frontend : `npm run typecheck && npm run build`).
6. Garde d'arrêt : à la sortie de `main()` (quit), annuler la tâche active et
   l'attendre avant `browser_manager.stop()`.

## Critères d'acceptation

- Pendant une recherche simulée lente : une action `save_page_to_investigation`
  émise depuis un tab externe est traitée sans attendre la fin de la recherche.
- `cancel_search` interrompt la recherche ≤ 2 s, tabs moteurs fermés, statut
  home mis à jour.
- Quit pendant une recherche : arrêt propre, pas de tâche orpheline ni
  d'exception non consignée.

## Commandes de test

```powershell
.venv\Scripts\python.exe -m unittest tests.test_main
.venv\Scripts\python.exe -m unittest tests.test_search_orchestrator
```

Smoke manuel obligatoire : recherche réelle + save page pendant la recherche +
annulation. Consigner le résultat.

## Risques

- Accès concurrents : la recherche écrit l'historique/DB pendant que la boucle
  traite d'autres actions ⇒ SQLite est sérialisé par connexion-par-opération
  (WAL), mais vérifier `record_search` vs actions d'enquête simultanées
  (`busy_timeout` 5 s couvre). Documenter.
- Deux sources de vérité pour « recherche en cours » (backend vs UI) : le
  backend fait foi, l'UI n'affiche que le statut poussé.
