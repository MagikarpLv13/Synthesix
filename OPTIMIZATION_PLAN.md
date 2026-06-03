# Plan d'optimisation

Etat au 2026-06-03.

## 1. Etat actuel

### Termine recemment

- La configuration runtime est centralisee dans `settings.py`.
- Les chemins `history/`, `history.html`, `history/robot_challenges/` et `zendriver-profile/` sont configurables.
- Les timeouts principaux navigateur/Brave et les moteurs actifs par defaut sont configurables par variables d'environnement.
- `zendriver` est verrouille sur `zendriver==0.15.3`.
- Les moteurs Google, Bing, Brave et DuckDuckGo sont disponibles.
- DuckDuckGo utilise des parametres orientes recherche pure, sans blocs IA/suggestions quand le moteur les accepte.
- Les requetes simples restent protegees par des guillemets via `smart_parse()`.
- Le scoring respecte les expressions exactes entre guillemets.
- La detection anti-robot Brave capture les pages de challenge dans `history/robot_challenges/`.
- La home, l'historique et les resultats utilisent un theme commun avec mode clair/sombre.
- Les captures HTML de test racine ont ete supprimees du depot.

### A conserver comme contraintes

- API async-first : ne pas introduire de code bloquant dans les flux navigateur.
- Pas de `time.sleep()` dans du code async ; utiliser `await asyncio.sleep()`.
- Fermeture propre du navigateur avec `await browser.stop()` ou equivalent.
- Pas de secrets hardcodes.
- Captures HTML uniquement en diagnostic ponctuel, pas comme fixtures permanentes a la racine.

## 2. Priorites

### P0 - Stabiliser la configuration runtime

Objectif : eviter que les chemins, timeouts et options moteur soient disperses.

- Statut : termine.
- Module ajoute : `settings.py`.
- Centralise :
  - `history/`
  - `history/robot_challenges/`
  - `zendriver-profile/`
  - timeouts navigateur
  - delais moteur Brave
  - moteurs actives par defaut
- Overrides disponibles via variables d'environnement :
  - `SYNTHESIX_BASE_DIR`
  - `SYNTHESIX_HISTORY_DIR`
  - `SYNTHESIX_BROWSER_PROFILE_DIR`
  - `SYNTHESIX_DEFAULT_ENGINES`
  - `SYNTHESIX_HISTORY_LIMIT`
  - `SYNTHESIX_DEFAULT_MAX_RESULTS`
  - `SYNTHESIX_HOME_POLL_INTERVAL`
  - `SYNTHESIX_EMPTY_TABS_GRACE_SECONDS`
  - `SYNTHESIX_PAGE_LOAD_TIMEOUT`
  - `SYNTHESIX_PAGE_LOAD_INTERVAL`
  - `SYNTHESIX_BRAVE_RESULTS_TIMEOUT`
  - `SYNTHESIX_BRAVE_RESULTS_INTERVAL`
  - `SYNTHESIX_BRAVE_ROBOT_FIND_TIMEOUT`

Tests :

- Tests unitaires sur les valeurs par defaut : fait.
- Tests unitaires sur les overrides d'environnement : fait.

### P1 - Extraire l'orchestration de recherche

Objectif : reduire la taille et la responsabilite de `main.py`.

- Extraire la boucle de recherche dans un service dedie, par exemple `search_orchestrator.py`.
- Garder `main.py` responsable de :
  - demarrer le navigateur
  - ouvrir la home
  - relier l'UI au service
  - fermer proprement les ressources
- Garder les moteurs responsables de :
  - construire l'URL
  - naviguer
  - parser les resultats
  - remonter les erreurs moteur

Tests :

- Tests unitaires de l'agregation multi-moteur avec moteurs factices async.
- Test sur la conservation de la requete exacte.

### P1 - Normaliser les erreurs moteur/CDP

Objectif : avoir des logs et des comportements coherents quand un moteur echoue.

- Introduire quelques exceptions applicatives simples :
  - `SearchEngineError`
  - `BrowserSessionError`
  - `RobotChallengeError`
- Transformer les exceptions Zendriver/CDP utiles en erreurs explicites.
- Ne pas faire echouer toute la recherche si un seul moteur tombe, sauf si aucun moteur ne repond.

Tests :

- Simuler un moteur en erreur et verifier que les autres resultats restent exploites.
- Verifier que les erreurs sont loggees avec le nom du moteur.

### P2 - Renforcer les timeouts et retries

Objectif : limiter les blocages navigateur/reseau.

- Encadrer les actions navigateur critiques avec des timeouts explicites.
- Ajouter des retries limites uniquement sur erreurs temporaires.
- Eviter les retries sur anti-robot, parsing invalide ou erreur logique.
- Rendre les timeouts configurables.

Tests :

- Tests unitaires sur la politique de retry.
- Smoke test optionnel avec Chrome/Chromium local.

### P2 - Structurer les rapports et l'historique

Objectif : eviter que les artefacts runtime polluent la racine du projet.

- Garder `index.html`, `theme.css` et `theme.js` a la racine.
- Generer `history.html` a la racine uniquement au runtime.
- Generer les resultats dans `history/`.
- Garder les captures anti-robot dans `history/robot_challenges/`.
- Ne pas committer les rapports HTML generes.

Tests :

- Tests unitaires sur les chemins generes.
- Tests unitaires sur l'echappement HTML des rapports.

### P3 - Documentation minimale

Objectif : rendre le projet plus facile a lancer et maintenir.

- Documenter les prerequis Chrome/Chromium.
- Documenter l'installation de `zendriver`.
- Documenter les moteurs disponibles et leurs limites.
- Documenter les artefacts runtime ignores par git.
- Documenter la procedure de mise a jour Zendriver :
  - bump version
  - smoke test navigateur
  - test moteurs
  - verification fermeture propre

## 3. Ordre d'execution recommande

1. Ajouter `settings.py` avec chemins/timeouts/moteurs par defaut. Fait.
2. Adapter `utils.py`, `main.py` et les moteurs pour utiliser cette configuration. Fait.
3. Extraire l'orchestration multi-moteur hors de `main.py`.
4. Ajouter les exceptions applicatives.
5. Ajouter les timeouts/retries configurables.
6. Ajouter les tests unitaires des nouveaux services.
7. Mettre a jour le README avec prerequis, lancement, artefacts et mise a jour Zendriver.

## 4. Regles de refactoring

- Faire des petits commits testables.
- Ne pas changer l'API utilisateur sans raison.
- Ne pas modifier la logique de scoring sans test explicite.
- Ne pas supprimer la recherche exacte entre guillemets.
- Ne pas ajouter de dependance lourde pour un besoin simple.
- Garder l'approche async partout ou Zendriver intervient.

## 5. Commandes de verification

```powershell
venv\Scripts\python.exe -m py_compile main.py utils.py scoring.py google.py bing.py brave.py duckduckgo.py browser_manager.py search_engine.py settings.py
venv\Scripts\python.exe -m unittest discover
git diff --check
```
