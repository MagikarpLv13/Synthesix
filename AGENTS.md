# AGENTS.md — Règles communes pour les agents IA

## 1. Portée et sources de vérité

Ce fichier s’applique à tout agent IA qui lit, modifie, teste ou documente Synthesix.

Ordre de priorité :

1. demande explicite de l’utilisateur ;
2. contraintes de sécurité et d’environnement ;
3. `AGENTS.md` ;
4. documentation spécialisée ;
5. conventions locales du code concerné.

Documents de référence :

* `AI_WORKLOG.md` : tâches actives, verrous, blocages, décisions et comptes rendus ;
* `README.md` : installation, architecture générale et commandes ;
* `docs/UX_REDESIGN.md` : design system et règles UX ;
* `frontend/README.md` : build et vérifications frontend ;
* `frontend/TASKS.md` : backlog et historique frontend ;
* `COLLAB.md` et `docs/CODEX_CLAUDE_WORKPLAN.md` : historique de collaboration et migration Lit.

Pour les travaux actifs, `AI_WORKLOG.md` fait autorité.

## 2. Coordination entre agents

Toute modification non triviale doit être déclarée dans `AI_WORKLOG.md` avant l’édition.

Une modification est considérée comme non triviale lorsqu’elle :

* touche plusieurs fichiers ;
* change un comportement ou un contrat ;
* modifie un fichier partagé ou sensible ;
* ajoute une dépendance ;
* génère ou modifie un bundle ;
* nécessite une migration ou une mise à jour de données.

### Avant de modifier

1. Lire les tâches actives, verrous, blocages et décisions.
2. Exécuter :

```powershell
git branch --show-current
git status --short
```

3. Déclarer dans `AI_WORKLOG.md` :

   * l’agent ;
   * l’objectif ;
   * les fichiers prévus ;
   * les tests prévus ;
   * les dépendances ou risques connus.
4. Poser les verrous nécessaires.
5. En travail parallèle, rendre le claim visible aux autres agents avant de modifier les fichiers concernés.

Synchroniser avec le distant uniquement si la branche est propre, que le distant est accessible et que l’opération ne risque pas d’écraser un travail local.

### Pendant la tâche

* Ne pas modifier un fichier verrouillé par un autre agent.
* Mettre à jour le périmètre avant de toucher un nouveau fichier partagé.
* Garder les modifications et commits ciblés.
* Ne pas mélanger une correction fonctionnelle avec un nettoyage global.
* Ne jamais effacer ou réécrire le travail d’un autre agent.
* En cas d’interruption, documenter :

  * l’état actuel ;
  * les fichiers modifiés ;
  * les tests exécutés ;
  * les risques ;
  * la prochaine action exacte.

### À la fin

* Exécuter les vérifications adaptées.
* Mettre à jour la documentation concernée.
* Retirer les verrous.
* Clôturer la tâche dans `AI_WORKLOG.md`.
* Indiquer les tests exécutés et ceux qui ne l’ont pas été.

Une tâche n’est pas terminée tant que son suivi n’est pas à jour.

## 3. Fichiers partagés sensibles

Un verrou exclusif est requis avant de modifier :

* `main.py`
* `ui.py`
* `utils.py`
* `theme.css`
* `index.html`
* `i18n.js`
* `settings.py`
* `search_orchestrator.py`
* `investigations/view.py`
* `investigations/search_view.py`
* `frontend/package.json`
* `frontend/tsconfig.json`
* `frontend/build.mjs`
* `frontend/src/index.ts`
* `frontend/src/overlay/index.ts`
* `assets/synthesix-ui.js`
* `assets/synthesix-overlay.js`
* `graphify-out/graph.json`
* `graphify-out/GRAPH_REPORT.md`

Les verrous doivent être précis et conservés uniquement pendant la durée nécessaire.

## 4. Invariants produit

Synthesix est une application OSINT locale :

* compatible Python 3.10+ ;
* async-first ;
* pilotée par Zendriver et Chrome DevTools Protocol ;
* lançable avec `python main.py` ;
* utilisable sans serveur ni environnement Node par l’utilisateur final.

Ne pas casser sans demande explicite et tests adaptés :

* la recherche en phrase exacte avec les dorks automatiques ;
* l’isolation des moteurs de recherche ;
* les retries, timeouts et mécanismes de scoring ;
* la fermeture propre de Zendriver et Chrome ;
* les pages locales chargées en `file://` ;
* les enquêtes, preuves, provenances et exports ZeroNeurone ;
* les contrats entre Python, CDP et JavaScript.

## 5. Contrats publics

Avant de modifier un élément contractuel, rechercher ses producteurs, consommateurs et tests.

Cela concerne notamment :

* API Python ;
* payloads ;
* schémas de données ;
* actions CDP ;
* `window.name` ;
* `window.synthesixHome` ;
* `window.synthesixPage` ;
* IDs et attributs `data-*` ;
* événements Lit ;
* propriétés réfléchies ;
* slots ;
* API publiques des composants.

Toute évolution fonctionnelle du CDP ou de l’overlay doit avoir :

* un test ciblé ;
* un smoke test réel lorsque possible ;
* ou une mention explicite indiquant pourquoi ce smoke test n’a pas été exécuté.

## 6. Architecture générale

Respecter les frontières suivantes :

* backend Python asynchrone pour le métier et le pilotage navigateur ;
* moteurs de recherche isolés derrière des interfaces communes ;
* orchestration séparée du scraping propre à chaque moteur ;
* séparation entre enquêtes, analyse, preuves et exports ;
* interface Lit compilée en bundles IIFE ;
* composants applicatifs séparés des composants injectés sur les pages tierces ;
* tests Python basés sur `unittest`.

Préférer une correction ciblée à une réécriture large.

## 7. Python

* Maintenir la compatibilité Python 3.10+.
* Ajouter des annotations de types au code modifié lorsque pertinent.
* Préférer des fonctions petites et testables.
* Utiliser de préférence `pathlib`, `dataclasses`, `typing` et `logging`.
* Limiter l’état global et les effets de bord implicites.
* Dans du code asynchrone, utiliser `await asyncio.sleep()`, jamais `time.sleep()`.
* Fermer le navigateur avec le mécanisme prévu ou `await browser.stop()`.
* Isoler les erreurs par moteur.
* Utiliser les migrations pour toute évolution de schéma.
* Préserver les données existantes.

## 8. TypeScript, Lit et CSS

* Conserver TypeScript en mode strict.
* Ne pas laisser de variables ou paramètres inutilisés.
* Utiliser `LitElement`, le Shadow DOM et le préfixe `sx-`.
* Garder un composant principal par fichier.
* Enregistrer les composants dans :

  * `frontend/src/index.ts` ;
  * ou `frontend/src/overlay/index.ts`.
* Utiliser les tokens CSS existants.
* L’overlay ne doit pas dépendre du CSS de la page hôte.
* Préserver les événements, propriétés, attributs et slots publics.
* Fournir un focus visible et les attributs d’accessibilité nécessaires.
* Les icônes seules doivent avoir un `title` ou un `aria-label`.
* Ne pas éditer directement les bundles minifiés.
* Les pages `file://` doivent charger les bundles par script classique, sans `type="module"`.

Après toute modification TypeScript :

```powershell
cd frontend
npm run typecheck
npm run build
cd ..
```

Committer ensemble les sources et les bundles générés.

En cas de changement visuel, vérifier au minimum :

* thème clair ;
* thème sombre ;
* état vide ;
* texte long ;
* affichage dense ou étroit.

## 9. i18n et UX

* Toute nouvelle chaîne visible doit être traduisible.
* Ne pas placer de texte utilisateur en dur dans un composant réutilisable.
* Synchroniser les dictionnaires de `i18n.js`, notamment `multilingual` et `additionalTranslations`.
* Exécuter les tests i18n après toute modification de clé.
* Masquer les champs sans valeur.
* Privilégier une hiérarchie claire, une densité utile et des actions accessibles.
* Ne pas introduire React, Tailwind ou un serveur obligatoire sans décision explicite.

## 10. Sécurité et données locales

Ne jamais inclure dans un commit, une réponse externe ou un journal partagé :

* secrets ou clés API ;
* cookies ;
* profils navigateur ;
* données d’enquête ;
* preuves ou captures ;
* bases runtime ;
* rapports générés ;
* informations personnelles ou client.

La lecture locale de ces données est autorisée uniquement lorsque la tâche l’exige.

Ne pas versionner notamment :

* `.venv/`
* `env/`
* `node_modules/`
* `data/`
* `history/`
* `*-profile/`
* `zendriver-profile/`
* `tmp_ui_render/`
* `.cache/`
* caches Python et résultats de couverture.

Valider les chemins, URL et entrées externes.

Éviter :

* `eval` ;
* `exec` ;
* la désérialisation non sûre ;
* les commandes shell construites depuis une entrée utilisateur ;
* le contournement des protections SSRF ;
* le contournement du nettoyage des preuves.

## 11. Dépendances et Git

* Préférer la bibliothèque standard et les dépendances existantes.
* Justifier toute nouvelle dépendance.
* Ajouter la dépendance dans le manifeste approprié.
* Pour Zendriver, suivre la procédure du `README.md`.
* Ne pas lancer de formatage global hors périmètre.
* Ne pas écraser les changements locaux d’un utilisateur ou d’un autre agent.

Interdits sans autorisation explicite :

```text
git reset --hard
git clean -fd
git push --force
rebase destructif
```

Avant de clôturer :

```powershell
git diff
git diff --staged
git status --short
git diff --check
```

Les messages de commit doivent décrire le résultat, pas l’outil IA utilisé.

## 12. Vérifications

### Python ciblé

```powershell
.venv\Scripts\python.exe -m unittest tests.test_<module>
git diff --check
```

### Frontend

```powershell
cd frontend
npm run typecheck
npm run build
cd ..
git diff --check
```

### Changement transversal

```powershell
cd frontend
npm run typecheck
npm run build
cd ..
.venv\Scripts\python.exe -m unittest discover
git diff --check
```

Sous Linux ou macOS, utiliser l’équivalent du virtualenv.

Ajouter selon le périmètre :

* `py_compile` ;
* test i18n ;
* capture Chrome headless ;
* smoke test CDP ;
* smoke test ZeroNeurone.

Ne jamais déclarer un test réussi sans l’avoir exécuté.

## 13. Navigation avec Graphify

Utiliser Graphify pour les questions transversales d’architecture, de dépendances ou de localisation de code inconnue :

```powershell
graphify query "<question précise>"
```

Règles :

* utiliser le résultat pour sélectionner les fichiers à lire ;
* toujours vérifier le code source avant de modifier ;
* ne pas considérer le graphe comme une preuve du comportement actuel ;
* ne pas lire tout `GRAPH_REPORT.md` pour une question locale ;
* ne pas utiliser Graphify pour connaître l’état des tâches ;
* lire directement `AI_WORKLOG.md` pour les claims, verrous et décisions ;
* vérifier la mise à jour du graphe après un changement architectural important.

## 14. Clôture et réponse finale

Avant de terminer, vérifier que :

* l’objectif demandé est réalisé ;
* les contrats et invariants sont préservés ;
* les tests adaptés ont été exécutés ;
* les bundles ont été régénérés si nécessaire ;
* les vérifications visuelles ou CDP ont été faites ou explicitement omises ;
* aucun fichier sensible ou temporaire n’est staged ;
* `git diff --check` est propre ;
* les verrous ont été retirés ;
* `AI_WORKLOG.md` est à jour.

La réponse finale doit contenir uniquement :

* le résultat ;
* les fichiers modifiés ;
* les tests réellement exécutés ;
* les vérifications non exécutées ;
* les limites ou prochaines actions nécessaires.
