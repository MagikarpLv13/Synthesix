# T-050 — Harness FakeTab/FakeBrowser

- **Statut** : done
- **Priorité** : P1 · **Effort** : moyen
- **Outil recommandé** : Claude (première version), Codex (extensions
  ultérieures)
- **Dépendances** : aucune — prérequis des tests de T-010, T-011, T-012,
  T-021 ; à faire tôt

## Objectif

Un faux navigateur/tab scriptable et partagé par tous les tests, pour tester
la boucle d'actions, les attentes moteurs, les retries et (plus tard) le
transport push — sans navigateur réel ni duplication de mocks ad hoc.

## Contexte

Les tests existants (`tests/test_engines.py`, `test_search_orchestrator.py`,
`test_main.py`) fabriquent chacun leurs doublures locales. Les tâches du plan
ont besoin d'un harness commun : séquences de réponses programmables
(`evaluate` → valeurs successives, `query_selector` → None puis nœud,
`get_content` → HTML fixture), horloge accélérée, journal des appels pour les
assertions de budget (T-006).

## Fichiers concernés

- Nouveau : `tests/fakes.py` — `FakeTab`, `FakeBrowser`, `FakeElement`,
  helpers de scénario.
- Migration progressive des doublures existantes (uniquement celles touchées
  par les tâches du plan — pas de réécriture globale des tests).

## Étapes

1. `FakeTab` : `evaluate`, `query_selector`, `xpath`, `get_content`, `get`,
   `close`, `bring_to_front`, `send` (captures), `save_screenshot`, `find`,
   attributs `url`, `target_id`, `closed`. Chaque méthode : file de réponses
   programmée (`side_effects`) + journal `calls` horodaté.
2. `FakeBrowser` : `tabs`, `update_targets`, `get(url, new_tab)`, `stopped`,
   `main_tab`, `cookies.clear` ; fabrique de FakeTabs.
3. Horloge : les boucles d'attente utilisent `time.monotonic` +
   `asyncio.sleep` — fournir un helper de test qui patche `asyncio.sleep` en
   no-op comptabilisé et avance une horloge injectable, pour tester les
   timeouts sans temps réel (les modules devront accepter une injection
   d'horloge là où c'est trivial ; sinon patch ciblé).
4. Journal exploitable : `harness.count("evaluate")`,
   `harness.scripts_evaluated_bytes()` — base du test budget T-006.
5. Documenter dans le module : 3 exemples d'usage (attente moteur, action
   home, capture).

## Critères d'acceptation

- Un test d'exemple par cas d'usage fourni et vert.
- `wait_for_page_load` testé timeout/succès en < 100 ms de temps réel.
- Utilisé par au moins un test réel migré (ex. un cas de
  `test_search_orchestrator`).

## Commandes de test

```powershell
.venv\Scripts\python.exe -m unittest tests.test_fakes
.venv\Scripts\python.exe -m unittest discover
```

## Risques

- Divergence fake/zendriver réel (signatures, exceptions) : limiter le fake
  aux méthodes réellement utilisées par le code (grep), et noter la version
  zendriver de référence (0.15.3) en tête du module.
- Sur-ingénierie de l'horloge : commencer par le patch `asyncio.sleep`
  comptabilisé ; n'ajouter l'horloge injectable que si un test la réclame.

## Résultat (2026-07-06, Claude)

- `tests/fakes.py` : `FakeTab` (evaluate/query_selector/xpath/find/
  get_content/get/send/save_screenshot/bring_to_front/reload/close),
  `FakeBrowser` (tabs/main_tab/get/update_targets/_get_targets/cookies.clear/
  stop), `FakeElement`, `CallJournal` (count, scripts_evaluated_bytes),
  `fake_clock(*modules)` qui patche `time.monotonic` + `asyncio.sleep` via
  proxy de module (aucun effet global). Résolution des réponses :
  file `program()` → handler `on()` → défaut par méthode.
- `tests/test_fakes.py` : 6 tests — attente moteur (succès + timeout 30 s
  simulé sans temps réel), boucle home action (`wait_for_home_action`),
  capture (`capture_png`), comportements du fake.
- Migration : `tests/test_cdp_budget.py` utilise désormais le harness
  (fabrique locale `make_tab` + handler de scripts), baseline T-006 intacte.
- Tests : `tests.test_fakes` (6 OK), `tests.test_cdp_budget` (4 OK),
  `unittest discover` 317 OK.
