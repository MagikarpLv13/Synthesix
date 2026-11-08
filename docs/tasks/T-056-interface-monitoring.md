# T-056 — Interface de configuration et historique du monitoring

- **Statut** : done
- **Priorité** : P1
- **Effort** : moyen
- **Outil recommandé** : Les deux
- **Dépendances** : T-053, T-054, T-055

## Objectif

Permettre à l'analyste de choisir ce qui est surveillé, confirmer ou remplacer
le profil proposé, régler la fréquence et comprendre les changements détectés.

## Étapes

1. Ajouter un dialogue depuis chaque page enregistrée.
2. Proposer `Automatique` par défaut avec explication du profil détecté.
3. Permettre de cocher les métriques et de saisir des sélecteurs personnalisés.
4. Afficher dernière et prochaine vérification, statut et erreurs.
5. Présenter un historique des observations et deltas.
6. Ajouter pause, reprise et lancement immédiat.
7. Internationaliser toutes les chaînes et couvrir clair, sombre et étroit.

## Critères d'acceptation

- L'analyste sait clairement ce que Synthesix a choisi automatiquement.
- Les réglages personnalisés sont modifiables sans supprimer l'historique.
- Une métrique indisponible n'est jamais affichée comme zéro.
- Les changements importants sont séparés du bruit mineur.
- Toutes les actions restent utilisables au clavier.

## Commandes de test

```powershell
cd frontend
npm run typecheck
npm run build
cd ..
.venv\Scripts\python.exe -m unittest tests.test_investigation_view tests.test_i18n_coverage
git diff --check
```

## Risques

- Surcharge visuelle de la page enquête.
- Mauvaise compréhension de la différence entre observation légère et archive
  probatoire.

## Résultat

- Un dialogue unique est accessible depuis chaque page enregistrée et chaque
  carte de moniteur. Il explique le profil automatique détecté et permet le
  mode personnalisé, les métriques, les sélecteurs CSS, la fréquence et la
  politique d'archive.
- Les cartes affichent état, profil, dernière/prochaine vérification et dernier
  changement. Le dialogue présente les vingt observations récentes, leurs
  deltas, valeurs typées et erreurs ; `missing`, `unavailable` et `error`
  restent distincts de la valeur numérique `0`.
- Pause, reprise et suppression conservent l'historique tant que le moniteur
  existe. `Run now` réclame le moniteur par bail SQLite et lance une sonde
  ciblée sans bloquer la boucle d'actions.
- Toutes les nouvelles chaînes sont synchronisées en français, espagnol,
  chinois, portugais et allemand. Le dialogue est responsive, navigable au
  clavier et désactive les mutations en lecture seule.

## Vérifications réalisées

- `py_compile` des sources et tests concernés — OK.
- `node --check i18n.js` et validation Node du script inline généré — OK.
- `tests.test_investigation_view tests.test_i18n_coverage` — 38 OK.
- Tests ciblés monitoring, investigations et main — inclus dans 175 tests OK.
- `cd frontend ; npm run typecheck ; npm run build` — OK.
- `.venv\Scripts\python.exe -m unittest discover` — 458 OK.
- `git diff --check` ciblé sur le lot — OK.

## Vérification non exécutée

- Smoke visuel interactif clair/sombre/étroit non exécuté : le runtime du
  navigateur intégré n'était pas exposé dans cette session.
