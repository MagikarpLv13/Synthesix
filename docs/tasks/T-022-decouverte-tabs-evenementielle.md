# T-022 — Découverte de tabs par événements Target

- **Statut** : review (2026-07-07, Claude)
- **Priorité** : P2 · **Effort** : moyen
- **Outil recommandé** : Claude
- **Dépendances** : T-020, T-021

## Objectif

Remplacer l'inventaire des tabs par tick (`Target.getTargets` 4×/s) par les
événements `Target.targetCreated` / `targetInfoChanged` / `targetDestroyed`,
avec une resynchronisation lente de secours.

## Contexte

`_open_tabs` (`main.py:137-154`) interroge les targets à chaque tick pour
détecter nouveaux tabs, fermetures et le cas « plus aucun tab ⇒ quit »
(`empty_tabs_grace_seconds`). Zendriver maintient déjà `browser.targets` à
partir des événements Target ; la boucle n'a besoin que d'un registre à jour
et de notifications.

## Fichiers concernés

- `browser/service.py` : registre de tabs entretenu par événements
  (`on_event`), callbacks `on_tab_created` / `on_tab_removed`.
- `main.py` : `wait_for_home_action` (suppression de l'inventaire par tick),
  logique quit « zéro tab » basée sur le registre.
- Purge automatique de `_OVERLAY_FOCUS_GUARD_ARMED_TARGETS` et des versions
  poussées T-003 sur `on_tab_removed` (si pas déjà fait).

## Étapes

1. Service : s'abonner aux événements Target au démarrage ; maintenir
   `self._tabs: dict[target_id, TabInfo]` (type page uniquement, URL suivie
   via `targetInfoChanged`).
2. Resync de secours : un `Target.getTargets` toutes les 10 s pour corriger
   toute dérive (journaliser si une dérive est détectée — signal de bug).
3. Brancher l'armement à la création : focus guard / binding / (plus tard)
   contexte extension s'arment dans `on_tab_created` au lieu du tick.
4. Adapter le quit « zéro tab » : déclenché par le registre vide pendant
   `empty_tabs_grace_seconds`, plus robuste au crash (conserver le garde T-005).
5. Mesure T-006 : `targets_poll` doit tomber à ~0,1/s.

## Critères d'acceptation

- Ouverture d'un tab externe ⇒ armement (guard/binding) en < 500 ms sans tick.
- Fermeture du dernier tab ⇒ quit après la grâce, comme aujourd'hui.
- Aucune requête `Target.getTargets` en régime stable hors resync 10 s.
- Suite verte + smoke réel (ouvrir/fermer des tabs en rafale).

## Commandes de test

```powershell
.venv\Scripts\python.exe -m unittest tests.test_main tests.test_transport_push
```

Smoke réel : rafales d'ouverture/fermeture, kill Chrome, quit normal.

## Risques

- Événements manqués pendant une reconnexion CDP : couverts par la resync 10 s.
- Ordre création/armement : une page peut commencer à charger avant
  l'armement du script new-document ; le focus guard tolère déjà ce cas
  (installé pour les navigations suivantes), l'extension (T-03x) le supprime
  pour les pages http(s).

## Réalisé (2026-07-07)

**Spike confirmé** : `zendriver` 0.15.3 s'abonne déjà à
`Target.targetCreated/InfoChanged/Destroyed` sur la connexion navigateur
(`set_discover_targets(discover=True)` + `_handle_target_update`) et
maintient `browser.targets` — **suppressions incluses** (le handler retire
l'entrée sur `TargetDestroyed`, contrairement à `update_targets()` qui
n'ajoute/rafraîchit que). Le `Listener` de la connexion navigateur tourne en
continu (`asyncio.create_task(listener_loop)`), donc les événements Target
alimentent le registre sans aucun poll de notre part.

**Déviation de conception assumée** (par rapport aux étapes 3 et à des
callbacks `on_tab_created`/`on_tab_removed` explicites) : plutôt que de
restructurer l'armement en callbacks événementiels, `BrowserService.tabs()`
lit le registre événementiel à chaque tick et ne fait un `getTargets`
autoritaire que toutes les `target_resync_interval` secondes (10 s par
défaut). L'armement (focus guard / binding) et l'élagage des registres
(`armed_script_targets`, `armed_binding_targets`, `last_local_sync_at`)
restent pilotés par la boucle existante (cadence ≤ `home_poll_interval`), ce
qui satisfait le critère « armement < 500 ms » **sans** poll `getTargets` —
et évite de toucher au chemin overlay http/https (hors périmètre,
DEC-PLAN-04).

**Détection de liveness préservée** : le `getTargets` de resync sert aussi de
sonde CDP — son échec renvoie `None` et alimente le garde
`_BROWSER_UNREACHABLE_QUIT_SECONDS`. Le kill franc de Chrome reste détecté
immédiatement par `browser.stopped` (poll process, sans CDP) en tête de
boucle. Un registre vide **force** un resync (une lacune d'événement
transitoire ne peut donc pas être confondue avec « plus aucun tab ⇒ quit »).

**Détection de dérive** : à chaque resync (hors tout premier), l'ensemble de
page-ids issu du fil est comparé au registre événementiel ; toute divergence
est journalisée en DEBUG (signal de bug d'événements manqués).

- **Fichiers modifiés** : `browser/service.py` (`tabs()` réécrit,
  `_live_page_ids`, `_resync_targets`, attrs `target_resync_interval` /
  `_last_target_resync`), `main.py` (câblage de l'intervalle sur le service
  partagé), `settings.py` (`target_resync_interval`,
  `SYNTHESIX_TARGET_RESYNC_INTERVAL`, défaut 10 s), `tests/test_cdp_budget.py`
  (baseline `targets_poll` 1 au lieu de 1/tick), `tests/test_transport_push.py`
  (proxy de tick = `eval_settings`), `tests/test_browser_service.py`
  (3 nouveaux tests).
- **Tests exécutés** : `tests.test_browser_service` (23),
  `tests.test_cdp_budget` (4), `tests.test_main` (42),
  `tests.test_transport_push` (4), `unittest discover` (363 OK),
  `py_compile` sur `browser/service.py main.py settings.py`,
  `git diff --check` (CRLF uniquement).
- **Non exécuté** : smoke CDP live (rafales d'ouverture/fermeture de tabs,
  kill Chrome, quit normal, mesure `targets_poll` ≈ 0,1/s) — à faire au
  premier run interactif ; couvert en unitaire par le harnais FakeBrowser.
- **Risque résiduel** : entre deux resyncs (≤ 10 s), un décrochage CDP «
  process vivant / websocket mort » n'est détecté qu'au resync suivant ; le
  garde unreachable (10 s) puis le quit s'enchaînent ensuite, et le kill franc
  reste couvert par `browser.stopped`.
