# T-035 — Contexte investigation + statuts vers l'extension

- **Statut** : todo
- **Priorité** : P1 · **Effort** : moyen
- **Outil recommandé** : Claude
- **Dépendances** : T-034

## Objectif

Sens backend → extension complet : l'overlay affiche l'investigation active,
ses tags/entités (menus), et les états de boutons (saving/saved/error,
capturing/captured, archiving/archived) — sans polling.

## Contexte

Aujourd'hui le contexte (investigation, tagsets, entités) est re-sérialisé
dans chaque evaluate de tick (`_install_and_consume_save_overlay`,
`main.py:494-566`) et les statuts sont poussés par 3 helpers evaluate
(`_set_save_overlay_status`, `_set_evidence_overlay_status`,
`_set_archive_overlay_status`, `main.py:1084-1179`). Le backend sait déjà
détecter un changement de workspace (hash de `_investigation_payload`,
`main.py:223-230`).

Cible : push sur changement uniquement — `Runtime.evaluate` dans le SW
(canal T-031) ⇒ `chrome.storage.local` (contexte) + `chrome.tabs.sendMessage`
(statuts ciblés). Les content scripts lisent le storage à l'installation et
s'abonnent à `chrome.storage.onChanged` : les nouveaux tabs ont le contexte
sans aller-retour backend.

## Fichiers concernés

- `extension/src/background.ts` : réception contexte/statuts, storage,
  diffusion.
- `extension/src/content/bootstrap.ts` + `overlay-main.ts` : application du
  contexte (menus entités, tags) et des états boutons (API publiques Lit
  existantes).
- Backend (`main.py` / `browser/service.py`) : push du contexte quand le hash
  workspace change ou quand l'investigation active change ; remplacement des
  3 helpers de statut par un envoi ciblé `{tabId, kind, state, message}` en
  mode extension.
- `tests/test_main.py` (sélection du canal selon le mode).

## Étapes

1. Définir les deux messages : `context_update` (payload = celui de
   `overlay_investigation` actuel, `main.py:2430-2459`) et `button_status`
   (mêmes états que les helpers actuels, y compris les timeouts d'affichage
   gérés côté composant).
2. Backend : émission `context_update` à chaque changement de hash (réutiliser
   `_investigation_payload`) et au démarrage ; suppression de la re-sérialisation
   par tick en mode extension.
3. Extension : appliquer au chargement + onChanged ; statuts routés au bon tab.
4. Étendre l'action `observe_saved_page` (marquage « déjà sauvegardée ») au
   canal extension : le content script l'émet une fois par (investigation,
   URL), comme la logique `observationKey` actuelle (`main.py:1058-1071`).
5. Smoke : changer d'investigation active pendant que 3 tabs http(s) sont
   ouverts ⇒ les 3 overlays se mettent à jour < 1 s ; save ⇒ bouton « Saved » ;
   erreur simulée ⇒ état erreur puis retour idle.

## Critères d'acceptation

- Aucun transfert de contexte en régime stable (rien ne change ⇒ zéro
  message), vérifiable par log SW.
- Nouveau tab ouvert : overlay immédiatement contextualisé (storage), sans
  aller-retour backend.
- Parité visuelle avec le mode CDP sur les 3 boutons et les 3 états chacun.

## Commandes de test

```powershell
cd frontend; npm run typecheck; npm run build; cd ..
.venv\Scripts\python.exe -m unittest tests.test_main
```

Smoke réel multi-tabs consigné.

## Risques

- Contexte volumineux (grosses enquêtes, centaines d'entités) dans
  `chrome.storage.local` : quota 10 Mo, payload actuel < 1 Mo — surveiller,
  sinon ne pousser que les champs utilisés par les menus.
- Ordre des messages après réveil du SW : le contexte est relu du storage,
  pas rejoué — pas de dépendance à l'ordre.
