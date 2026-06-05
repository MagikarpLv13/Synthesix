# Plan d'optimisation

Etat au 2026-06-05.

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
- L'orchestration multi-moteur est extraite dans `search_orchestrator.py`.
- `main.py` reste concentre sur le navigateur, l'UI, la home et l'ouverture du rapport.
- L'agregation multi-moteur est couverte par des tests unitaires avec moteurs factices async.
- Les erreurs applicatives sont normalisees dans `exceptions.py`.
- Les echecs moteur, session navigateur et challenge anti-robot Brave remontent avec des types explicites.
- Les recherches moteur sont encadrees par un timeout global configurable.
- Les erreurs transitoires moteur sont retryees de maniere limitee et configurable.
- Les rapports et l'historique HTML runtime sont generes dans `history/` par defaut.

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
  - `SYNTHESIX_HISTORY_REPORT_PATH`
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
  - `SYNTHESIX_ENGINE_SEARCH_TIMEOUT`
  - `SYNTHESIX_ENGINE_RETRY_ATTEMPTS`
  - `SYNTHESIX_ENGINE_RETRY_DELAY`
  - `SYNTHESIX_ENGINE_RETRY_BACKOFF`

Tests :

- Tests unitaires sur les valeurs par defaut : fait.
- Tests unitaires sur les overrides d'environnement : fait.

### P1 - Extraire l'orchestration de recherche

Objectif : reduire la taille et la responsabilite de `main.py`.

- Statut : termine.
- Module ajoute : `search_orchestrator.py`.
- Extrait :
  - lancement parallele des moteurs actifs
  - isolation des erreurs moteur individuelles
  - validation des colonnes de resultats
  - fusion des resultats
  - scoring
  - deduplication par lien avec fusion des sources
  - generation du rapport et de l'historique
- `main.py` conserve :
  - demarrage du navigateur
  - ouverture de la home
  - lecture des actions UI
  - parsing smart/avance de la requete
  - ouverture de l'onglet rapport
  - fermeture propre des ressources
- Les factories de moteurs sont injectables pour permettre des tests sans navigateur.

Contraintes respectees :

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

- Tests unitaires de l'agregation multi-moteur avec moteurs factices async : fait.
- Test sur la conservation de la requete exacte : fait.
- Test moteur en erreur sans abandonner les resultats des autres moteurs : fait.

### P1 - Normaliser les erreurs moteur/CDP

Objectif : avoir des logs et des comportements coherents quand un moteur echoue.

- Statut : termine.
- Module ajoute : `exceptions.py`.
- Exceptions applicatives introduites :
  - `SynthesixError`
  - `SearchEngineError`
  - `BrowserSessionError`
  - `RobotChallengeError`
- Transformations ajoutees :
  - navigateur absent ou navigation CDP echouee -> `BrowserSessionError`
  - contenu page illisible -> `BrowserSessionError`
  - parsing moteur echoue -> `SearchEngineError`
  - exception brute moteur -> `SearchEngineError` dans l'orchestrateur
  - challenge anti-robot Brave non resolu -> `RobotChallengeError`
- Un moteur en erreur ne bloque pas les resultats des autres moteurs.
- Si tous les moteurs lances echouent, l'orchestrateur remonte une erreur applicative au lieu de generer un rapport trompeur.

Tests :

- Simuler un moteur en erreur et verifier que les autres resultats restent exploites : fait.
- Verifier que les erreurs sont loggees avec le nom du moteur : fait.
- Verifier que les exceptions brutes moteur sont normalisees : fait.
- Verifier que l'echec de navigation devient `BrowserSessionError` : fait.
- Verifier que l'anti-robot Brave non resolu devient `RobotChallengeError` : fait.

### P2 - Renforcer les timeouts et retries

Objectif : limiter les blocages navigateur/reseau.

- Statut : termine pour la premiere passe.
- Ajoute dans `SearchOrchestrator` :
  - timeout global par moteur avec `asyncio.wait_for`
  - retry limite sur erreurs transitoires
  - backoff configurable entre retries
- Erreurs retryees :
  - `BrowserSessionError`
  - `TimeoutError`
  - `ConnectionError`
  - `OSError`
  - `SearchEngineError` issue d'un timeout ou d'un chargement incomplet
- Erreurs non retryees :
  - `RobotChallengeError`
  - erreurs de parsing
  - erreurs logiques non classees temporaires
- Configuration ajoutee :
  - `SYNTHESIX_ENGINE_SEARCH_TIMEOUT`
  - `SYNTHESIX_ENGINE_RETRY_ATTEMPTS`
  - `SYNTHESIX_ENGINE_RETRY_DELAY`
  - `SYNTHESIX_ENGINE_RETRY_BACKOFF`

Tests :

- Tests unitaires sur la politique de retry : fait.
- Tests unitaires sur le non-retry anti-robot : fait.
- Tests unitaires sur le timeout moteur global : fait.
- Smoke test optionnel avec Chrome/Chromium local : a lancer avant release si les moteurs sont modifies.

### P2 - Structurer les rapports et l'historique

Objectif : eviter que les artefacts runtime polluent la racine du projet.

- Statut : termine.
- Garder `index.html`, `theme.css` et `theme.js` a la racine : fait.
- Generer l'historique HTML dans `history/history.html` par defaut : fait.
- Generer les resultats dans `history/` : fait.
- Garder les captures anti-robot dans `history/robot_challenges/` : fait.
- Ne pas committer les rapports HTML generes : fait via `.gitignore`.
- Override disponible : `SYNTHESIX_HISTORY_REPORT_PATH`.

Tests :

- Tests unitaires sur les chemins generes : fait.
- Tests unitaires sur l'echappement HTML des rapports : fait.

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
3. Extraire l'orchestration multi-moteur hors de `main.py`. Fait.
4. Ajouter les exceptions applicatives. Fait.
5. Ajouter les timeouts/retries configurables. Fait.
6. Ajouter les tests unitaires des nouveaux services. Fait pour l'orchestration, les erreurs et les retries.
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
venv\Scripts\python.exe -m py_compile main.py utils.py scoring.py google.py bing.py brave.py duckduckgo.py browser_manager.py search_engine.py settings.py search_orchestrator.py exceptions.py
venv\Scripts\python.exe -m unittest discover
git diff --check
```
