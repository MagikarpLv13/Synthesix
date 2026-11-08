# T-012 — Attente moteurs par evaluate composite

- **Statut** : done (2026-07-06, Claude)
- **Priorité** : P1 · **Effort** : moyen
- **Outil recommandé** : Claude
- **Dépendances** : T-006 (mesure avant/après)

## Objectif

Réduire chaque itération d'attente moteur à **un seul** `Runtime.evaluate`
léger, et ne rapatrier le HTML complet qu'une fois la page prête. Supprimer
les `get_content()` (page entière) exécutés en boucle.

## Contexte

- `SearchEngine.wait_for_page_load` (`search_engine.py:210-230`) : poll
  `query_selector` toutes les 100 ms.
- DDG `_wait_for_result_content` (`duckduckgo.py:287-335`) : par itération,
  `query_selector` + éventuellement `read_page_content()` = `tab.get_content()`
  (DOM.getOuterHTML complet, potentiellement des Mo) toutes les ~0,5 s, suivi
  d'un parse lxml complet — jusqu'à ~20 fois par attente.
- Brave `_wait_for_results_container` (`brave.py:245-257`) : poll jusqu'à 45 s.
- Détection de challenge faite côté Python sur le HTML rapatrié alors qu'un
  `document.querySelector` côté page suffit pour les marqueurs DOM.

## Fichiers concernés

- `search_engine.py` : nouvelle méthode `probe_page_state()` + réécriture de
  `wait_for_page_load` sur cette base.
- `duckduckgo.py` : `_wait_for_result_content`,
  `_wait_for_manual_challenge_resolution` (marqueurs DOM côté JS).
- `brave.py` : `_wait_for_results_container`.
- `tests/test_engines.py`, `tests/test_search_engine_errors.py`.

## Étapes

1. Définir un probe JS unique paramétré par moteur, retournant un petit objet :
   `{found: bool, ready: document.readyState, bodyLength: int,
   challenge: bool, noResults: bool}`. Les sélecteurs de challenge/no-results
   par moteur sont fournis par une méthode `get_probe_markers()` (DDG :
   `.anomaly-modal`, titre 403 ; Brave : chemin `/captcha`, `blockRobots` via
   `document.documentElement.innerHTML.includes` limité — préférer des
   sélecteurs DOM quand ils existent).
2. Réécrire les boucles d'attente : un `evaluate(probe)` par itération ;
   `get_content()` uniquement quand `found` (pour parser) ou à la sortie en
   erreur (pour la capture debug/challenge existante).
3. Conserver les seuils/timeouts actuels (comportement inchangé, seul le coût
   par itération change). Le passage aux événements `Page.loadEventFired`
   reste hors périmètre (viendra avec T-020 si utile).
4. Mettre à jour les captures debug (`capture_debug_html`) pour qu'elles
   restent déclenchées aux mêmes moments qu'avant (résultats, timeout,
   challenge).
5. Mesure avant/après avec T-006 (`eval_engine_wait`, `get_content`) sur une
   recherche réelle 4 moteurs ; consigner les chiffres.

## Critères d'acceptation

- Plus aucun `get_content()` dans une boucle d'attente (grep dans les boucles).
- Comportements préservés : détection challenge DDG/Brave, fallback endpoint
  HTML DDG, arrêt anticipé « no results ».
- Tests moteurs verts ; mesure consignée (appels et octets par attente ↓).

## Commandes de test

```powershell
.venv\Scripts\python.exe -m unittest tests.test_engines tests.test_search_engine_errors
```

Smoke réel : une recherche 4 moteurs, vérifier logs + rapport généré.

## Risques

- Marqueurs de challenge détectés aujourd'hui sur le HTML brut (regex texte)
  pas tous exprimables en sélecteurs : garder pour ces cas un
  `document.body.innerText.slice(0, 20000)` retourné par le probe quand
  `found=false` depuis > N itérations, plutôt que le HTML complet.
- Divergence probe/parse (le probe dit prêt, le parse ne trouve rien) :
  conserver la boucle de re-tentative existante.

## Réalisation (2026-07-06)

- `search_engine.py` : `probe_page_state()` (un `Runtime.evaluate` par
  itération, retour JSON ≤ ~400 octets : `found`, `ready`, `body_length`,
  `result_count`, `challenge`, `forbidden`, `no_results`, `url`, `title`,
  `text` optionnel tronqué à 20 000 caractères), marqueurs par moteur via
  `get_probe_markers()`, constante `PROBE_MARKER` pour identifier les
  probes ; `wait_for_page_load` réécrit sur le probe.
- `duckduckgo.py` : `_wait_for_result_content` et
  `_wait_for_manual_challenge_resolution` sans `get_content()` en boucle
  (challenge = sélecteurs `.anomaly-modal` + textes visibles ; forbidden =
  titre exact `403 forbidden`/`forbidden` ; arrêt anticipé « no results »
  conservé) ; la capture follow-up ne lit le HTML qu'au moment du 403.
  `_wait_for_additional_results` : lecture de page seulement quand
  `result_count` change (pagination).
- `brave.py` : `_wait_for_results_container` sur le probe ; marqueurs
  `/captcha` (pathname) et `blockRobots` (`innerHTML` borné à 200 000).
- Le parse en boucle DDG (page parseable sans sélecteur correspondant) est
  supprimé : le sélecteur couvre les trois familles de markup, et le repli
  endpoint HTML reste le filet.
- **Mesure** : avant = 1 `query_selector` / itération + `get_content()`
  complet (DOM entier, potentiellement des Mo) toutes les ~0,5 s côté DDG ;
  après = 1 evaluate / itération (script ~2,7-3 Ko envoyé, JSON ~0,35 Ko
  reçu), `get_content()` uniquement à `found`, au timeout ou au challenge.
  Octets reçus par attente : suivis via `observe_bytes("eval_engine_wait")`.
  Probe validé dans un vrai DOM (Chrome headless, 9 scénarios
  found/challenge/no-results/forbidden DDG+Brave). Mesure live 4 moteurs
  (`--verbose`, dump T-006) à consigner au premier run interactif réel.
