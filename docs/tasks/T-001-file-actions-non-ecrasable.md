# T-001 — File d'actions non écrasable côté pages

- **Statut** : todo
- **Priorité** : P0 · **Effort** : faible
- **Outil recommandé** : Codex
- **Dépendances** : aucune

## Objectif

Aucun clic utilisateur (save, capture, archive, entité) ne doit être perdu
lorsque deux actions surviennent entre deux ticks de polling ou pendant une
recherche en cours.

## Contexte

Le backend lit les actions via une variable scalaire écrasable :
`window.__synthesixSavePageAction` (écriture aux clics, lecture/remise à null
dans `_install_and_consume_save_overlay`, `main.py:1073-1075`). Deux clics
entre deux ticks (intervalle 250 ms, ou bien plus pendant qu'une recherche
bloque la boucle) = la première action est silencieusement écrasée. Même
schéma côté pages locales : `window.synthesixHome.consumeAction()` et
`window.synthesixPage.consumeAction()` ne renvoient qu'une action à la fois
(acceptable si elles utilisent déjà une file interne — à vérifier dans
`index.html` et `investigations/view.py`).

## Fichiers concernés

- `main.py` : JS généré dans `_install_and_consume_save_overlay` (tous les
  `window.__synthesixSavePageAction = {...}`) et la consommation.
- `main.py` : boucle `wait_for_home_action` — traiter une **liste** d'actions.
- `index.html`, `investigations/view.py` : vérifier que `consumeAction` draine
  une file ; sinon aligner sur le même modèle tableau.

## Étapes

1. Côté JS injecté : remplacer chaque affectation scalaire par
   `(window.__synthesixActions = window.__synthesixActions || []).push({...})`.
2. Côté consommation : drainer atomiquement
   (`const a = window.__synthesixActions || []; window.__synthesixActions = []; return a;`).
3. Côté Python : `_install_and_consume_save_overlay` renvoie une liste ;
   `wait_for_home_action` retourne la première action et re-empile les
   suivantes (ou les traite en séquence — choisir le plus simple, documenter).
4. Vérifier `consumeAction` des pages locales ; corriger si écrasable.
5. Garder la compatibilité : liste vide ⇒ comportement identique à `null`.

## Critères d'acceptation

- Deux actions poussées dans le même tick sont toutes deux traitées, dans
  l'ordre d'émission.
- Aucun changement de contrat pour les actions elles-mêmes (mêmes champs).
- `python -m unittest tests.test_main` vert.

## Commandes de test

```powershell
.venv\Scripts\python.exe -m unittest tests.test_main
.venv\Scripts\python.exe -m unittest tests.test_home_ui
```

Ajouter un test : FakeTab dont `evaluate` renvoie deux actions ⇒ les deux
atteignent le dispatcher.

## Risques

- Oubli d'un point d'écriture scalaire dans le JS généré (grep
  `__synthesixSavePageAction` doit rendre zéro occurrence hors compatibilité).
- Double traitement si le drain n'est pas atomique (drainer dans un seul
  `evaluate`).
