# T-031 — Spike : transport extension ↔ backend Python

- **Statut** : todo
- **Priorité** : P0 (bloquant pour T-034/T-035/T-036) · **Effort** : moyen
- **Outil recommandé** : Claude
- **Dépendances** : T-030 (squelette chargeable)

## Objectif

Valider expérimentalement le canal de communication entre le service worker
de l'extension et le backend Python, **sans serveur local**. Livrable : une
note de décision (dans ce fichier + `PROJECT_STATE.md`) et un prototype
minimal jetable, pas du code produit.

## Contexte

Contraintes : local-first, pas de serveur ni de port ouvert (invariant
AGENTS.md §4 « sans serveur »), le navigateur est déjà piloté par CDP.

### Option A (privilégiée) — binding CDP sur le service worker

Le SW de l'extension apparaît comme target CDP (`type: service_worker`,
URL `chrome-extension://<id>/...`). Python s'y attache
(`Target.attachToTarget`), y fait `Runtime.addBinding("synthesixDispatch")`,
et le SW appelle `synthesixDispatch(json)` pour pousser les actions reçues
des content scripts (`chrome.runtime.sendMessage`). Sens Python→extension :
`Runtime.evaluate` dans le contexte SW (qui rediffuse aux content scripts via
`chrome.tabs.sendMessage`). Un seul target à gérer, événements natifs.

Points à prouver dans le spike :
1. zendriver 0.15.3 expose-t-il le target SW et permet-il de s'y attacher
   proprement (sinon : connexion websocket bas niveau via l'API zendriver) ?
2. `Runtime.addBinding` fonctionne-t-il dans un contexte SW d'extension ?
3. Cycle de vie MV3 : le SW s'endort (~30 s d'inactivité). La session CDP
   attachée le maintient-elle éveillé ? Sinon : ré-armement sur l'événement
   Target de réapparition + file d'attente côté `chrome.storage.session`
   pour ne rien perdre pendant le sommeil.
4. Latence aller simple content script → Python (< 100 ms attendu).

### Option C (repli simple) — poll du seul SW

Si le binding échoue : Python poll UNE cible (le SW) toutes les 250 ms au
lieu de N pages. Déjà un gros progrès vs l'existant ; latence conservée.

### Option B (dernier recours) — native messaging

Host natif (manifeste JSON + script Python lancé par Chrome, stdio). Fiable
mais : enregistrement par navigateur/OS (registre Windows), processus séparé
à réconcilier avec `main.py`, complexité d'installation. À ne retenir que si
A et C échouent — documenter pourquoi le cas échéant.

## Fichiers concernés

- Prototype jetable : `extension/spike/` (supprimé à la clôture) +
  script d'essai `tests/manual/spike_ext_transport.py` (conservé comme doc
  exécutable, hors suite unittest).
- Ce fichier : section « Décision » complétée.
- `PROJECT_STATE.md` : décision consignée (DEC-PLAN-07).

## Étapes

1. Brancher le squelette T-030 : bouton de test dans le content script qui
   `sendMessage` → SW → `synthesixDispatch`.
2. Script Python : démarrer zendriver avec l'extension (flag T-032 en dur pour
   le spike), lister les targets, attacher le SW, armer le binding, logguer
   les événements reçus.
3. Tester : action depuis 2 pages différentes ; SW endormi 2 min puis action ;
   redémarrage navigateur ; mesurer latences.
4. Rédiger la décision : option retenue, limites, contrats (format du message
   action, ré-armement), plan B.

## Critères d'acceptation

- Démo reproductible : clic sur une page https ⇒ ligne de log Python < 1 s.
- Les 4 points à prouver ont chacun une réponse écrite (oui/non + détail).
- Décision consignée ici + `PROJECT_STATE.md` ; prototype nettoyé.

## Commandes de test

```powershell
.venv\Scripts\python.exe tests\manual\spike_ext_transport.py
```

(manuel, navigateur visible requis)

## Risques

- Chrome peut restreindre l'attache debugger aux targets d'extension selon
  version/flags (`--silent-debugger-extension-api`…) : c'est précisément ce
  que le spike doit trancher — ne pas construire T-034 avant.
- Conclusion « option C » = acceptable ; « option B » = re-planifier T-034
  avec un lot d'installation dédié.
