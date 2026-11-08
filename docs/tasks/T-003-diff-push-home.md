# T-003 — Payload home poussé seulement sur changement

- **Statut** : done (2026-07-06, Claude)
- **Priorité** : P1 · **Effort** : faible
- **Outil recommandé** : Codex
- **Dépendances** : aucune

## Objectif

Ne plus transférer l'historique et la liste des investigations complets dans
chaque `evaluate` du tick de polling ; ne les envoyer que quand leur version
change.

## Contexte

`_consume_home_tab_action` (`main.py:161-204`) embarque `history_json` et
`investigations_json` entiers dans le JS de chaque tick (4×/s). Le
versionnage actuel (`historyVersion`, `investigationsVersion`) n'évite que
l'application côté page : le transfert et le parse du script ont déjà eu lieu.
Le backend connaît déjà les versions (`_cached_history_payload`,
`_investigation_payload`) — il suffit de mémoriser la dernière version
poussée par tab.

## Fichiers concernés

- `main.py` : `_consume_home_tab_action`, `wait_for_home_action`.

## Étapes

1. Scinder en deux evaluates : (a) un mini-evaluate par tick qui pose
   `window.name` si absent et renvoie `{ready, action, historyVersion,
   investigationsVersion}` ; (b) un evaluate de push (setHistory /
   setInvestigations) exécuté uniquement si la version page ≠ version backend.
2. Alternative plus simple si (a) suffit : mémoriser côté Python
   `pushed_versions[target_id]` et n'embarquer les payloads que si la version
   mémorisée diffère ; vider l'entrée quand le tab disparaît.
3. Vérifier le cas rechargement de la page home (versions page réinitialisées
   ⇒ re-push automatique).

## Critères d'acceptation

- En régime stable (aucun changement d'historique/investigations), le tick
  home ne transfère plus ni `history_json` ni `investigations_json`
  (vérifiable par la taille du script loggée par T-006, ou par un test unitaire
  sur la chaîne JS générée).
- Après une recherche (historique modifié), la home se met à jour comme avant.
- Après rechargement manuel de la home, les données réapparaissent.

## Commandes de test

```powershell
.venv\Scripts\python.exe -m unittest tests.test_main tests.test_home_ui
```

Smoke manuel : lancer l'app, ouvrir la home, lancer une recherche, vérifier
l'historique mis à jour ; recharger la home, vérifier le re-push.

## Risques

- Désynchronisation si la page est rechargée sans que le backend le voie :
  couvert par la lecture de version par tick (étape 1a) ou par re-push quand
  `ready:false→true`.

## Résultat (2026-07-06)

- `_consume_home_tab_action` réduit à un probe léger (consomme une action,
  retourne `historyVersion`/`investigationsVersion` de la page, pose
  `window.name` seulement si absent).
- Nouveau `_push_home_tab_data` : n'embarque chaque payload (history,
  investigations) que si sa version diverge de celle de la page ; robuste au
  rechargement par construction (la page annonce ses versions à chaque tick).
- Régime stable : 1 evaluate léger/tick, 0 octet de payload (verrouillé par
  `test_cdp_budget`, assertion bytes == 0 + nouveau test de divergence :
  probe + push = 2 evaluates, payloads transférés une fois).
- Tests : `tests.test_cdp_budget`, `tests.test_main`, `tests.test_home_ui`
  → 48 OK.
