# T-040 — Navigateur de recherche séparé

- **Statut** : todo
- **Priorité** : P1 · **Effort** : moyen-élevé
- **Outil recommandé** : Claude
- **Dépendances** : T-010, T-011 (recherche annulable) ; T-014 utile mais pas
  bloquant

## Objectif

Isoler la recherche automatisée dans une seconde instance navigateur (profil
`search-profile/`) : plus aucun tab moteur dans la fenêtre de l'utilisateur,
plus de vol de focus, plus de contamination cookies entre moteurs et
navigation d'enquête.

## Contexte

Aujourd'hui une seule instance visible sert tout (`HeadlessBrowserManager`,
`browser_manager.py` ; headless désactivé car Brave le détecte,
`browser_manager.py:358-362`). Les moteurs ouvrent leurs tabs dans la fenêtre
de l'utilisateur (`search_engine.py:142`), déposent leurs cookies dans
`zendriver-profile/`, et les challenges anti-robot se résolvent dans cette
même fenêtre. Décision DEC-PLAN-06.

Contrainte : headless reste exclu. La 2e instance est visible mais discrète :
fenêtre séparée positionnée/réduite (`--window-position`, `--window-size`),
amenée au premier plan **uniquement** pour une résolution manuelle de
challenge (les `bring_to_front` des `robot_check` gardent alors tout leur
sens et ciblent la bonne fenêtre).

## Fichiers concernés

- `browser_manager.py` : factorisation — une classe/fabrique paramétrée
  (profil, home/bookmark ou non, flags fenêtre) ; instance « user » inchangée,
  nouvelle instance « search » sans bookmark ni home.
- `settings.py` : `search_profile_dir` (`SYNTHESIX_SEARCH_PROFILE_DIR`,
  défaut `search-profile/`), `SYNTHESIX_SEARCH_BROWSER=shared|separate`
  (défaut `separate` après validation, `shared` = comportement actuel).
- `main.py` : démarrage paresseux de l'instance recherche (au premier
  search, pas au boot — démarrage app inchangé), arrêt propre au quit,
  `perform_search` reçoit le browser de recherche.
- `.gitignore` : `search-profile/` (règle AGENTS.md §10 — vérifier le motif
  `*-profile/` existant).
- `tests/test_browser_manager.py`, `tests/test_main.py`.

## Étapes

1. Factoriser la création (config zendriver) sans changer l'instance user.
2. Instance recherche : lancement paresseux + réutilisation entre recherches
   (pas de start/stop par recherche : coût de démarrage ~1-3 s) ; watchdog —
   si elle a crashé, la relancer au search suivant.
3. Router `perform_search`/retries vers cette instance ; challenges :
   `bring_to_front` remonte la fenêtre de recherche (comportement existant,
   maintenant sans gêner la fenêtre principale).
4. Nettoyage : `clear_browser_data` (home) nettoie les DEUX profils ; refuser
   pendant une recherche active (garde T-011).
5. Arrêt : quit ⇒ stop des deux instances (ordre : recherche d'abord).
6. Smoke : recherche complète pendant que l'utilisateur navigue dans la
   fenêtre principale — zéro interférence de focus ; challenge simulé ⇒ la
   fenêtre recherche remonte.

## Critères d'acceptation

- Pendant une recherche : aucun tab créé dans la fenêtre user, aucun
  changement de focus non sollicité.
- Cookies moteurs absents de `zendriver-profile/` après recherche (vérifier
  sur un profil frais).
- Mode `shared` restaure exactement l'existant.
- Quit propre : aucun process Chrome orphelin (vérifier le gestionnaire de
  tâches après quit).

## Commandes de test

```powershell
.venv\Scripts\python.exe -m unittest tests.test_browser_manager tests.test_main
```

Smoke réel obligatoire (scénarios ci-dessus), consigné.

## Risques

- Deux Chrome = ~300-500 Mo de RAM en plus pendant les recherches : assumé
  (lancement paresseux + option de fermeture après N minutes d'inactivité si
  besoin, hors périmètre initial).
- Profil de recherche neuf = moins de « karma » cookies face aux moteurs :
  à surveiller sur les taux de challenge ; le profil est persistant, il se
  construit à l'usage.
- Empreinte de la fenêtre réduite (viewport minuscule) : garder une taille
  réaliste (ex. 1280×900 hors écran plutôt que minimisée) — les moteurs
  rendent des layouts différents sous 400 px.
