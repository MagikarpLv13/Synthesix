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
| 4 | Navigateur de recherche séparé, SQLite hors event loop, hydratation JSON | en cours (T-040/T-042 done ; T-041 review ; T-043 à faire) |
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
  le smoke réel utilisateur a été validé le 2026-07-09 et T-040 est clôturée.
- T-041 est en review depuis le 2026-07-09 : les points chauds
  `record_search`, `workspace_payload`, génération de page d'enquête et
  payload liste/caché sont sortis de l'event loop via `asyncio.to_thread`,
  sans réécrire le repository synchrone. Mesure synthétique : les opérations
  workspace/page/search étaient ~60-80 ms en sync sur 200 résultats + 50
  entités ; elles restent de coût comparable en thread mais ne bloquent plus
  la boucle asyncio.
- T-042a est livré le 2026-07-10 : chaque page d'enquête charge désormais un
  script adjacent `<id>.workspace.js`, écrit atomiquement et compatible
  `file://`. Les sauvegardes sans rechargement ne réécrivent plus la coquille
  HTML ; le re-rendu client sans `tab.reload()` est reporté aux sous-lots b/c.
- T-042b1 est livré le 2026-07-10 : une sauvegarde sans reload pousse la
  nouvelle version du script vers l'onglet source. La page charge les données
  sans navigation, met à jour les métriques de synthèse et émet
  `synthesix-workspace-update`; les sections détaillées restent à migrer.
- T-042b2a réconcilie les propriétés des entités avec le workspace au
  chargement initial et après une mise à jour poussée. Une propriété supprimée
  ne peut plus réapparaître après un refresh manuel.
- T-042b2b étend cette protection aux suppressions de pages, entités,
  propriétés extraites, preuves, exports et moniteurs. Les mises à jour
  détaillées non destructives restent à traiter avant la clôture de T-042.
- T-042 est en review depuis le 2026-07-10 : toutes les mutations no-reload
  réconcilient désormais le DOM avec le workspace compressé. La mesure sur 200
  pages donne 6 803 octets de workspace pour 1 390 744 octets de HTML (0,49 %)
  ; seul le smoke visuel/CDP d'une enquête réelle reste avant `done`.
- Le smoke réel T-042 a été validé par l'utilisateur le 2026-07-10 ; T-042 est
  clôturée.
- T-052 est clôturée après smoke utilisateur : les archives de page produisent
  désormais une capture
  visuelle complète dans un lecteur `visual.html` autonome (tuiles PNG
  intégrées), en plus du MHTML et du texte. Le lecteur visuel est l'artefact
  principal ; le DOM est transitoire et le manifeste reste disponible pour la
  vérification sans être affiché à l'analyste.

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
Prochaine validation prioritaire : observation T-041 sur grosse enquête réelle.
Après validation, poursuivre T-043.
Smokes réels toujours en attente au premier
run interactif : phase 2
(`eval_home`/`eval_page`, `targets_poll`, rafales tabs, kill/quit Chrome),
mesure `engine_tab_open`/`eval_engine_wait` (T-006), fenêtre sans clignotement
(T-014), annulation live (T-011), workflow complet recherche/save/capture/archive
post-T-020, smoke SPA/scroll infini/focus guard T-033.
