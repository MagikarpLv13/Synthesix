# Synthesix — Audit UX (refonte cockpit)

Audit d'exécution de la refonte `redesign/cockpit` (repartie de `main` le
2026-06-19). Complète le diagnostic produit `docs/UX_REDESIGN_AUDIT.md` et la
référence design `docs/UX_REDESIGN.md`.

## Méthode

- Lecture statique de `index.html`, `theme.css`, `i18n.js`, `utils.py`,
  `investigations/view.py`, `investigations/search_view.py`, `main.py` et de
  tous les tests de rendu.
- Cartographie des **contrats** que `main.py` consomme par CDP avant toute
  modification (IDs, noms d'actions, payloads, objets `window.*`).
- Rendu réel hors-ligne des pages générées (rapport, historique, archive,
  workspace) via leurs fonctions Python pour extraire les chaînes et vérifier la
  couverture i18n.
- Suite `unittest` exécutée à chaque lot (référence 216 → 221).
- Smoke test navigateur **non réalisable** ici (pas de Chrome/Zendriver ni
  d'interface graphique). Pas de capture ni de vérification live ; validation =
  statique + tests + rendu HTML hors-ligne.

## Contraintes découvertes (qui ont cadré la refonte)

1. **Contrats CDP stricts.** La home expose `window.synthesixHome`
   (`consumeAction`, `setHistory`/`setInvestigations`, etc.) et `window.name =
   "synthesix-home"` ; les pages générées exposent `window.synthesixPage`. Tout
   est piloté par IDs et noms d'actions. → Refonte du **markup** uniquement,
   contrôleurs JS préservés.
2. **Tests de rendu très couplés.** `test_investigation_view.py` (656 l.) fige le
   markup du workspace, jusqu'à imposer **un seul script inline**. → `ui.render_page`
   (qui ajoute un script) ne peut pas être appliqué au workspace ; restructuration
   limitée à de l'ajout sûr.
3. **Overlay non testable.** L'overlay injecté (`main.py`, ~770 lignes) construit
   son DOM par `createElement` avec styles **inline entrelacés à la logique CDP**,
   dans une f-string échappée. Aucun test ; vérifiable uniquement dans un
   navigateur. → Reporté (voir Décisions).

## Problèmes identifiés (classés)

| # | Problème | Criticité | Fréquence | Impact | Difficulté |
| --- | --- | --- | --- | --- | --- |
| 1 | Rapport et historique en table dense jQuery/DataTables, peu scannables, dépendance CDN lourde. | Élevée | Élevée | Lenteur de triage | Moyenne |
| 2 | Home : un seul long formulaire, tout visible en permanence. | Élevée | Élevée | Charge cognitive | Moyenne |
| 3 | Vocabulaire visuel dupliqué (HTML statique + chaînes Python) → incohérences entre pages. | Moyenne | — | Maintenabilité | Moyenne |
| 4 | Overview de l'enquête purement descriptive, pas orientée action. | Moyenne | Moyenne | Pas de « next step » | Faible |
| 5 | Overlay riche et encombrant dans la page visitée. | Moyenne | Moyenne | Gêne le site | Élevée (non vérifiable) |

## Décisions

- **Couche de rendu unique** `ui.py` (pure) + design system cockpit dans
  `theme.css` : une seule source pour boutons/cartes/chips/badges/scores.
- **Multi-onglets + composants partagés** plutôt qu'une surface unique :
  préserve l'architecture pilotée par `main.py`.
- **Migration progressive, sans casse** : anciennes classes conservées tant
  qu'une surface n'est pas migrée ; jQuery/DataTables retirés des rapports et de
  l'historique (la table de couverture conserve `data-table`).
- **Workspace** : ajout sûr d'un **worklist** d'actions dans l'overview ; pas de
  réécriture du markup figé par les tests (inspecteur liste/détail reporté car il
  exige une réécriture coordonnée du test de 656 lignes).
- **Overlay reporté** : un changement non vérifiable sur le flux critique de
  collecte de preuves n'est pas livré à l'aveugle. À traiter avec un navigateur.
- **i18n** : chaque chaîne ajoutée est traduite dans les 6 langues et gardée par
  des tests (symétrie des dictionnaires + couverture stricte de la home +
  présence des chaînes de la refonte).

## Conservé

Toute la logique métier (recherche exacte, dorks, variantes, multi-moteur,
scoring explicable, enquêtes, preuves, archive FTS5, exports, monitoring) ; les
contrats CDP (`window.synthesixHome`/`synthesixPage`, actions, IDs, payloads) ;
le mode lecture seule des enquêtes archivées ; le modèle clair/sombre.

## Remplacé / ajouté

- Rapport, historique, archive : tables/cartes hétérogènes → `result_card`
  partagées + triage clavier ; jQuery/DataTables retirés (sauf table de
  couverture).
- Home : formulaire → cockpit (barre de commande, aperçu de requête, rail de
  contexte, divulgation progressive).
- Workspace : overview enrichie d'un worklist d'actions.
- `ui.py`, `theme.css` (couche cockpit), `docs/UX_REDESIGN.md`, garde-fous i18n.

## Reste à faire

1. **Overlay** (`main.py`) : refonte minimale **avec vérification navigateur**.
2. **Workspace** : inspecteur liste/détail (réécriture coordonnée markup + test).
3. Harmonisation finale des classes héritées restantes + purge du CSS inutilisé.
4. Smoke test navigateur complet (clair/sombre, fr/en, 768–1920 px).
