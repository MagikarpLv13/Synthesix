# docs/tasks — Suivi des tâches concrètes

Une tâche = un fichier `T-XXX-slug.md`. Codex et Claude doivent pouvoir se
relayer sur une tâche sans relire le reste du dépôt : chaque fichier est
autonome (contexte, fichiers, étapes, critères, tests, risques).

## Règles

- Avant de démarrer une tâche : la passer `in_progress` ici et déclarer le
  claim dans `AI_WORKLOG.md` (verrous si fichiers sensibles).
- Une tâche reste petite : si elle grossit, la découper en `T-XXXa/b`.
- Statuts : `todo` / `in_progress` / `blocked` / `review` / `done`.
- À la clôture : statut `done` + note de résultat en bas du fichier tâche,
  compte rendu dans `AI_WORKLOG.md`, mise à jour de `PROJECT_STATE.md` si la
  phase change d'état.
- « Outil recommandé » = qui exécute le mieux : Codex (édits mécaniques,
  Python pur, tests), Claude (CDP, architecture, spikes, smoke navigateur),
  ou les deux (lots séquentiels).
- Ordre conseillé à l'intérieur d'une phase : celui de l'index. Entre phases :
  0 → 1 → 2 → 3 → 4 ; QA en continu. Les dépendances dures sont notées dans
  chaque fichier.

## Index

### Phase 0 — Quick wins stabilité

| ID | Titre | Priorité | Outil | Statut |
|---|---|---|---|---|
| [T-001](T-001-file-actions-non-ecrasable.md) | File d'actions non écrasable côté pages | P0 | Codex | done |
| [T-002](T-002-cache-settings.md) | Cache `get_settings()` | P1 | Codex | done |
| [T-003](T-003-diff-push-home.md) | Payload home poussé seulement sur changement | P1 | Codex | done |
| [T-004](T-004-captcha-google-selector.md) | Détection captcha Google fiable | P1 | Claude | done |
| [T-005](T-005-nettoyages-cdp-mineurs.md) | Nettoyages CDP mineurs (targets, window.name, purges) | P2 | Codex | done |
| [T-006](T-006-instrumentation-cdp.md) | Instrumentation compteurs CDP + budget par tick | P1 | Claude | done |

### Phase 1 — Recherche robuste

| ID | Titre | Priorité | Outil | Statut |
|---|---|---|---|---|
| [T-010](T-010-deadline-globale-recherche.md) | Deadline globale de recherche + résultats partiels | P0 | Claude | todo |
| [T-011](T-011-recherche-non-bloquante.md) | Recherche non bloquante + annulation | P0 | Claude | todo |
| [T-012](T-012-attente-moteurs-composite.md) | Attente moteurs par evaluate composite | P1 | Claude | todo |
| [T-013](T-013-brave-fallback-parsing.md) | Parsing Brave : chaîne JSON → XPath | P1 | Codex | todo |
| [T-014](T-014-pool-tabs-moteurs.md) | Pool de tabs moteurs + fin des vols de focus | P2 | Claude | todo |
| [T-015](T-015-golden-files-parsing.md) | Golden files de parsing par moteur | P1 | Codex | todo |

### Phase 2 — BrowserService + push (pages locales)

| ID | Titre | Priorité | Outil | Statut |
|---|---|---|---|---|
| [T-020](T-020-browserservice.md) | BrowserService : couche unique Zendriver/CDP | P1 | Claude | todo |
| [T-021](T-021-push-binding-pages-locales.md) | Push `Runtime.addBinding` pour pages locales | P1 | Claude | todo |
| [T-022](T-022-decouverte-tabs-evenementielle.md) | Découverte de tabs par événements Target | P2 | Claude | todo |

### Phase 3 — Extension Chrome (migration overlay)

| ID | Titre | Priorité | Outil | Statut |
|---|---|---|---|---|
| [T-030](T-030-extension-squelette.md) | Squelette extension MV3 + build | P1 | Claude | todo |
| [T-031](T-031-spike-transport-extension.md) | Spike transport extension ↔ backend | P0 | Claude | todo |
| [T-032](T-032-chargement-extension.md) | Chargement de l'extension par Synthesix | P1 | Claude | todo |
| [T-033](T-033-portage-overlay-content-script.md) | Portage overlay en content scripts | P1 | Les deux | todo |
| [T-034](T-034-cablage-actions-extension.md) | Câblage actions extension → backend (flag) | P1 | Claude | todo |
| [T-035](T-035-contexte-et-statuts-extension.md) | Contexte investigation + statuts vers l'extension | P1 | Claude | todo |
| [T-036](T-036-bascule-retrait-overlay-cdp.md) | Bascule par défaut + retrait overlay CDP | P1 | Les deux | todo |

### Phase 4 — Isolation & données

| ID | Titre | Priorité | Outil | Statut |
|---|---|---|---|---|
| [T-040](T-040-navigateur-recherche-separe.md) | Navigateur de recherche séparé | P1 | Claude | todo |
| [T-041](T-041-sqlite-hors-event-loop.md) | Écritures SQLite lourdes hors event loop | P2 | Codex | todo |
| [T-042](T-042-hydratation-json-page-enquete.md) | Page enquête hydratée par workspace.json | P2 | Les deux | todo |
| [T-043](T-043-retrait-pandas-agregation.md) | Retrait de pandas de l'agrégation | P3 | Codex | todo |

### QA transverse

| ID | Titre | Priorité | Outil | Statut |
|---|---|---|---|---|
| [T-050](T-050-harness-faketab.md) | Harness FakeTab/FakeBrowser | P1 | Claude | todo |
| [T-051](T-051-test-workflow-investigation.md) | Test bout en bout workflow investigation | P2 | Les deux | todo |

## Gabarit de tâche

```markdown
# T-XXX — Titre

- **Statut** : todo
- **Priorité** : PX · **Effort** : faible/moyen/élevé
- **Outil recommandé** : Codex | Claude | Les deux
- **Dépendances** : T-YYY (ou aucune)

## Objectif
## Contexte
## Fichiers concernés
## Étapes
## Critères d'acceptation
## Commandes de test
## Risques
```
