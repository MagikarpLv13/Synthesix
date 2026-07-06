# T-013 — Parsing Brave : chaîne JSON → XPath

- **Statut** : done
- **Priorité** : P1 · **Effort** : faible
- **Outil recommandé** : Codex
- **Dépendances** : T-015 recommandé (fixtures), pas bloquant

## Objectif

Le moteur Brave ne doit plus dépendre d'un seul motif regex sur le bundle
minifié de Brave Search : ajouter un repli DOM et un signal clair quand les
deux échouent.

## Contexte

`brave.py:154-182` : `parse_results` extrait les résultats via la regex
`results:\s*\[\{(.*?)\}\],bo` — le suffixe `],bo` est un identifiant minifié
du bundle Brave, qui change à chaque rebuild de leur frontend. Un parseur DOM
existe déjà (`parse_results_old` + `get_xpaths`, `brave.py:135-152`) mais
n'est plus branché. `js_like_to_json` (`utils.py:332`) est lui-même fragile
(quoting par regex).

## Fichiers concernés

- `brave.py` : `parse_results`.
- `tests/test_engines.py` (fixtures HTML Brave réelles — voir T-015).

## Étapes

1. Renommer le chemin regex actuel en `_parse_results_embedded_json` et
   assouplir la regex de fin (`\}\],\s*[a-zA-Z_$]{1,3}` au lieu de `}],bo`).
2. `parse_results` : essayer JSON embarqué ; si 0 résultat, tenter
   `parse_results_old` (XPath) ; consigner en `logger.warning` quel chemin a
   servi quand ce n'est pas le chemin nominal.
3. Vérifier que `nb_results_per_page`/`num_results` (utilisés par la
   pagination `post_execute_search`) sont correctement alimentés dans les deux
   chemins.
4. Ajouter deux fixtures : une page Brave actuelle (chemin JSON) et une page
   où le motif JSON est absent (chemin XPath).

## Critères d'acceptation

- Sur la fixture « motif absent », le moteur retourne quand même des résultats
  via XPath au lieu de 0.
- Le chemin utilisé est visible dans les logs en cas de repli.
- Pagination Brave inchangée sur le chemin nominal.

## Commandes de test

```powershell
.venv\Scripts\python.exe -m unittest tests.test_engines
```

## Risques

- Les XPaths `snippet`/`title` de `parse_results_old` peuvent être eux-mêmes
  datés : les vérifier contre la fixture récente et les ajuster dans cette
  tâche (rester minimal).
- Doublons entre les deux chemins : non concerné, un seul chemin est utilisé
  par page.

## Résultat 2026-07-06

- `parse_results` tente d'abord le bloc JSON embarqué via
  `_parse_results_embedded_json`, avec suffixe minifié assoupli.
- Si ce chemin retourne 0 résultat, Brave bascule sur le parser XPath et
  consigne le chemin de repli en `warning`.
- `num_results` et `nb_results_per_page` sont alimentés sur les deux chemins.
- Fixtures ajoutées : `brave_2026-06.html` (JSON) et
  `brave_xpath_2026-06.html` (fallback XPath).
