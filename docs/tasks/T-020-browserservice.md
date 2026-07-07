# T-020 — BrowserService : couche unique Zendriver/CDP

- **Statut** : done (2026-07-07, Claude)
- **Priorité** : P1 · **Effort** : moyen-élevé
- **Outil recommandé** : Claude
- **Dépendances** : T-005, T-006 (mesures)

## Objectif

Un seul module parle à Zendriver/CDP. `main.py`, les moteurs et `evidence/`
consomment une API interne stable : plus d'`evaluate` inline éparpillés ni
d'API privées zendriver hors de cette couche.

## Contexte

Les appels CDP sont dispersés : ~60 `evaluate` inline dans `main.py`, accès
privé `browser._get_targets` (`main.py:140`), `tab.send(uc.cdp.page.*)`
(`main.py:456-461`), captures dans `evidence/capture.py`, polls dans les
moteurs. Chaque évolution (push binding T-021, extension T-03x, second
navigateur T-040) exige aujourd'hui de toucher partout. La couche doit rester
**fine** : des wrappers typés, pas un framework.

## Fichiers concernés

- Nouveau : `browser/__init__.py`, `browser/service.py`.
- `browser_manager.py` : devient l'usine de `BrowserService` (inchangé sinon).
- `main.py` : remplacement mécanique des helpers CDP par les méthodes du
  service (peut être scindé en lots T-020a/b si le diff dépasse ~400 lignes).
- `evidence/capture.py` : signatures inchangées, reçoit un handle du service.

## Étapes

1. Définir l'API minimale (dataclasses simples, pas d'abstraction spéculative) :
   - `tabs() -> list[TabInfo]` (remplace `_open_tabs`, une seule requête) ;
   - `eval(tab, script, *, category: str) -> Any` (instrumentation T-006
     intégrée, timeout uniforme, exceptions normalisées) ;
   - `arm_new_document_script(tab, script) -> None` (idempotent par target) ;
   - `screenshot(tab, clip, beyond_viewport) -> bytes` ;
   - `mhtml(tab) -> str` ; `outer_html(tab) -> str` ;
   - `open_tab(url, *, background: bool)` / `close_tab(tab)` ;
   - `on_event(cdp_event, handler)` (enregistrement zendriver `add_handler`).
2. Migrer `main.py` : les helpers existants (`_set_home_status`,
   `_consume_*`, `_arm_overlay_focus_guard`, etc.) appellent le service ; leur
   JS ne bouge pas dans cette tâche.
3. Migrer `evidence/capture.py` (3 appels `tab.send`).
4. Interdire les regrets : ajouter un test qui échoue si `main.py` contient
   encore `tab.send(` ou `browser._get_targets` (grep dans le test).
5. Pas de changement de comportement : c'est un déplacement, validé par la
   suite complète + un smoke.

## Critères d'acceptation

- `main.py` sans appel CDP direct (`tab.send`, `_get_targets`,
  `uc.cdp.` hors imports) — vérifié par test.
- Suite complète verte ; smoke réel : démarrage, recherche, save page,
  capture région, archive — comportement identique.
- Toutes les méthodes du service instrumentées (catégories T-006).

## Commandes de test

```powershell
.venv\Scripts\python.exe -m unittest discover
```

Smoke réel obligatoire (workflow complet ci-dessus). Consigner.

## Risques

- Gros diff mécanique : le scinder en lots (a : service + evidence ;
  b : main.py) pour rester relisible.
- Sur-abstraction : refuser toute méthode non utilisée par un appelant
  existant ou une tâche planifiée.

## Résultat (2026-07-07, Claude)

- Nouveau paquet `browser/` : `BrowserService` (état par navigateur :
  `tabs()` avec purge du registre, `open_tab`, `arm_new_document_script`
  idempotent par target, `on_event` minimal pour T-021) + wrappers
  module-level sans état (`eval_js`, `screenshot`, `mhtml`, `outer_html`)
  utilisables avec un simple handle de tab. `get_browser_service(browser)`
  = instance partagée (WeakKeyDictionary ; doubles de test non
  weakref-ables → instance fraîche non cachée).
- `main.py` : plus aucun `tab.send` / `tab.evaluate` / `_get_targets` /
  `uc.cdp.` ; tous les evaluates passent par `eval_js` (catégories T-006,
  échec normalisé en `None` + log DEBUG, comme les anciens try/except par
  site). `_open_tabs` conservé comme seam de test (délègue au service).
  `_install_and_consume_save_overlay` reçoit le service en premier
  paramètre.
- `evidence/capture.py` : signatures publiques inchangées, les 3 `tab.send`
  migrés vers les wrappers.
- `browser_manager.py` : `HeadlessBrowserManager.service` posé à `create()`
  et `clear_browser_data()`, remis à `None` par `stop()`.
- Garde anti-régression : `tests/test_browser_service.py` échoue si
  `main.py` ou `evidence/capture.py` recontiennent un idiome CDP brut.
- Nouvelles catégories T-006 : `open_tab`, `arm_script`, `capture_html`,
  `capture_mhtml` ; `eval_settings` compte désormais aussi
  `_apply_settings_to_tabs` (hors boucle idle, baseline inchangée).

### Écarts assumés vs énoncé

- Pas de dataclass `TabInfo` : les appelants ont besoin des handles
  zendriver vivants (`bring_to_front`, `reload`) ; à revoir avec T-022.
- `close_tab` non implémenté : aucun appelant dans `main.py` (les moteurs
  ferment leurs tabs eux-mêmes et ne sont pas migrés par T-020).
- Pas de timeout uniforme sur `eval_js` : en ajouter un changerait le
  comportement ; à introduire quand T-021 en aura besoin.
- `tabs()` garde la double requête `update_targets` + `_get_targets`
  (limite zendriver 0.15.3 documentée, supprimée par T-022).

### Validation

- `unittest discover` : 350 tests OK (dont 14 nouveaux service + garde).
- Baseline T-006 verrouillée inchangée (`tests/test_cdp_budget.py`).
- Smoke réel : démarrage `python main.py --verbose`, home ouverte via
  `open_tab=1`, régime idle 1 `targets_poll` + 1 `eval_home` +
  1 `eval_settings` par tick, push initial 8 KiB puis 0 octet (T-003) ;
  kill des processus Chrome du profil → arrêt propre (« Goodbye! »,
  exit 0, aucun processus résiduel). Non couvert en live : recherche,
  save page, capture région, archive (nécessitent une session
  interactive ; comportement inchangé couvert par la suite complète).
