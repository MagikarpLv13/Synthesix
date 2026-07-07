# T-021 — Push `Runtime.addBinding` pour pages locales

- **Statut** : review (2026-07-07, Claude)
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

## Réalisé (2026-07-07)

Spike de risque levé en premier : `zendriver` 0.15.3 expose bien
`cdp.runtime.add_binding` / `cdp.runtime.BindingCalled`, et
`Connection.add_handler` route l'événement vers un callback coroutine
planifié par `asyncio.create_task` (jamais un thread — important, cf. plus
bas) sans jamais l'appeler nulle part par défaut (`Runtime.enable` doit être
appelé explicitement).

**Périmètre réduit par rapport à la fiche initiale**, après vérification du
code réel :
- `investigations/search_view.py` : page statique sans `queueAction` ni
  `synthesixPage` → rien à faire.
- `utils.py::_home_navigation_script` : code mort, aucun appelant dans le
  dépôt → rien à faire.
- Chaque page vivante n'a qu'**un seul point d'émission d'action**
  (`queueAction` dans `index.html` et `investigations/view.py`) : un seul
  endroit à modifier par page, pas un balayage de chaque site d'appel.

**Déviation de conception assumée** : plutôt que de ralentir la cadence de
toute la boucle en mode push (ce que suggérait l'étape 5), le repli est
découplé en deux mécanismes indépendants pour ne pas régresser l'overlay
CDP sur les pages http/https (hors périmètre T-021, DEC-PLAN-04) :
- le `sleep` de fin de boucle devient une course
  `asyncio.wait_for(service.dispatch_queue.get(), timeout=home_poll_interval)`
  — timeout inchangé, donc aucune régression sur l'overlay/scan réglages ;
  seul effet : réveil immédiat si une action est pushée pendant l'attente ;
- le budget CDP réduit vient du throttle de l'évaluation de consommation
  par tab locale (`_should_sync_local_tab` / `_mark_local_tab_synced` dans
  `main.py`), rejouée seulement tous les `home_push_fallback_interval`
  (2 s par défaut) une fois le binding confirmé — l'overlay et le scan de
  réglages ne sont pas concernés par ce throttle.

**Piège corrigé pendant l'implémentation** : le handler CDP doit rester une
coroutine — `Connection`'s dispatch exécute les callbacks synchrones via
`asyncio.to_thread` (thread séparé), où toucher `asyncio.Queue` n'est pas
sûr ; un handler `async def` reste sur la boucle événementielle
(`asyncio.create_task`), seul chemin sûr pour `put_nowait`.

- **Fichiers modifiés** : `browser/service.py`, `main.py`, `settings.py`,
  `index.html`, `investigations/view.py`, `observability.py`,
  `tests/fakes.py`, `tests/test_browser_service.py`,
  `tests/test_cdp_budget.py`, `tests/test_transport_push.py` (nouveau).
- **Tests exécutés** : `tests.test_transport_push` (4),
  `tests.test_browser_service` (20), `tests.test_cdp_budget` (4, ré-ancré en
  mode poll explicite pour le baseline historique), `tests.test_main` (42),
  `unittest discover` (360 OK), `node --check` sur le script inline
  d'`investigations/view.py` (test existant) et sur celui d'`index.html`
  (vérifié manuellement), `git diff --check` (CRLF uniquement).
- **Non exécuté** : smoke CDP live (session Chrome réelle confirmant
  latence < 50 ms et la baisse réelle du taux `eval_home`/`eval_page` sans
  régression sur `eval_overlay`) — à faire au premier run interactif ;
  comportement couvert par la suite unitaire (harnais `FakeTab.fire`).
- **Risque résiduel** : persistance du binding across navigation (pas
  seulement reload) documentée par CDP mais pas vérifiée en direct pour ce
  dépôt ; si un rechargement complet perdait le binding, le repli poll
  (`_should_sync_local_tab` retombe à `True` tant que non re-confirmé)
  couvre le cas sans perte d'action, seulement avec une latence dégradée
  temporaire.
