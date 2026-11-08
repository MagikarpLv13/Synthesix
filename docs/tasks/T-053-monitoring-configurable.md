# T-053 — Configuration automatique ou personnalisée des moniteurs

- **Statut** : done (2026-07-16)
- **Priorité** : P1
- **Effort** : moyen
- **Outil recommandé** : Codex
- **Dépendances** : T-052

## Objectif

Étendre le contrat des moniteurs de page afin que Synthesix puisse choisir un
profil automatiquement selon l'URL, tout en laissant l'analyste sélectionner
les métriques, les sélecteurs, la fréquence et l'état actif ou suspendu.

## Contexte

Le monitoring existant ne conserve que la référence des archives comparées.
La future sonde périodique a besoin d'une configuration persistante avant de
pouvoir ouvrir une page et produire une observation légère.

## Fichiers concernés

- `investigations/monitoring.py`
- `investigations/models.py`
- `investigations/migrations.py`
- `investigations/repository.py`
- `investigations/service.py`
- `tests/test_monitoring.py`
- `tests/test_investigations.py`

## Étapes

1. Définir les modes `automatic` et `custom`.
2. Définir les profils générique, Instagram, TikTok, Facebook, X et YouTube.
3. Valider métriques, sélecteurs CSS, fréquence et état activé.
4. Ajouter une migration additive aux moniteurs existants.
5. Exposer création et mise à jour de la configuration dans le service.
6. Préserver le comportement idempotent de `create_page_monitor`.

## Critères d'acceptation

- Une URL sociale reçoit le profil correspondant en mode automatique.
- Une page inconnue reçoit `generic_page`.
- L'analyste peut conserver le profil automatique et choisir les métriques.
- Le mode personnalisé accepte des métriques et sélecteurs bornés et validés.
- Un moniteur existant migre avec des valeurs génériques sûres.
- Désactiver un moniteur le place en statut `paused`.

## Commandes de test

```powershell
.venv\Scripts\python.exe -m py_compile investigations\monitoring.py investigations\models.py investigations\migrations.py investigations\repository.py investigations\service.py tests\test_monitoring.py tests\test_investigations.py
.venv\Scripts\python.exe -m unittest tests.test_monitoring
.venv\Scripts\python.exe -m unittest tests.test_investigations
git diff --check
```

## Risques

- Les profils indiquent le contrat attendu, pas encore la disponibilité réelle
  d'une métrique sur une plateforme.
- Les sélecteurs personnalisés seront exécutés uniquement par T-054, après
  validation dans le contexte de la page.
- Les moniteurs créés avant la migration restent génériques jusqu'à leur
  prochaine reconfiguration.

## Résultat

Le contrat est livré avec migration v18, détection automatique sensible au type
de chemin (profil versus post/vidéo), configuration personnalisée validée,
persistance de la fréquence et pause/reprise. Les futures observations et leur
exécution périodique restent volontairement dans T-054 et T-055.
