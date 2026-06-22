@AGENTS.md

# Instructions propres à Claude Code

## Démarrage

Avant toute modification non triviale :

1. lire `AI_WORKLOG.md` ;
2. vérifier branche et `git status --short` ;
3. identifier fichiers, contrats et tests concernés ;
4. rechercher les références avant de renommer une action CDP, un attribut `data-*`, un événement Lit, une API ou une clé i18n ;
5. revendiquer la tâche et les fichiers chauds dans le journal.

Ne pas écrire si un autre agent possède un verrou incompatible.

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

## Plan et périmètre

- Correction locale évidente : agir directement.
- Tâche multi-fichiers ou risquée : plan court avec critères de validation.
- Découper les gros travaux en lots indépendants.
- Préférer une correction ciblée à une réécriture.
- Ne pas effectuer de « nettoyage au passage » hors périmètre.

## Sous-agents

Utiliser les sous-agents pour l'exploration en lecture seule, l'inventaire des références, la revue de tests ou l'analyse d'un sous-système.

- Un seul agent écrivain par fichier ou lot.
- Jamais d'écritures parallèles sur les mêmes fichiers.
- Transmettre explicitement invariants, périmètre et fichiers interdits.
- Rappeler les règles critiques aux agents Explore/Plan.
- Exiger un retour synthétique : fichiers, contrats, risques et tests.
- Vérifier les conclusions avant toute modification.

## Discipline d'édition

- Lire les sections utiles avant de patcher.
- Préserver style local, noms publics et ordre logique.
- Faire des patches petits ; relire le diff après un changement structurel.
- Modifier la source TS, jamais directement le bundle généré.
- Ne jamais inventer un résultat de commande, test ou comportement observé.
- En cas d'échec, corriger la cause ou documenter précisément la limite.

## Rappels Synthesix

- Python 3.10+, async-first, Zendriver/CDP ; entrée : `python main.py`.
- Recherche exacte, isolation des moteurs et arrêt propre du navigateur sont des invariants.
- Pages internes en `file://` avec bundle IIFE chargé par script classique.
- Overlay IIFE injecté sur DOM tiers, isolé par Shadow DOM.
- TypeScript strict, Lit, préfixe `sx-`, tokens CSS, accessibilité et i18n.
- Source frontend et bundle doivent être committés ensemble.
- Changement CDP/overlay fonctionnel : smoke live obligatoire ou absence explicitement signalée.
- Ne jamais versionner données d'enquête, preuves, profils, rapports ou secrets.

## Séquences de travail

### Python

1. identifier/reproduire le défaut ;
2. lire module et tests concernés ;
3. corriger la cause racine ;
4. ajouter/adapter un test ciblé ;
5. exécuter test ciblé puis suite large si transversal ;
6. `git diff --check` ;
7. clôturer `AI_WORKLOG.md`.

### Lit

1. vérifier claim et composants voisins ;
2. préserver API, slots, événements et attributs ;
3. éviter tout texte i18n en dur ;
4. mettre à jour l'index et la démo ;
5. `npm run typecheck` puis `npm run build` ;
6. vérifier clair/sombre, vide, long et dense ;
7. clôturer `AI_WORKLOG.md`.

### CDP / overlay

1. inventorier producteurs et consommateurs ;
2. préserver actions et payloads sauf migration demandée ;
3. modifier par petits incréments ;
4. exécuter tests Python et build nécessaire ;
5. effectuer le smoke CDP live ;
6. documenter chaque scénario non testé.

## Commandes

```powershell
.venv\Scripts\python.exe -m unittest discover
.venv\Scripts\python.exe -m py_compile <modules>
git diff --check

cd frontend
npm run typecheck
npm run build
```

Utiliser les équivalents du virtualenv sous Linux/macOS. Ne pas installer globalement.

## Suivi et réponse finale

À chaque relais, consigner état, fichiers, décisions, tests, inconnues et prochaine action exacte. Ne pas mettre dans le journal de raisonnement interne ni de logs bruts.

Terminer avec :

- résultat ;
- fichiers modifiés ;
- tests réellement exécutés ;
- vérifications non exécutées ;
- risques ou prochaine étape indispensable.

Ne pas déclarer un changement validé sans preuve.
