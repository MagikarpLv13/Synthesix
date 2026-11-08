# Synthesix — Refonte UX « cockpit »

Refonte conduite sur la branche `redesign/cockpit` (repartie de `main`). Objectif :
maximiser le débit de l'analyste sur la boucle `chercher → trier → collecter →
qualifier → exporter`, sans jamais sacrifier la provenance ni l'intégrité des
preuves. Voir `docs/UX_REDESIGN_AUDIT.md` pour le diagnostic d'origine.

## Principes

- **Recherche au premier plan** : une action principale évidente par écran.
- **Divulgation progressive** : les outils avancés sont repliés par défaut.
- **Contexte persistant** : l'enquête active reste visible.
- **Triage au clavier** : navigation sans souris sur les listes de résultats.
- **Langage preuve/provenance constant** sur toutes les pages générées.

## Architecture front-end (sans build ni framework)

- `theme.css` — tokens du design system + composants (couche « cockpit »).
- `ui.py` — **couche de rendu unique et pure** (aucune logique de chemin/IO ;
  le code appelant passe les préfixes d'assets et les liens calculés). Toutes
  les pages générées partagent ses primitives, ce qui supprime la duplication de
  markup HTML/Python.
- JavaScript natif : le contrôleur `window.synthesixHome` de la home et le
  `page_behavior_script` des pages générées (`window.synthesixPage`) sont
  préservés à l'identique ; le triage clavier est ajouté côté client.

### `ui.py` — primitives partagées

`render_page` (coquille + assets + script de comportement), `topbar`,
`context_bar`, `result_card` (titre, domaine, extrait, méta, actions, slot
`extra_html`), `chip`, `score_badge` (dépliable), `provenance`, `insight_grid`,
`empty_state`, `keyboard_hint`, `icon` (SVG inline, sans dépendance).

## Design system (`theme.css`)

Tokens en `:root`, surchargés par `:root[data-theme="dark"]` (variables
partagées, pas de feuille dupliquée) :

- Marque : `--brand-primary #2563EB`, `--brand-navy`, `--brand-cyan`,
  `--brand-slate` (conforme au `README`).
- Surfaces `--bg/--surface/--surface-2/--surface-3`, texte `--text/--muted`,
  séparateur `--line`.
- Sémantique avec variantes lisibles AA : `--success(-soft/-ink)`,
  `--warning(-soft/-ink)`, `--danger(-soft/-ink)`, `--accent(-soft/-ink)`.
- Échelle d'espacement 4 px `--space-1..6`, rayons `--radius-sm/md/lg`, ombre
  douce `--shadow-soft`, anneau de focus `--focus`, hauteur de contrôle
  `--control-h`, largeur max `--maxw`.

États couverts : hover, focus-visible, active, disabled ; `prefers-reduced-motion`
respecté ; empilement responsive (≤720 px / ≤640 px).

## Surfaces livrées

| Surface | Avant | Après |
| --- | --- | --- |
| Home (`index.html`) | formulaire dense, tout à plat | cockpit : barre de commande proéminente, **aperçu de requête** live, enquête active en **rail de contexte persistant**, moteurs compacts, outils avancés en grille de divulgation. Contrat `window.synthesixHome`, `window.name`, IDs et actions inchangés. |
| Rapport de résultats (`utils.py`) | table jQuery/DataTables | **cartes de triage** scannables (titre, domaine, extrait, chips de consensus moteurs, score dépliable + raison, provenance « Found via », action Open), bandeau d'insights, **triage clavier** (`j`/`k`/`o`). jQuery/DataTables supprimés. |
| Historique (`utils.py`) | table DataTables | liste de cartes scannables, « View results », triage clavier. jQuery/DataTables supprimés. |
| Archive locale (`investigations/search_view.py`) | cartes ad hoc | `result_card` partagées : chips Already-observed / moteur / statut / preuves, provenance d'enquête liée, première/dernière observation, notes, tags. Sûreté des liens préservée. |

## Accessibilité

Focus visible homogène, navigation clavier (triage + tabulation), `aria-label`
traduits, `role="status"`/`aria-live` sur les zones d'état, structure sémantique
(`header`/`section`/`details`), pas de dépendance exclusive à la couleur.

## Internationalisation

Traduction au runtime par `i18n.js` (correspondance du texte source anglais).
Toute nouvelle chaîne est ajoutée **dans les deux** dictionnaires `multilingual`
(fr/es/zh) et `additionalTranslations` (pt/de). Garde-fous (`tests/
test_i18n_coverage.py`) : symétrie des dictionnaires + couverture stricte des
chaînes de la home + présence des chaînes de la refonte (rapport, historique,
archive).

## Préservation fonctionnelle

Aucune logique métier modifiée : recherche exacte, dorks, variantes, multi-moteur,
scoring explicable, enquêtes, archive FTS5, captures et provenance restent
intactes. Les contrats CDP (`window.synthesixHome` / `window.synthesixPage`,
noms d'actions, payloads, IDs) sont préservés.

## Reste à faire

1. **Espace d'enquête** (`investigations/view.py`) : Overview en worklist +
   inspecteur liste/détail + sections en onglets, sur `ui.py`.
2. **Overlay injecté** (`main.py`) : outil de terrain minimal (1 action primaire,
   états clairs, Shadow DOM, footprint réduit).
3. Migration des classes héritées restantes vers le vocabulaire cockpit, puis
   suppression du CSS devenu inutilisé.
4. Smoke test navigateur complet (clair/sombre, fr/en, 768–1920 px) dès qu'un
   environnement Chrome est disponible.

## Validation

Suite `unittest` complète verte à chaque lot (220 tests). `i18n.js` validé par
`node --check`. `git diff --check` propre. Validation navigateur live non réalisée
(Chrome/Zendriver indisponible dans cet environnement) — vérification statique +
tests + rendu HTML hors-ligne.
