# T-015 — Golden files de parsing par moteur

- **Statut** : todo
- **Priorité** : P1 · **Effort** : faible-moyen
- **Outil recommandé** : Codex (collecte des fixtures : Claude ou l'utilisateur)
- **Dépendances** : aucune

## Objectif

Chaque parseur moteur est testé contre des pages HTML réelles archivées
(« golden files »). Toute casse future d'un moteur devient une fixture de
non-régression au lieu d'un bug silencieux.

## Contexte

Les parseurs dépendent de structures fragiles : Google
(`.//div[@jscontroller][@data-ved][@data-hveid]`, `google.py:37-43`), Brave
(regex bundle, `brave.py:155`), DDG (3 variantes de layout,
`duckduckgo.py:108-142`), Bing (`b_algo`, redirects `/ck/a`). Les tests
actuels (`tests/test_engines.py`) ne couvrent pas des pages complètes datées.
`SYNTHESIX_DEBUG_HTML=1` (`--debug-html`) sait déjà capturer les pages
réelles dans `history/debug_pages/`.

## Fichiers concernés

- Nouveau : `tests/fixtures/engines/<moteur>_<AAAA-MM>.html` (pages
  anonymisées : vérifier absence de cookies/tokens dans le HTML avant commit —
  règle sécurité AGENTS.md §10).
- `tests/test_engine_golden.py` (nouveau).
- `docs/tasks/README.md` : rien ; procédure de rafraîchissement documentée
  dans le test lui-même.

## Étapes

1. Collecter une page de résultats réelle par moteur via `--debug-html`
   (requête neutre, ex. "open source intelligence"). Nettoyer tout élément
   personnel (la page est du HTML public, mais vérifier).
2. Écrire `test_engine_golden.py` : pour chaque fixture,
   `engine.parse_results(html)` retourne ≥ 5 résultats, chacun avec `title`,
   `link` http(s), `description`, `source` ; liens Bing dé-wrappés
   (`resolve_bing_redirect`) ; liens DDG nettoyés (`uddg`).
3. Documenter en tête du test la procédure de rafraîchissement d'une fixture
   quand un moteur change (capture + remplacement + date dans le nom).
4. Intégrer à la suite standard (aucune dépendance réseau).

## Critères d'acceptation

- 4 fixtures commit (une par moteur), datées dans le nom de fichier.
- Test vert hors ligne, < 5 s.
- Casser volontairement un XPath fait échouer le test du moteur concerné
  uniquement.

## Commandes de test

```powershell
.venv\Scripts\python.exe -m unittest tests.test_engine_golden
```

## Risques

- Fixtures volumineuses (~500 Ko-1 Mo/page) : acceptable ; si le dépôt doit
  rester léger, tronquer aux 200 premiers résultats DOM sans casser la
  structure.
- Golden files figent un instantané : ils détectent les régressions de *nos*
  parseurs, pas les changements côté moteur — c'est le rôle du repli T-013 et
  des statuts de couverture.
