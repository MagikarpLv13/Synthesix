# AGENTS.md

## Objectif

Maintenir Synthesix comme une application Python robuste, lisible et testable, sans casser ses recherches exactes, son approche asynchrone Zendriver/CDP ni ses workflows d'enquête.

## Style de travail

- Comprendre l'objectif et inspecter uniquement les fichiers concernés avant de modifier.
- Pour une tâche complexe, annoncer un plan bref; sinon agir directement.
- Faire des changements minimaux, ciblés et cohérents avec l'architecture existante.
- Ne pas réécrire massivement, inventer d'API ou modifier un comportement sans nécessité.
- Ne pas ajouter de dépendance sans justification.

## Gestion du contexte et coût en tokens

- Répondre avec concision; détailler seulement sur demande ou pour signaler un risque.
- Préférer un diff ou un résumé à la reproduction complète d'un fichier.
- Ne pas relire les mêmes fichiers; dans les gros fichiers, cibler les sections utiles.
- Ignorer `.venv`, `env`, `.git`, `__pycache__`, `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `dist`, `build`, `node_modules`, `coverage`, `.coverage` et `htmlcov`.
- Ne mentionner une hypothèse que si elle influence la solution.

## Standards Python

- Respecter la compatibilité Python 3.10+ du projet.
- Ajouter des annotations de types au code nouveau ou modifié.
- Écrire des fonctions petites, explicites et testables, avec une gestion claire des erreurs.
- Préférer `pathlib`, `dataclasses`, `typing` et `logging`; éviter l'état global inutile.
- Respecter PEP 8. Garder le code navigateur asynchrone: `await asyncio.sleep()`, jamais `time.sleep()`.
- Fermer Zendriver proprement via le gestionnaire du navigateur ou `await browser.stop()`.

## Structure de projet

- Respecter les responsabilités décrites dans `README.md`.
- Garder la logique CDP dans `browser_manager.py`/`search_engine.py`, l'orchestration dans `search_orchestrator.py`, les moteurs dans leurs modules et le domaine d'enquête dans `investigations/` et `evidence/`.
- Séparer logique métier, rendu HTML et automatisation navigateur.

## Qualité, lint et formatage

- Corriger la cause racine et préserver la lisibilité avant toute micro-optimisation.
- Vérifier les cas limites et la compatibilité des moteurs.
- Utiliser Ruff s'il est ajouté au projet; ne pas l'imposer sans configuration.
- Exécuter `git diff --check` avant de terminer.

## Tests

- Le projet utilise `unittest`; ajouter ou adapter les tests lorsqu'un comportement change.
- Exécuter d'abord les tests ciblés, puis `.venv\Scripts\python.exe -m unittest discover`.
- Pour Linux/macOS, utiliser l'interpréteur équivalent du virtualenv.
- Ne jamais déclarer un test réussi s'il n'a pas été exécuté; signaler clairement tout test omis et pourquoi.
- Préserver notamment la recherche en phrase exacte, l'isolation des moteurs et la fermeture propre du navigateur.

## Sécurité

- Ne jamais afficher, déplacer, modifier ou versionner des secrets, profils, cookies ou données d'enquête.
- Ne pas coder en dur de clé, token, mot de passe ou chemin utilisateur sensible.
- Documenter les variables dans `.env.example` si nécessaire.
- Valider toute entrée utilisée pour les fichiers, le réseau, les commandes ou des données externes.
- Éviter `eval`, `exec`, la désérialisation dangereuse et les commandes shell construites depuis une entrée.

## Gestion des dépendances

- Préférer la bibliothèque standard; justifier toute nouvelle dépendance.
- Mettre à jour `requirements.txt` de façon cohérente et ne jamais installer globalement.
- Pour Zendriver, suivre la procédure de mise à jour et le smoke test décrits dans `README.md`.

## Documentation

- Mettre à jour `README.md` lorsqu'une commande, une configuration ou un comportement utilisateur change.
- Documenter les prérequis Chrome/Chromium et les variables d'environnement utiles.
- Garder les commentaires courts et réservés aux choix non évidents.

## Refactoring

- Procéder par petits lots vérifiables sans casser l'API existante.
- Conserver les conventions locales et éviter les abstractions sans gain concret.
- Isoler les erreurs d'un moteur afin qu'elles ne bloquent pas les autres.
- Préférer une correction de parseur ciblée lorsqu'un moteur change son HTML.

## Commandes utiles

```powershell
.venv\Scripts\python.exe -m unittest discover
git diff --check
python main.py
```

Consulter `README.md` pour la compilation complète, le profiling et le smoke test navigateur.

## Réponse attendue de Codex

Terminer par un résumé concis indiquant les changements, les fichiers modifiés, les tests réellement exécutés et les points d'attention restants. Éviter toute explication excessive.
