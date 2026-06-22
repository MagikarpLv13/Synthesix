# AGENTS.md — Règles communes pour les agents IA

## Portée et sources de vérité

Ce fichier s'applique à tout agent IA qui lit, modifie, teste ou documente Synthesix.

Priorité : demande utilisateur → contraintes de sécurité/environnement → `AGENTS.md` → documentation spécialisée → conventions locales.

Lire selon le périmètre :

- `AI_WORKLOG.md` : source de vérité pour claims, verrous, blocages, décisions et comptes rendus IA ;
- `README.md` : architecture, fonctionnement, configuration et commandes ;
- `COLLAB.md`, `docs/CODEX_CLAUDE_WORKPLAN.md` : contraintes et historique de la migration Lit ;
- `docs/UX_REDESIGN.md` : design system et UX ;
- `frontend/README.md` : build et vérification visuelle ;
- `frontend/TASKS.md` : backlog/historique frontend. Pour les travaux actifs, `AI_WORKLOG.md` fait autorité.

## Coordination obligatoire

Toute modification non triviale doit avoir une tâche `AI-YYYYMMDD-NNN` dans `AI_WORKLOG.md` avant l'édition. Sont non triviales les modifications multi-fichiers, comportementales, contractuelles, générant un bundle, ajoutant une dépendance ou touchant un fichier chaud.

### Avant d'écrire

1. Lire les travaux actifs, verrous, blocages et décisions.
2. Exécuter `git branch --show-current` et `git status --short`.
3. Faire `git pull --rebase` si le distant est accessible.
4. Déclarer agent, objectif, fichiers prévus, tests et dépendances.
5. Poser les verrous nécessaires. En travail simultané, commit/push du claim seul.

### Pendant

- Ne pas modifier un fichier verrouillé par un autre agent.
- Étendre le périmètre dans le journal avant de toucher un nouveau fichier chaud.
- Garder des commits petits ; rebaser régulièrement.
- Ne pas effacer l'historique d'une autre IA.
- En cas d'interruption, consigner état, fichiers, tests, risques et prochaine action exacte.

### Fin

- Exécuter les vérifications adaptées.
- Mettre à jour documentation, tâche et verrous.
- Ajouter un compte rendu factuel : changements, fichiers, tests exécutés, tests omis, commit, risques et reste à faire.

Une tâche n'est pas terminée tant que `AI_WORKLOG.md` n'est pas à jour.

## Fichiers chauds

Verrou exclusif obligatoire avant modification :

- `main.py`, `ui.py`, `utils.py`, `theme.css`, `index.html`, `i18n.js`
- `settings.py`, `search_orchestrator.py`
- `investigations/view.py`, `investigations/search_view.py`
- `frontend/package.json`, `frontend/tsconfig.json`, `frontend/build.mjs`
- `frontend/src/index.ts`, `frontend/src/overlay/index.ts`
- `assets/synthesix-ui.js`, `assets/synthesix-overlay.js`

Un verrou doit être précis et aussi court que possible.

## Invariants produit

Synthesix est une application OSINT locale, Python 3.10+, async-first, pilotée par Zendriver/CDP. Elle doit rester lançable par `python main.py` sans serveur ni Node requis pour l'utilisateur final.

Ne jamais casser sans demande explicite et tests dédiés :

- recherche en phrase exacte quand les dorks automatiques sont actifs ;
- isolation des moteurs, retries, timeouts, scoring explicable et rapports ;
- fermeture propre de Zendriver/Chrome ;
- pages locales `file://`, enquêtes, preuves, provenance et exports ZeroNeurone ;
- contrats CDP/JavaScript : `window.name`, `window.synthesixHome`, `window.synthesixPage`, actions, payloads, IDs, événements et attributs `data-*`.

Avant de modifier un contrat, rechercher tous ses producteurs, consommateurs et tests. Toute évolution CDP/overlay exige un test ciblé et un smoke live, ou une mention explicite de l'absence de smoke.

## Architecture

- `main.py` : cycle navigateur, boucle UI et actions CDP.
- `browser_manager.py`, `search_engine.py` : navigateur et comportement moteur commun.
- `google.py`, `bing.py`, `brave.py`, `duckduckgo.py` : logique propre aux moteurs.
- `search_orchestrator.py` : concurrence, retries, scoring et rapports.
- `investigations/`, `analysis/`, `evidence/`, `exports/` : domaine, analyse, preuves et exports.
- `ui.py`, `utils.py`, `theme.css`, `i18n.js` : rendu, thème et traductions.
- `frontend/src/components/` : composants Lit applicatifs.
- `frontend/src/overlay/` : composants injectés sur des pages tierces.
- `assets/synthesix-*.js` : bundles IIFE générés et versionnés.
- `tests/` : suite `unittest`.

Séparer métier, données, navigateur et rendu. Préférer une correction ciblée à une réécriture large.

## Python

- Compatibilité Python 3.10+, annotations de types sur le code modifié.
- Fonctions petites, testables ; préférer `pathlib`, `dataclasses`, `typing`, `logging`.
- Éviter l'état global et les effets de bord implicites.
- Dans l'async : `await asyncio.sleep()`, jamais `time.sleep()`.
- Fermer le navigateur via le gestionnaire prévu ou `await browser.stop()`.
- Isoler les erreurs par moteur.
- Utiliser les migrations pour le schéma ; préserver les données existantes.
- Ne pas changer une API ou un payload sans rechercher tous les consommateurs.

## TypeScript, Lit et CSS

- TypeScript strict ; aucun local/paramètre inutilisé.
- `LitElement`, Shadow DOM, préfixe `sx-`, un composant principal par fichier.
- Enregistrer dans `frontend/src/index.ts` ou `frontend/src/overlay/index.ts`.
- Utiliser les tokens CSS existants. L'overlay ne dépend jamais du CSS de la page hôte.
- Pas de texte utilisateur en dur dans un composant réutilisable : propriétés, attributs, slots ou `i18n.js`.
- Focus visible, clavier, rôles et `aria-label` pour les icônes.
- Préserver événements, attributs réfléchis, slots et API publiques.
- Les pages `file://` chargent le bundle applicatif par script classique, pas `type="module"`.
- Ne pas éditer les bundles minifiés directement.
- Après modification TS : `npm run typecheck`, `npm run build`, puis commit source + bundle.
- Adapter une démo `frontend/demo/` et vérifier clair/sombre, vide, long et dense si l'UI change.

## i18n et UX

- Toute nouvelle chaîne utilisateur doit être traduisible.
- Synchroniser les dictionnaires de `i18n.js`, dont `multilingual` et `additionalTranslations`.
- Exécuter les tests i18n après changement de clé.
- Privilégier densité utile, hiérarchie claire et actions rapides.
- Masquer les champs vides ; fournir `title`/`aria-label` aux icônes seules.
- Ne pas introduire React, Tailwind ou serveur obligatoire sans décision explicite.

## Sécurité et fichiers interdits

Ne jamais afficher ou versionner secrets, cookies, profils navigateur, données d'enquête, bases runtime, captures, archives de preuve ou rapports générés.

Ne pas committer notamment : `.venv/`, `env/`, `node_modules/`, `data/`, `history/`, `*-profile/`, `zendriver-profile/`, `tmp_ui_render/`, `.cache/`, caches Python/tests et couverture.

Valider chemins, URL et entrées externes. Éviter `eval`, `exec`, désérialisation dangereuse et shell construit depuis une entrée. Ne pas contourner les protections SSRF ou le nettoyage des preuves.

## Dépendances et Git

- Préférer standard library et dépendances existantes.
- Justifier toute dépendance et l'ajouter au bon manifeste.
- Pour Zendriver, suivre la procédure du `README.md`.
- Ne pas lancer de formatage global hors périmètre.
- Ne pas écraser des changements utilisateur/agent.
- Interdits sans autorisation : `git reset --hard`, `git clean -fd`, force-push, rebase destructif.
- Inspecter `git diff`, `git diff --staged`, `git status --short`.
- Messages de commit centrés sur le résultat, pas sur l'outil IA.

## Vérifications

Python ciblé :

```powershell
.venv\Scripts\python.exe -m unittest tests.test_<module>
git diff --check
```

Frontend :

```powershell
cd frontend
npm run typecheck
npm run build
cd ..
git diff --check
```

Changement large :

```powershell
cd frontend
npm run typecheck
npm run build
cd ..
.venv\Scripts\python.exe -m unittest discover
git diff --check
```

Utiliser l'équivalent du virtualenv sous Linux/macOS. Ajouter selon le périmètre : `py_compile`, capture Chrome headless, smoke CDP live ou smoke ZeroNeurone.

Ne jamais déclarer un test réussi sans l'avoir exécuté.

## Definition of Done

- objectif réalisé sans élargissement caché ;
- invariants et contrats préservés ;
- tests adaptés exécutés et résultats rapportés ;
- bundles régénérés si nécessaire ;
- vérification visuelle/CDP faite ou explicitement omise ;
- documentation à jour ;
- `git diff --check` propre ;
- aucun fichier sensible/temporaire staged ;
- `AI_WORKLOG.md` clôturé sans verrou actif ;
- réponse finale : résumé, fichiers, tests, limites et reste à faire.
