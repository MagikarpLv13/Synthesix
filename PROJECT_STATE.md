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
| 1 | Recherche robuste (deadline globale, non-bloquante, attentes optimisées, parsing durci) | en cours (T-010, T-011, T-013, T-015 done ; T-012/T-014 à faire) |
| 2 | BrowserService + push CDP pour pages locales | à faire |
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

Phase 1 : T-012 (attente moteurs composite, Claude) est la prochaine action
prioritaire ; T-014 (pool de tabs moteurs) reste disponible ensuite. T-050,
T-010, T-011, T-013 et T-015 sont livrés.
