# PROJECT_STATE.md — État court du projet

> État synthétique de Synthesix pour Codex et Claude. Mise à jour à chaque étape
> significative. Les détails opérationnels (claims, verrous) restent dans
> `AI_WORKLOG.md`. Les tâches concrètes vivent dans `docs/tasks/`.

## Vision courte

Synthesix : outil OSINT local-first. Recherche multi-moteur pilotée par
Zendriver/CDP, agrégation/scoring/rapports HTML, workflow d'investigation
(pages sauvées, captures, entités, exports ZeroNeurone). UI = pages `file://`
+ composants Lit. Pas de serveur, pas de cloud, usage PC.

## Décisions structurantes en vigueur

| ID | Décision |
|---|---|
| DEC-PLAN-01 | Zendriver est conservé. Pas de migration Playwright ni CDP maison. |
| DEC-PLAN-02 | Le transport d'actions UI passe progressivement du polling `evaluate` à un modèle push (`Runtime.addBinding` + événements CDP) derrière une couche `BrowserService`. |
| DEC-PLAN-03 | L'overlay injecté par CDP dans les pages http(s) est retiré progressivement au profit d'une **extension Chrome MV3 intégrée** (répertoire `extension/`, chargée par Synthesix, pas un produit séparé). |
| DEC-PLAN-04 | L'extension couvre uniquement les pages http/https. Les pages locales `file://` (home, enquêtes, rapports) restent pilotées par CDP. |
| DEC-PLAN-05 | Les captures (PNG/MHTML/HTML) restent réalisées côté Python via CDP ; l'extension ne transmet que les intentions et coordonnées. |
| DEC-PLAN-06 | La recherche automatisée sera isolée dans une seconde instance navigateur avec profil dédié (`search-profile/`). |
| DEC-PLAN-07 | Transport extension retenu : `Runtime.addBinding("synthesixDispatch")` armé sur le `service_worker` Synthesix, messages content script → service worker → Python via `chrome.runtime.sendMessage` puis binding CDP. Validé avec Brave ; Chrome stable brandé ignore `--load-extension` dans l'environnement testé. |

## Phases du plan (voir docs/tasks/README.md)

| Phase | Contenu | Statut |
|---|---|---|
| 0 | Quick wins stabilité (file d'actions, caches, instrumentation CDP) | **terminée** (2026-07-06, T-001..T-006) |
| 1 | Recherche robuste (deadline globale, non-bloquante, attentes optimisées, parsing durci) | **terminée** (2026-07-06, T-010..T-015) |
| 2 | BrowserService + push CDP pour pages locales | en cours (T-020 done ; T-021/T-022 review, smoke live restant) |
| 3 | Extension Chrome : squelette, spike transport, portage overlay, bascule | en cours (T-030..T-035 done ; T-036 attend une semaine d'usage extension) |
| 4 | Navigateur de recherche séparé, SQLite hors event loop, hydratation JSON | en cours (T-040 review ; T-041..T-043 à faire) |
| QA | Harness FakeTab/FakeBrowser, tests bout en bout | en cours (T-050 done ; T-051 à faire) |

## État courant

- Branche active : `feat/lit-frontend`.
- Migration Lit frontend : terminée (Lots 17-22, voir `frontend/TASKS.md`).
- Review technique complète réalisée le 2026-07-06 (base du présent plan).
- Phase 0 livrée le 2026-07-06 (6 commits, 307 tests verts). Baseline CDP
  verrouillée par `tests/test_cdp_budget.py` : 1 inventaire targets +
  6 evaluates par tick idle ; payloads home à 0 octet en régime stable.
- Phase 3 démarrée le 2026-07-07 : squelette extension MV3 `extension/`
  livré par T-030, build intégré à `frontend/build.mjs`, permissions limitées
  à `storage`. T-031 a validé le transport extension ↔ Python avec Brave :
  target service worker Synthesix, binding CDP, deux pages `https://`, latence
  ~1-3 ms et message reçu après 125 s d'inactivité MV3. T-032 ajoute les flags,
  la détection, l'ID stable et le statut home ; Chrome stable brandé reste en
  mode dégradé car il ignore `--load-extension` dans l'environnement testé.
  T-033 porte l'overlay dans l'extension : injection `overlay-main.js`
  CSP-safe, bootstrap DOM main-world, focus guard MV3, relais d'actions vers
  le service worker ; smoke Brave OK sur `example.com` et `github.com`. T-034
  câble les actions extension vers le dispatcher backend derrière
  `SYNTHESIX_OVERLAY_MODE=auto|cdp|extension` ; smoke Brave réel OK sur deux
  onglets HTTPS avec résolution correcte de l'onglet source. T-035 ajoute le
  sens backend → extension : contexte investigation poussé sur changement
  uniquement via `chrome.storage.local`, nouveaux tabs contextualisés depuis le
  storage, statuts boutons routés par `chrome.tabs.sendMessage` au `tabId`
  d'origine. Smoke Brave renforcé OK le 2026-07-08 sur contexte, clics,
  `observe_saved_page` et statuts boutons backend → overlay ; smoke app
  complète validé par l'utilisateur le 2026-07-08.
- Phase 4 démarrée le 2026-07-08 : T-040 isole les recherches dans une
  seconde instance Zendriver lancée paresseusement avec profil
  `search-profile/`, sans extension ni bookmark. Le mode
  `SYNTHESIX_SEARCH_BROWSER=shared` restaure le comportement historique. Les
  tabs idle `about:blank` sont nettoyés après recherche/retry et l'instance
  search est stoppée s'il ne reste que des tabs vides. La fenêtre recherche
  est hors écran par défaut (`SYNTHESIX_SEARCH_WINDOW_MODE=offscreen`) avec
  modes `visible`, `minimized` et `headless` disponibles ; Brave headless
  démarre et navigue, mais DuckDuckGo a déclenché un challenge anti-robot en
  smoke moteur, donc headless reste opt-in. En mode headless, un
  `RobotChallengeError` ouvre automatiquement l'artefact capturé dans le
  navigateur UI pour inspection. En mode fenêtre, un captcha manuel Google,
  Brave ou DuckDuckGo replace temporairement la fenêtre de recherche à l'écran
  pour résolution humaine. Les tests unitaires et la suite complète sont verts ;
  le smoke réel focus/challenge reste à exécuter avant passage `done`.

## Risques ouverts majeurs

1. ~~Actions UI perdables~~ corrigé (T-001) ; le coût du polling reste,
   réduit par T-003, supprimé par les phases 2/3.
2. ~~Recherche bloque la boucle d'actions~~ corrigé (T-011 : tâche de fond,
   `cancel_search`, bouton home) ; ~~pas de plafond global~~ corrigé
   (T-010 : budget 120 s, résultats partiels, annulation propre). Smoke
   live T-011 non exécuté (clôture décidée par l'utilisateur) — à observer
   au premier run réel.
3. ~~Parsing Brave par regex sur bundle minifié~~ durci (T-013 : repli XPath,
   suffixe JSON assoupli ; T-015 : fixtures golden parsing).
4. `--load-extension` retiré de Chrome stable brandé ≥137 : l'extension doit prévoir l'installation unpacked persistante (T-032).
5. Smokes navigateur réels de la phase 0 non exécutés (kill Chrome, captcha
   Google, mesure 60 s) — à couvrir au premier run interactif.

## Prochaine action recommandée

Phase 3 : T-030..T-035 livrés et validés. Ne pas démarrer T-036 avant une
semaine d'usage quotidien en mode extension sans régression signalée. Garder
Chrome stable en mode dégradé CDP tant que `--load-extension` y est ignoré.
Prochaine validation prioritaire : smoke réel T-040 (recherche complète pendant
navigation dans la fenêtre principale, aucun tab moteur côté UI, challenge
simulé qui remonte la fenêtre recherche, quit sans process orphelin). Smokes
réels toujours en attente au premier run interactif : phase 2
(`eval_home`/`eval_page`, `targets_poll`, rafales tabs, kill/quit Chrome),
mesure `engine_tab_open`/`eval_engine_wait` (T-006), fenêtre sans clignotement
(T-014), annulation live (T-011), workflow complet recherche/save/capture/archive
post-T-020, smoke SPA/scroll infini/focus guard T-033.
