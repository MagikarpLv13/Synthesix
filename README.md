# Synthesix

Synthesix est un navigateur local spécialisé dans les dorks et les recherches
multi-requêtes. Il interroge Google, Bing, Brave et DuckDuckGo, fusionne les
liens en double, classe les résultats et permet de les ouvrir dans des profils
navigateur séparés et persistants.

Les enquêtes, preuves, entités, graphes, exports ZeroNeurone et fonctions de
monitoring ne font plus partie de Synthesix. Le travail d'investigation reste
extérieur, dans ZeroNeurone avec ZNELFP. Aucune passerelle spécifique avec ce
plugin n'est implémentée.

## Lancer l'application sous Windows

Un Chrome ou Brave installé est nécessaire. Son moteur et ses mises à jour
restent gérés par le navigateur.

Dans le paquet construit depuis cette branche, ouvrir `Synthesix.exe` dans le
répertoire `Synthesix`. Conserver les fichiers `_internal` à côté de l'exécutable.
L'archive `dist/Synthesix-Windows.zip` contient ce répertoire complet. Python et
Node ne sont pas nécessaires sur la machine d'utilisation.

L'exécutable conserve ses données dans `%LOCALAPPDATA%/Synthesix`, indépendamment
du dossier d'installation. L'option `--data-dir <répertoire>` permet de choisir
un autre emplacement. Le paquet préparé localement n'est pas signé.

## Utiliser Synthesix

1. Saisir une à vingt requêtes, une par ligne.
2. Choisir les moteurs et, si besoin, les filtres de site, titre, URL, contenu,
   type de fichier, pays ou dates.
3. Laisser les dorks automatiques pour rechercher les termes en phrase exacte,
   ou désactiver cette option pour une recherche naturelle. Les requêtes avec
   des opérateurs explicites sont conservées.
4. Lancer la recherche : les résultats apparaissent progressivement et les
   doublons sont fusionnés. La couverture indique les erreurs ou challenges
   moteur. L'annulation conserve les résultats déjà disponibles dans l'historique.
5. Choisir le profil d'ouverture, puis cliquer sur un résultat.

Dans **Profils navigateur**, créer et nommer une persona puis ouvrir sa fenêtre.
Se connecter normalement aux sites une première fois : le navigateur conserve
la session. Chaque persona utilise son propre répertoire de données. Plusieurs
fenêtres d'une même persona partagent sa session. Synthesix ne collecte pas ses
mots de passe et n'attache pas CDP à ces fenêtres.

Le profil neutre de navigation et le profil d'automatisation des moteurs sont
séparés des personas. Les profils séparent les sessions ; ils ne changent ni
l'adresse IP ni l'empreinte de la machine. Aucun proxy par profil n'est configuré.
Les fenêtres des personas restent indépendantes quand Synthesix se ferme.

L'historique permet de retrouver les résultats et de relancer les mêmes requêtes.
Les cinquante recherches les plus récentes sont affichées ; les plus anciennes
restent conservées dans la base.

## Développement

Python 3.10+ et Chrome/Brave sont nécessaires. Depuis le projet :

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

La version Zendriver est volontairement fixée dans `requirements.txt`. Toute
mise à jour doit inclure les tests moteurs, les tests CDP et les smoke tests réels.

Le bundle frontend est versionné. Pour modifier l'interface uniquement :

```powershell
cd frontend
npm install
npm run typecheck
npm run build
```

Les pages sont chargées en `file://` avec un script classique IIFE. Aucun serveur
local et aucun environnement Node ne sont nécessaires à l'exécution.

## Architecture

- `main.py` : options de lancement et cycle de vie de la commande.
- `app/runtime.py` : assemblage de l'application et commandes de la page locale.
- `app/search.py` : validation des requêtes et navigateur de recherche à la demande.
- `search_orchestrator.py` : exécution parallèle bornée, résultats progressifs,
  déduplication et scoring. `collect()` ne produit ni rapport ni historique.
- `query_syntax.py`, `query_operators.py`, `query_variants.py` : syntaxe des dorks.
- `google.py`, `bing.py`, `brave.py`, `duckduckgo.py`, `parsers.py` : adaptateurs moteurs.
- `app/storage.py` : base SQLite indépendante pour recherches et noms de profils.
- `app/profiles.py` : lancement natif des personas, sans pont privilégié dans leurs pages.
- `browser/` et `browser_manager.py` : CDP, découverte des onglets et lancement.
- `frontend/src/components/sx-browser-app.ts` : interface Lit principale.

Les utilitaires d'export de rapports HTML restent disponibles séparément dans
`utils.py` et `ui.py`. Ils ne sont pas importés par le nouveau parcours de recherche.

## Données et ancienne version

Depuis les sources, les données sont relatives au projet ; dans l'exécutable,
elles sont relatives au répertoire de données indiqué plus haut :

| Chemin | Usage |
|---|---|
| `data/browser.sqlite` | Noms des profils, requêtes, résultats et couverture |
| `data/browser-profiles/<identifiant>/` | Données natives des personas |
| `data/browser-ui-profile/` | Profil de l'accueil et de la navigation neutre |
| `search-profile/` | Profil isolé d'automatisation des moteurs |
| `logs/browser.log` | Diagnostic local |

L'ancienne base `data/synthesix.db`, les preuves et les anciens rapports ne sont
ni ouverts ni migrés ni supprimés par ce lancement. Le nouvel historique ne les
importe pas automatiquement. Le commit `0e58af1` conserve les sources complètes
avant recentrage pour retrouver l'ancienne application et exporter les enquêtes
si nécessaire, dans une copie séparée avec sauvegarde préalable des données.

## Vérifications et construction

```powershell
.venv\Scripts\python.exe -m unittest discover
.venv\Scripts\python.exe tests/manual/smoke_browser_app.py
.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.venv\Scripts\python.exe scripts/build_windows.py
.venv\Scripts\python.exe tests/manual/smoke_frozen_browser.py
```

Les smoke tests utilisent des profils temporaires et des données synthétiques.
Le test d'interface exerce les vrais clics et le vrai transport CDP, avec des
moteurs simulés. Il ne valide pas les connexions à des comptes réels ni la
fiabilité des pages de résultats externes du jour.

Les options `--quiet`, `--verbose` et `--debug-html` restent disponibles.
`SYNTHESIX_BROWSER_EXECUTABLE_PATH` sélectionne un navigateur explicitement.
`SYNTHESIX_SEARCH_WINDOW_MODE=visible|minimized|offscreen|headless` configure
l'instance de recherche ; `offscreen` reste le mode par défaut. Le mode headless
peut déclencher davantage de challenges, qui ne sont pas contournés.

Voir `docs/ARCHITECTURE_NAVIGATEUR.md` et `AI_WORKLOG.md` pour les décisions et
les vérifications de la refonte. Les anciennes tâches d'investigation décrivent
l'historique et ne constituent plus le périmètre produit.
