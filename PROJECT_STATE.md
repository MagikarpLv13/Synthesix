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

## Phases du plan (voir docs/tasks/README.md)

| Phase | Contenu | Statut |
|---|---|---|
| 0 | Quick wins stabilité (file d'actions, caches, instrumentation CDP) | **terminée** (2026-07-06, T-001..T-006) |
| 1 | Recherche robuste (deadline globale, non-bloquante, attentes optimisées, parsing durci) | **terminée** (2026-07-06, T-010..T-015) |
| 2 | BrowserService + push CDP pour pages locales | en cours (T-020 done ; T-021/T-022 review, smoke live restant) |
| 3 | Extension Chrome : squelette, spike transport, portage overlay, bascule | à faire |
| 4 | Navigateur de recherche séparé, SQLite hors event loop, hydratation JSON | à faire |
| QA | Harness FakeTab/FakeBrowser, tests bout en bout | en cours (T-050 done ; T-051 à faire) |

## État courant

- Branche active : `feat/lit-frontend`.
- Migration Lit frontend : terminée (Lots 17-22, voir `frontend/TASKS.md`).
- Review technique complète réalisée le 2026-07-06 (base du présent plan).
- Phase 0 livrée le 2026-07-06 (6 commits, 307 tests verts). Baseline CDP
  verrouillée par `tests/test_cdp_budget.py` : 1 inventaire targets +
  6 evaluates par tick idle ; payloads home à 0 octet en régime stable.

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

Phase 2 : T-020 livré. T-021 et T-022 livrés en `review`. T-021 : push
`Runtime.addBinding` sur home + pages d'enquête (poll en repli, throttlé une
fois le binding confirmé). T-022 : découverte de tabs par le registre
événementiel de zendriver (`Target.*`), le `getTargets` autoritaire ne
tournant plus qu'en resync lent (10 s, `SYNTHESIX_TARGET_RESYNC_INTERVAL`) qui
sert aussi de sonde de liveness ; overlay CDP http/https et scan de réglages
inchangés (hors périmètre, DEC-PLAN-04). Reste sur la phase 2 : smoke CDP live
(latence perçue, `eval_home`/`eval_page` réduits, `targets_poll` ≈ 0,1/s,
rafales d'ouverture/fermeture, kill Chrome, quit normal) au premier run
interactif. La phase 2 n'a plus de tâche à coder ; enchaîner sur la phase 3
(T-030/T-031, extension Chrome) ou T-051 (test bout en bout investigation, QA).
Smokes réels en attente au premier run interactif : mesure
`engine_tab_open`/`eval_engine_wait` (T-006), fenêtre sans clignotement
(T-014), annulation live (T-011), workflow complet
recherche/save/capture/archive post-T-020.
