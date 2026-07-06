# T-041 — Écritures SQLite lourdes hors event loop

- **Statut** : todo
- **Priorité** : P2 · **Effort** : moyen
- **Outil recommandé** : Codex
- **Dépendances** : T-011 (la boucle tourne pendant les recherches — c'est là
  que le blocage devient visible)

## Objectif

Les opérations DB coûteuses ne bloquent plus la boucle asyncio (donc plus la
réactivité UI) : elles passent par `asyncio.to_thread`.

## Contexte

`InvestigationRepository` est synchrone (connexion par opération,
`investigations/repository.py:123-142`) et appelé depuis les coroutines de
`main.py`. Pendant `record_search` (insertion de dizaines de résultats),
`workspace_payload` (lecture complète d'une grosse enquête, appelée à chaque
itération de la boucle d'actions, `main.py:2432`) ou la régénération des
pages (`generate_investigation_page` sur tout le workspace), l'event loop est
gelé. WAL et `busy_timeout=5000` rendent le multi-thread sûr, chaque
opération ayant sa propre connexion.

Périmètre : **uniquement** les points chauds mesurés — pas de réécriture
async du repository.

## Fichiers concernés

- `main.py` : appels aux points chauds (`record_search` via
  `perform_search`, `workspace_payload`, `_generate_investigation_page`,
  `list_payload`/`_investigation_payload`).
- `investigations/service.py` : rien (reste sync) ; les wrappers
  `to_thread` vivent côté appelant.
- `tests/test_main.py`.

## Étapes

1. Mesurer d'abord : logguer la durée des 4 points ci-dessus sur une enquête
   réelle chargée (ou générée : 200 pages sauvées, 50 entités). Consigner.
2. Envelopper dans `asyncio.to_thread` ceux qui dépassent ~20 ms au p95.
3. Attention aux enchaînements lecture-modification : chaque appel threadé
   doit rester une opération repository complète (transaction incluse), pas
   une séquence entrecoupée.
4. `_investigation_payload` (json.dumps + sha256 du payload complet à chaque
   itération de boucle, `main.py:223-230`) : en plus du thread, mémoriser le
   résultat tant qu'aucune écriture DB n'a eu lieu (compteur de version
   incrémenté par le service à chaque mutation — simple entier en mémoire).
5. Re-mesurer, consigner le gain.

## Critères d'acceptation

- Aucune opération DB > 20 ms exécutée sur l'event loop dans le flux nominal
  (mesure instrumentée avant/après consignée).
- Comportement fonctionnel inchangé (suite complète verte).
- Pas d'accès concurrent à une même connexion sqlite (revue : les wrappers
  n'exposent que des méthodes repository complètes).

## Commandes de test

```powershell
.venv\Scripts\python.exe -m unittest tests.test_investigations tests.test_main
.venv\Scripts\python.exe -m unittest discover
```

## Risques

- Réordonnancement : deux actions rapides de l'utilisateur peuvent désormais
  s'entrelacer au niveau DB — WAL + transactions par opération le tolèrent ;
  si un handler dépend d'un ordre strict (save puis observe), garder ces
  enchaînements awaités séquentiellement dans le même handler.
- Sur-threading : ne pas threader les micro-lectures (< 1 ms), le coût du
  thread dépasserait le gain.
