# T-022 — Découverte de tabs par événements Target

- **Statut** : todo
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
