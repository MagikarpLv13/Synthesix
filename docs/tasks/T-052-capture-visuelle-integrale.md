# T-052 — Capture visuelle intégrale des archives de page

- **Statut** : done (2026-07-10, smoke utilisateur)
- **Priorité** : P1
- **Effort** : moyen
- **Outil recommandé** : Codex
- **Dépendances** : T-020, T-050

## Objectif

Une archive de page doit fournir une preuve visuelle ouvrable hors ligne et
défilable, sans promettre que le DOM HTML brut est une reproduction fidèle.

## Réalisé

- `capture_visual_page()` relève les dimensions CSS via CDP, réchauffe les
  contenus lazy par défilement contrôlé, puis capture des tuiles PNG bornées à
  4 096 pixels de haut.
- Les tuiles sont encodées dans un unique `visual.html` local. Le hash stocké
  couvre donc chaque octet visuel et le lecteur ne dépend d'aucune ressource
  distante.
- L'hôte de l'overlay est masqué par `display:none!important` avant chaque
  défilement et reste absent des tuiles ; sa feuille de style et la position
  de lecture sont restaurées dans un `finally`.
- Une archive conserve `Visual`, MHTML et texte normalisé. Le DOM HTML n'est
  qu'un fichier transitoire pour produire le texte, puis est supprimé.
  L'interface présente uniquement `Visual`, `MHTML` et `Text`.
- Le manifeste de provenance reste associé à la preuve pour la vérification,
  sans encombrer la vue analyste.
- `visual` est exclu des parcours d'extraction de texte, de comparaison et de
  provenance : il reste une preuve visuelle, pas un faux document source.

## Critères d'acceptation

- Le lecteur `visual.html` s'ouvre en `file://` sans ressource réseau.
- Une page longue produit plusieurs tuiles sans dépasser une zone de capture
  raisonnable.
- Une erreur de capture visuelle laisse les autres archives disponibles et
  marque la preuve `partial`.
- Le manifeste enregistre dimensions et nombre de tuiles.
- L'analyste retrouve sa position initiale après la capture.

## Tests

```powershell
.venv\Scripts\python.exe -m unittest tests.test_evidence tests.test_browser_service tests.test_main tests.test_investigation_view
.venv\Scripts\python.exe -m unittest discover
git diff --check
```

## Smoke restant

Sur une page réelle, vérifier : page longue avec images lazy, SPA, thème clair
et sombre de la page enquête, restauration du scroll, ouverture de `visual.html`
et de `page.mhtml`. Les sites qui réagissent fonctionnellement au scroll (par
exemple certains carrousels vidéo) doivent être testés séparément ; leur état
capturé est celui observé pendant l'archive.

## Validation finale

L'utilisateur a validé l'ouverture de `visual.html`, l'absence de l'overlay
Synthesix, la liste réduite `Visual` / `MHTML` / `Text` et la consultation
locale. La tâche est clôturée.
