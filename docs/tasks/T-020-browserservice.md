# T-020 — BrowserService : couche unique Zendriver/CDP

- **Statut** : todo
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
