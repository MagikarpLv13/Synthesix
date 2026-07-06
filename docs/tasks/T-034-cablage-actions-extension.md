# T-034 — Câblage actions extension → backend (flag de bascule)

- **Statut** : todo
- **Priorité** : P1 · **Effort** : moyen-élevé
- **Outil recommandé** : Claude
- **Dépendances** : T-031 (décision transport), T-032 (chargement + ID),
  T-033 (overlay émettant des actions)

## Objectif

Les actions overlay (save, archive, capture, entités, focus_home) émises par
l'extension parviennent au dispatcher Python existant, sous le contrôle du
flag `SYNTHESIX_OVERLAY_MODE=cdp|extension|auto`.

## Contexte

Le backend consomme aujourd'hui les actions overlay via le retour de
`_install_and_consume_save_overlay` dans `wait_for_home_action`
(`main.py:2339-2355`), puis les traite dans le `while` de `main()` (handlers
`save_page_to_investigation`, `archive_page_to_investigation`,
`capture_evidence_to_investigation`, `create_graph_entity_from_selection`,
`attach_selection_to_graph_entity`, `observe_saved_page`, `focus_home`).
**Les handlers ne changent pas** : seule la source des actions change.

Transport selon décision T-031 (option A attendue : binding CDP sur le SW).
Les actions doivent porter l'identité du tab source (`tabId` Chrome côté SW)
que le backend mappe vers son target CDP pour les réponses ciblées (statuts,
capture sur le bon tab).

## Fichiers concernés

- `extension/src/background.ts` : file d'actions, appel du binding, champ
  `tabId` + `url` par action.
- `browser/service.py` (ou `main.py` si T-020/021 pas encore passés —
  documenter l'ordre réel à l'exécution) : attache au SW, réception,
  conversion en actions du dispatcher avec résolution `tabId → tab CDP`
  (correspondance par URL + ordre d'ouverture ; via
  `Target.getTargets`/`targetInfo` — les target ids CDP et tab ids extension
  diffèrent, prévoir la table de correspondance).
- `main.py` : sélection de la source selon `SYNTHESIX_OVERLAY_MODE` ;
  en mode `extension`, `_install_and_consume_save_overlay` n'est plus appelé
  (le poll overlay disparaît du tick) ; en mode `auto`, extension si détectée
  (T-032), sinon chemin CDP actuel.
- `settings.py` : le flag.
- `tests/test_main.py` + tests dédiés du mapping.

## Étapes

1. Contrat de message : réutiliser tel quel le schéma d'action existant
   (mêmes clés `action`, `investigationId`, `page`, `selection`…, AGENTS.md
   §5) + enveloppe `{v: 1, tabId, url, action: {...}}`.
2. SW : file locale persistée en `chrome.storage.session` (survit au sommeil
   du SW), vidée à l'acquittement backend.
3. Backend : réception (binding ou poll SW selon T-031), validation stricte
   (schéma, types, URL http/https, taille bornée), résolution du tab source,
   injection dans le flux d'actions existant.
4. Réponses : les statuts (`_set_save_overlay_status` etc.) passent par le
   canal inverse minimal — pour cette tâche, message SW → content script
   « ack/erreur » basique ; les états riches arrivent en T-035.
5. Flag + mode `auto` ; les deux chemins testés.
6. Smoke complet en mode `extension` : save, archive, capture viewport,
   capture région, création d'entité, depuis 2 tabs différents.

## Critères d'acceptation

- Mode `extension` : les 6 types d'action aboutissent (DB/preuves identiques
  au mode CDP, vérifié sur une investigation de test).
- La capture s'exécute sur le bon tab quand 2 tabs sont ouverts sur le même
  domaine.
- Sommeil du SW : une action émise après 2 min d'inactivité n'est pas perdue.
- Mode `cdp` : strictement inchangé.
- Actions malformées (fuzz simple) : rejetées + log, pas d'exception.

## Commandes de test

```powershell
.venv\Scripts\python.exe -m unittest tests.test_main
.venv\Scripts\python.exe -m unittest discover
```

Smoke réel obligatoire (liste ci-dessus), consigné avec versions navigateur.

## Risques

- Mapping tabId↔target ambigu (2 tabs même URL) : lever l'ambiguïté par
  l'ordre targetInfo/openerId, sinon marquer le tab via un token éphémère posé
  par le content script et lu une fois côté CDP (dernier recours).
- Si T-031 conclut option C (poll SW) : latence identique à aujourd'hui mais
  1 seule cible — le reste de la tâche est inchangé.
- Validation d'entrée : l'extension réduit la surface de spoof mais le backend
  garde la validation stricte (défense en profondeur, données OSINT hostiles).
