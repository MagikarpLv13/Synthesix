# T-051 — Test bout en bout du workflow investigation

- **Statut** : todo
- **Priorité** : P2 · **Effort** : moyen
- **Outil recommandé** : Les deux (Claude : squelette + points CDP fakés ;
  Codex : assertions et variantes)
- **Dépendances** : T-050

## Objectif

Un test d'intégration local (sans navigateur réel) qui déroule le workflow
complet : créer une investigation → sauver une page → capturer une preuve →
créer une entité → exporter ZeroNeurone — et vérifie la traçabilité de bout
en bout (DB, fichiers, manifests, hashes).

## Contexte

Les tests actuels couvrent les briques séparément (`test_investigations`,
`test_evidence`, `test_zeroneurone_export`). Aucun test ne vérifie la chaîne
complète ni la cohérence inter-couches (ex. : le chemin PNG stocké en DB
correspond au fichier écrit et au manifest ; l'export référence bien la
preuve). C'est la garantie anti-régression principale pendant les phases
2-4, qui remanient précisément ces enchaînements.

## Fichiers concernés

- Nouveau : `tests/test_workflow_investigation.py`.
- `tests/fakes.py` (T-050) : FakeTab avec `send` répondant aux commandes de
  capture (`Page.captureScreenshot` → PNG 1×1 base64, `Page.captureSnapshot`
  → MHTML minimal, `DOM.getDocument`/`getOuterHTML` → HTML fixture).

## Étapes

1. Environnement isolé : `SYNTHESIX_BASE_DIR` vers un répertoire temporaire
   (DB, evidence, exports, pages) via variables d'env + `reload_settings()`
   (T-002).
2. Dérouler le scénario via `InvestigationService` + les handlers de `main.py`
   appelés directement avec FakeTab (pas via la boucle de poll).
3. Assertions de traçabilité :
   - `manifest.json` de la capture : sha256 = hash du fichier écrit,
     `source_url`/`result_id` cohérents avec la DB ;
   - archive MHTML : entêtes sensibles absents (réutiliser un MHTML fixture
     avec `Cookie:` pour vérifier la sanitisation) ;
   - export ZeroNeurone : la preuve et l'entité y figurent avec les bons
     chemins relatifs ;
   - page enquête générée : contient la page sauvée et l'entité.
4. Variante erreur : capture qui échoue (FakeTab.send lève) ⇒ investigation
   intacte, pas de fichier orphelin, statut d'erreur retourné.
5. Budget : test < 5 s, hors réseau, hors navigateur.

## Critères d'acceptation

- Scénario nominal vert et déterministe (3 exécutions consécutives).
- La variante erreur ne laisse ni fichier orphelin ni ligne DB pendante.
- Le test échoue si on casse volontairement un maillon (ex. chemin stocké
  non relatif) — vérifié une fois manuellement à l'écriture.

## Commandes de test

```powershell
.venv\Scripts\python.exe -m unittest tests.test_workflow_investigation
```

## Risques

- Couplage aux handlers de `main.py` (signatures instables pendant les
  phases 2-3) : passer par de petites fonctions d'orchestration extraites au
  besoin — c'est un bénéfice secondaire (les handlers deviennent testables).
- Fixtures binaires : garder le PNG/MHTML minimaux (< 1 Ko), générés dans le
  test, pas de binaires commit.
