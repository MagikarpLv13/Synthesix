# T-036 — Bascule par défaut + retrait de l'overlay CDP

- **Statut** : todo
- **Priorité** : P1 · **Effort** : moyen
- **Outil recommandé** : Les deux (Claude : bascule + smoke ; Codex : retrait
  mécanique du code mort)
- **Dépendances** : T-034 et T-035 validés par smoke réel + au moins une
  semaine d'usage quotidien en mode `extension` sans régression signalée

## Objectif

Faire de l'extension le chemin par défaut, puis supprimer le chemin overlay
CDP de `main.py` (~800 lignes) et ses béquilles. `main.py` ne pilote plus
aucune page http(s) par evaluate en régime nominal.

## Contexte

Après T-034/T-035, deux implémentations coexistent derrière
`SYNTHESIX_OVERLAY_MODE`. La coexistence a un coût (double maintenance des
contrats overlay, AGENTS.md §5) : ce retrait est planifié, pas optionnel.
Reste un cas dégradé : extension indisponible (Chrome stable sans install
manuelle) ⇒ bannière d'instructions (T-032), pas de retour au chemin CDP.

## Fichiers concernés

- `settings.py` : défaut `SYNTHESIX_OVERLAY_MODE=auto` → `extension`
  (le flag reste une session le temps de la transition, retiré ensuite).
- `main.py` — suppression :
  - `_install_and_consume_save_overlay` (`main.py:487-1081`) ;
  - `_set_save_overlay_status`, `_set_evidence_overlay_status`,
    `_set_archive_overlay_status` (`main.py:1084-1179`) ;
  - `_overlay_focus_guard_script`, `_arm_overlay_focus_guard`,
    `_OVERLAY_FOCUS_GUARD_ARMED_TARGETS` (`main.py:356-464`) — le guard vit
    dans l'extension (T-033) ;
  - la branche overlay du tick dans `wait_for_home_action`
    (`main.py:2339-2346`) ;
  - `_overlay_injection_blocked` (`main.py:467-484`) — la liste vit dans le
    manifest (`exclude_matches`).
- `assets/synthesix-overlay.js` : ne plus l'embarquer dans `main.py`
  (`_overlay_bundle_script`, `main.py:74-79`) ; vérifier s'il reste consommé
  ailleurs, sinon retirer la cible de build correspondante.
- `tests/` : retirer/adapter les tests du chemin CDP ; conserver les tests de
  contrat d'action (ils testent le dispatcher, indépendant de la source).
- `AGENTS.md` §5 : mettre à jour la liste des contrats
  (`window.__synthesixSavePageAction` disparaît, contrats extension ajoutés).
- `PROJECT_STATE.md`, `AI_WORKLOG.md` : clôture de la phase 3.

## Étapes

1. Basculer le défaut, une semaine d'usage réel (critère d'entrée ci-dessus
   déjà rempli ⇒ formalité).
2. Supprimer le code listé, en un seul lot cohérent, diff relu.
3. Chasse aux références mortes : grep `__synthesix`, `SynthesixOverlay`,
   `synthesix-overlay` dans `main.py`, `tests/`, docs.
4. Mesure finale T-006 : plus aucun `eval_overlay` ; consigner le delta global
   depuis la mesure de référence.
5. Mise à jour AGENTS.md §5 + docs.

## Critères d'acceptation

- `wait_for_home_action` ne touche plus jamais un tab http(s).
- Suite complète verte ; `git diff --check` propre.
- Smoke complet (save/archive/captures/entités/statuts/focus guard) en mode
  extension sur Brave + un navigateur secondaire.
- `main.py` réduit d'au moins 700 lignes (indicateur, pas objectif en soi).

## Commandes de test

```powershell
cd frontend; npm run typecheck; npm run build; cd ..
.venv\Scripts\python.exe -m unittest discover
git diff --check
```

## Risques

- Suppression prématurée : le critère d'entrée (une semaine d'usage réel)
  est bloquant — ne pas céder à la tentation de fusionner T-034/035/036.
- Utilisateurs Chrome stable sans extension : mode dégradé assumé (save
  possible via la home ? non — documenter clairement la dépendance à
  l'extension pour le workflow pages externes dans README).
