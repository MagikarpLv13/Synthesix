# T-021 — Push `Runtime.addBinding` pour pages locales

- **Statut** : todo
- **Priorité** : P1 · **Effort** : élevé
- **Outil recommandé** : Claude
- **Dépendances** : T-020, T-001

## Objectif

Les pages locales (home `index.html`, pages enquête, rapports) livrent leurs
actions en **push** immédiat via `Runtime.bindingCalled`, au lieu d'être
interrogées par `evaluate` toutes les 250 ms. Le poll devient un fallback lent.

## Contexte

`wait_for_home_action` (`main.py:2280-2357`) interroge chaque tab local par
`evaluate` à chaque tick : latence 0-250 ms, coût CDP permanent (mesure T-006).
CDP offre le chemin inverse : `Runtime.addBinding(name)` expose
`window.<name>(payload)` dans la page ; chaque appel émet un événement
`Runtime.bindingCalled` reçu par zendriver (`add_handler`). Les pages locales
sont nos propres fichiers : on peut y appeler `window.synthesixDispatch(...)`
directement aux points où elles poussent aujourd'hui dans leur file
`consumeAction`.

Périmètre : pages locales uniquement. Les pages http(s) migrent vers
l'extension (T-03x) — ne pas investir sur le poll overlay ici.

## Fichiers concernés

- `browser/service.py` : `arm_binding(tab, name)`, dispatch des
  `bindingCalled` vers une `asyncio.Queue` d'actions typées.
- `main.py` : `wait_for_home_action` consomme la queue avec
  `asyncio.wait_for(queue.get(), timeout=fallback_interval)` ; le poll
  existant devient le fallback (intervalle 2 s) derrière
  `SYNTHESIX_TRANSPORT=push|poll` (défaut `push`).
- `index.html`, `investigations/view.py`, `investigations/search_view.py`,
  `utils.py` (page historique) : appeler `synthesixDispatch` si présent, en
  plus de la file locale existante (compat poll conservée).
- `tests/test_main.py` + nouveau `tests/test_transport_push.py`.

## Étapes

1. Service : `Runtime.enable` + `Runtime.addBinding("synthesixDispatch")` sur
   chaque tab local (armement à la découverte du tab, ré-armement après
   navigation via `arm_new_document_script` qui re-déclare l'usage côté page).
2. Handler `bindingCalled` : parse JSON, valider la forme
   `{action: str, ...}`, empiler `(tab_id, action)` dans la queue.
3. Côté pages : petite fonction utilitaire commune (générée dans le HTML)
   `dispatch(action)` = `window.synthesixDispatch ? synthesixDispatch(JSON.stringify(action)) : file locale`.
4. Boucle : consommer la queue ; conserver les pushes sortants existants
   (setHistory/statuts) inchangés dans cette tâche.
5. Les evaluates de tick restants pour pages locales passent à l'intervalle
   fallback (2 s) uniquement en mode `poll` ou si le binding n'a pas confirmé
   (page ancienne en cache).
6. Mesure T-006 avant/après : appels/s à vide attendus divisés par ~8-10 sur
   les pages locales ; latence d'action ressentie immédiate.

## Critères d'acceptation

- Mode `push` : une action home (recherche) part sans attendre un tick
  (latence < 50 ms mesurée par log horodaté).
- Mode `poll` (flag) : comportement actuel intact.
- Rechargement d'une page locale : le binding refonctionne sans intervention.
- Budget CDP par tick à vide (T-006) abaissé et re-verrouillé.

## Commandes de test

```powershell
.venv\Scripts\python.exe -m unittest tests.test_transport_push tests.test_main
.venv\Scripts\python.exe -m unittest discover
```

Smoke réel : recherche, navigation enquête, statuts, rechargements.

## Risques

- Zendriver 0.15.3 et `bindingCalled` : vérifier que l'événement est bien
  exposé par `add_handler` (sinon, handler bas niveau sur la connexion tab —
  rester dans le service). Point de spike au début de la tâche.
- Payload binding = chaîne : taille limitée en pratique — nos actions sont
  petites ; les gros contenus (upload base64) restent sur le chemin existant.
- Double livraison (binding + file poll) : la page ne pousse dans la file
  locale que si le binding est absent (étape 3).
