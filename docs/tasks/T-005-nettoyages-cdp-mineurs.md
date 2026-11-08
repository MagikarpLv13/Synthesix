# T-005 — Nettoyages CDP mineurs

- **Statut** : done (2026-07-06, Claude)
- **Priorité** : P2 · **Effort** : faible
- **Outil recommandé** : Codex
- **Dépendances** : aucune

## Objectif

Éliminer quatre irritants à faible risque : double requête Target par tick,
`window.name` re-posé en boucle, set d'armement jamais purgé, boucle zombie
possible après crash navigateur.

## Contexte

1. `_open_tabs` (`main.py:137-154`) appelle `browser.update_targets()` **puis**
   `browser._get_targets()` (API privée) : deux requêtes `Target.getTargets`
   par tick, et une dépendance à une API interne de zendriver 0.15.3.
2. `_consume_home_tab_action` (`main.py:181`) exécute
   `window.name = "synthesix-home"` à chaque tick. `window.name` survit aux
   navigations cross-origin : si l'utilisateur navigue depuis le tab home vers
   un site externe, ce site peut lire le marqueur (traçabilité OSINT).
3. `_OVERLAY_FOCUS_GUARD_ARMED_TARGETS` (`main.py:361`) n'est jamais purgé à la
   fermeture des tabs.
4. Après un crash de Chrome, `_open_tabs` retourne `None` indéfiniment et
   `wait_for_home_action` boucle en silence (`browser.stopped` n'est vrai
   qu'après un `stop()` propre).

## Fichiers concernés

- `main.py` : `_open_tabs`, `_consume_home_tab_action`,
  `_OVERLAY_FOCUS_GUARD_ARMED_TARGETS`, `wait_for_home_action`.

## Étapes

1. `_open_tabs` : une seule source de vérité — `await browser.update_targets()`
   puis filtrer `browser.targets`/`browser.tabs` sans `_get_targets()` ;
   vérifier le comportement sur zendriver 0.15.3.
2. `window.name` : ne poser la valeur que si
   `window.name !== "synthesix-home"` (condition dans le JS existant), et la
   nettoyer n'est pas nécessaire — le home tab est identifié par URL.
3. Purger `_OVERLAY_FOCUS_GUARD_ARMED_TARGETS` : retirer les target_ids absents
   de la liste des tabs vivants à chaque passage de `_open_tabs` (ou borner la
   taille du set).
4. Boucle zombie : compter les retours `None` consécutifs de `_open_tabs` ;
   au-delà d'un seuil (ex. 40 ≈ 10 s), retourner `{"action": "quit"}` avec un
   log explicite.

## Critères d'acceptation

- Une seule requête `Target.getTargets` par tick (visible via T-006 si déjà
  fait, sinon par lecture du code).
- Plus aucun usage de `browser._get_targets` dans le dépôt.
- Kill du process Chrome pendant l'exécution ⇒ Synthesix se termine proprement
  en ~10 s avec un log clair (smoke manuel).

## Commandes de test

```powershell
.venv\Scripts\python.exe -m unittest tests.test_main
```

Smoke manuel : lancer l'app, tuer le process Chrome, vérifier l'arrêt propre.

## Risques

- Différence de fraîcheur entre `browser.tabs` et les targets réels selon la
  version zendriver : garder le filtre « type page » actuel.

## Résultat (2026-07-06)

1. **Dédoublonnage targets : non réalisable proprement sur zendriver 0.15.3**
   (vérifié dans le source du paquet) : `update_targets()` ajoute et met à
   jour les targets mais ne retire jamais les fermés, et `Connection.closed`
   est aussi vrai pour des tabs vivants jamais attachés — le second
   `_get_targets()` est le seul moyen de filtrer les vivants. Les deux
   requêtes restent, avec un commentaire en code expliquant pourquoi ; T-022
   (événements Target) les supprimera toutes les deux. Usage privé confiné à
   `_open_tabs`.
2. `window.name` conditionnel : déjà livré par T-003 (probe home).
3. Purge de `_OVERLAY_FOCUS_GUARD_ARMED_TARGETS` : `intersection_update` avec
   les pages vivantes à chaque inventaire.
4. Garde anti-zombie : `_BROWSER_UNREACHABLE_QUIT_SECONDS = 10.0` — si
   `_open_tabs` échoue en continu (Chrome tué), la boucle quitte proprement
   avec un log au lieu de tourner en silence.
- Tests : `tests.test_cdp_budget` (2 nouveaux : purge du set + quit sur
  navigateur injoignable), `tests.test_main` → 39 OK. Smoke réel
  « kill Chrome » non exécuté (couvert par le test unitaire ; à observer au
  prochain run réel).
