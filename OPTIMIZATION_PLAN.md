# Plan d'optimisation

## 1. Stabilisation Zendriver/CDP

- Maintenir `zendriver` a jour et verifier les changements d'API apres chaque mise a jour.
- Version actuelle testee localement: `zendriver==0.15.3`.
- Ajouter un smoke test navigateur court pour verifier `uc.start()`, `browser.get()`, `tab.get_content()` et `browser.stop()`.
- Surveiller les changements de gestion des profils, cookies, timeouts et fermeture d'onglets.

## 2. Configuration

- Centraliser les chemins runtime (`history/`, `zendriver-profile/`), les moteurs actifs et les timeouts.
- Prevoir une configuration par variables d'environnement sans secrets hardcodes.

## 3. Orchestration

- Extraire l'orchestration de recherche hors de `main.py`.
- Garder les moteurs responsables seulement de la navigation, du parsing et de la pagination.

## 4. Robustesse

- Remplacer les `print` restants par `logging`.
- Normaliser les exceptions moteur/CDP.
- Ajouter des retries limites sur les erreurs reseau temporaires.

## 5. Tests

- Etendre les tests unitaires sur les parsers avec snapshots HTML.
- Ajouter des doubles Zendriver pour tester les flux async sans navigateur.
- Ajouter un smoke test live optionnel pour Chrome/Chromium.

## 6. Documentation

- Documenter les prerequis Chrome/Chromium.
- Documenter le profil navigateur, l'historique et les rapports generes.
- Documenter la procedure de mise a jour Zendriver.
