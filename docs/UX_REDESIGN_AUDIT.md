# Synthesix UX/UI redesign audit

## Audit rapide du projet

Synthesix est une application locale pilotee par Zendriver/CDP. L'utilisateur
interagit avec `index.html`, puis `main.py` orchestre les actions, les moteurs
de recherche, les pages generees, les investigations, les captures et les
exports.

### Architecture reperee

- `index.html` : home locale, recherche web, selection d'investigation,
  filtres OSINT, variantes de requete, archive locale, actions de donnees et
  modale d'investigation.
- `theme.css` : theme commun pour home, historique, rapports, archive locale et
  pages d'investigation.
- `theme.js` et `i18n.js` : theme clair/sombre, langue, bouton Settings injecte
  dans la topbar, synchronisation entre onglets.
- `main.py` : boucle navigateur, polling des actions, injection overlay,
  recherche, capture de preuve, archive HTML/MHTML, comparaison, export et
  rafraichissement des pages.
- `utils.py` : generation historique et rapports de resultats HTML.
- `investigations/view.py` : generation du workspace investigation.
- `investigations/search_view.py` : generation de la page de recherche dans
  l'archive locale.
- `investigations/repository.py`, `service.py`, `models.py`, `migrations.py` :
  couche SQLite/FTS5, domaine investigation, provenance, entites, evidence,
  monitoring et exports.
- `evidence/` : captures PNG, HTML, MHTML, texte normalise, manifests,
  hachage, redaction des champs sensibles et comparaison.
- `analysis/` : extraction deterministe d'entites et analyse technique d'URL.
- `exports/` : export ZeroNeurone.
- `search_orchestrator.py`, `search_engine.py`, `google.py`, `bing.py`,
  `brave.py`, `duckduckgo.py`, `query_operators.py`, `search_regions.py`,
  `scoring.py` : recherche multi-moteur, dorks, regions, scoring et erreurs.

### Parcours utilisateur

1. Recherche simple : `index.html` -> action `search` -> `main.py` ->
   `SearchOrchestrator` -> rapport HTML dans `history/`.
2. Recherche OSINT avancee : meme flux avec `SearchFilters`, dorks, regions et
   variantes explicites.
3. Investigation : creation/selection via home, persistance SQLite, workspace
   genere dans `data/investigation_pages/`.
4. Sauvegarde de preuve : overlay CDP sur pages HTTP(S), action save/capture,
   enregistrement SQLite, regeneration du workspace.
5. Consultation des resultats : rapport DataTables genere par `utils.py`.
6. Analyse d'entites : actions depuis les cartes de pages sauvegardees et
   overlay de selection de texte.
7. Archive locale : recherche FTS5 depuis home, rapport local genere par
   `investigations/search_view.py`.
8. Gestion investigations : home et workspace, archivage en lecture seule.
9. Export preuves : liens manifest/artefacts dans workspace et export
   ZeroNeurone.
10. Historique : `history/history.html`, DataTables et actions de retry.

### Points de friction UX principaux

- La home combine trop de domaines : recherche web, investigation, filtres
  avances, variantes, archive locale, data cleanup, VPN et settings.
- Les actions destructives ou techniques sont visibles au meme niveau que la
  recherche.
- Les rapports de resultats restent en table dense alors que l'investigation et
  l'archive locale utilisent deja des cartes.
- L'overlay est robuste techniquement grace au Shadow DOM, mais trop riche pour
  un bouton flottant : save, archive, capture, selection d'entite et rattachement
  coexistent dans un long bloc inline dans `main.py`.
- Les pages generees ne partagent pas toutes le meme niveau de design system :
  le rapport de comparaison a encore du CSS inline.
- Les workflows puissants existent, mais la distinction entre "chercher",
  "collecter", "analyser", "archiver" et "administrer les donnees" n'est pas
  assez visible.

## Diagnostic UX

Ce qui surcharge l'interface :

- Trop de champs persistants dans le flux principal.
- Trop d'actions secondaires dans l'ecran d'accueil.
- Navigation limitee a une topbar compacte, sans separation claire des modes.
- Details analyste, entites, URL analysis et evidence visibles dans chaque
  carte sauvegardee des que la carte est deployee.
- Parametres techniques et nettoyage de donnees proches des actions courantes.

Ce qui doit rester visible :

- Recherche principale.
- Investigation active.
- Moteurs actifs.
- Filtres rapides vraiment frequents.
- Bouton Search.
- Acces clair a Historique, Archive locale, Workspace et Settings.

Ce qui doit etre masque ou deplace :

- Operateurs `site`, `exclude`, `title`, `url`, `body`, `filetype`, pays et
  dates dans un drawer avance.
- Variantes de requete dans le meme drawer ou un panneau "Variantes".
- Recherche archive locale dans un mode dedie, pas sous la recherche web.
- Nettoyage historique/profil navigateur dans Settings/Data.
- Details entites/evidence/analyse URL sous onglets ou panneaux de carte.

## Proposition de refonte

### Vision produit

Synthesix doit se presenter comme un poste d'enquete local : rechercher,
collecter, qualifier, relier et exporter des preuves avec provenance. L'ecran
doit toujours repondre a quatre questions : quelle investigation est active,
quelle recherche est lancee, quels filtres/moteurs sont actifs, et quelle action
analyste vient ensuite.

### Architecture d'information cible

- `Search` : recherche web, investigation active, moteurs, filtres rapides,
  drawer avance.
- `Investigations` : liste/courte gestion, workspace actif, pages sauvegardees,
  entites, preuves, monitoring, exports.
- `Archive` : recherche FTS5 locale, filtres, resultats, liens de provenance.
- `History` : recherches passees, rapports, retry.
- `Settings / Data` : langue, theme, chemins runtime, nettoyage historique,
  nettoyage profil navigateur.

### Layout cible

- Topbar compacte : marque, investigation active, navigation primaire,
  settings.
- Home en deux niveaux : recherche principale au centre, puis chips de contexte
  et moteurs.
- Drawer lateral `Advanced OSINT` pour les operateurs, dates, pays, variantes
  et apercu de requete.
- Archive locale comme ecran/rapport dedie, pas comme panneau secondaire de la
  home.
- Workspace investigation avec nav sticky conservee, mais cartes plus compactes
  et sous-sections explicites.

### Design system cible

- Tokens centraux : couleurs, spacing, radius, shadows, focus, statuts,
  surfaces, typographie.
- Composants : boutons, inputs, chips, badges, cards, tables, empty states,
  drawers, dialogs, notifications, provenance badges, score badges, entity
  badges.
- Etats : hover, focus-visible, disabled, loading, success, warning, danger.
- Direction visuelle : sobre, claire, compacte, professionnelle, sans imagerie
  "hacker" et sans dashboard surcharge.

## Overlay vs extension Chrome

### Option A - garder l'overlay injecte

Avantages :

- Aucun packaging extension.
- Fonctionne deja avec le navigateur pilote par Zendriver.
- Pas de permission Chrome supplementaire.
- Shadow DOM limite les collisions CSS.
- Le flux actuel est deja teste indirectement par les actions `main.py`.

Limites :

- Gros bloc de JS/CSS inline dans `main.py`, difficile a maintenir.
- UX exposee dans une zone flottante qui peut gener les sites visites.
- Etats et menus difficiles a faire evoluer proprement.
- Pas de side panel natif ni de separation claire entre page visitee et outil.

### Option B - extension Chrome dediee

Avantages :

- Separation plus propre : popup/side panel, content script minimal, UI propre.
- Permissions explicites et mieux documentables.
- Meilleure UX pour notes rapides, tags, investigation active et capture.
- Code front mieux testable et factorisable.

Limites :

- Distribution et installation locale plus complexes.
- Communication avec l'application locale a concevoir.
- Risque de permissions trop larges si le MVP est mal cadre.
- Zendriver/CDP reste necessaire pour recherche et captures robustes.

### Recommandation

- Court terme : garder l'overlay, le rendre plus discret, et extraire sa
  construction dans un module dedie ou une ressource JS/CSS locale injectee.
- Moyen terme : preparer une extension MVP avec permissions minimales, mais ne
  pas bloquer la refonte principale dessus.
- Cible : extension Chrome optionnelle pour la collecte manuelle, overlay CDP
  conserve comme fallback dans le navigateur pilote.

## Plan d'implementation

### Phase 1 - Audit et stabilisation

- Fichiers : documentation, `index.html`, `theme.css`, `utils.py`,
  `investigations/view.py`, `investigations/search_view.py`, `main.py`.
- Risques : casser les IDs/actions que `main.py` consomme, casser les tests de
  presence HTML, deformer les rapports generes.
- Tests : `python -m unittest tests.test_home_ui tests.test_investigation_view
  tests.test_local_search_view`.
- Acceptation : audit valide, aucun comportement modifie.

### Phase 2 - Design system

- Fichiers : `theme.css`, puis pages generees.
- Actions : ajouter tokens semantiques, classes de composants, etats vides,
  badges et layouts compacts.
- Risques : regression visuelle dans rapports DataTables et pages generees.
- Tests : tests UI existants, `git diff --check`, verification navigateur.
- Acceptation : composants reutilisables sans supprimer les classes existantes.

### Phase 3 - Home simplifiee

- Fichiers : `index.html`, `theme.css`, tests home.
- Actions : mettre Search au premier niveau, investigation active comme contexte,
  moteurs en chips, drawer OSINT, archive/settings/data en navigation secondaire.
- Risques : IDs manquants, payload de recherche altere, local archive moins
  accessible.
- Acceptation : recherche simple/avancee, variantes, investigation et archive
  locale inchanges cote payload.

### Phase 4 - Reports et investigation

- Fichiers : `utils.py`, `investigations/view.py`, `search_view.py`, `theme.css`.
- Actions : transformer result report en cartes ou table compacte enrichie,
  harmoniser empty states, provenance, scores, badges d'entites et preuves.
- Risques : DataTables, tri score, liens relatifs, echappement HTML.
- Acceptation : rapports lisibles, liens et provenance preserves.

### Phase 5 - Overlay puis extension MVP

- Fichiers : `main.py`, nouveau module JS/CSS d'overlay si valide, docs.
- Actions : overlay plus discret, panneau clair, notes/tags rapides si possible,
  style isole, puis specification extension.
- Risques : actions CDP, capture evidence, selection region, pages HTTP(S).
- Acceptation : save/capture/archive/selection toujours fonctionnels.

### Phase 6 - Non-regression

- Tests : ciblés puis `.venv\Scripts\python.exe -m unittest discover`,
  `git diff --check`, smoke test manuel navigateur si disponible.
- Acceptation : recherche exacte preservee, moteurs isoles, navigateur ferme
  proprement, preuves et archive verifiables.

## Premiere serie d'actions proposee

1. Valider ce diagnostic et la separation `Search / Investigations / Archive /
   History / Settings`.
2. Ajouter les tokens de design system sans supprimer les variables actuelles.
3. Reorganiser visuellement la home en gardant les memes IDs et payloads.
4. Harmoniser les empty states et badges de provenance sur archive locale et
   investigation.
5. Extraire progressivement l'overlay inline de `main.py` avant d'ajouter de
   nouvelles fonctions.
