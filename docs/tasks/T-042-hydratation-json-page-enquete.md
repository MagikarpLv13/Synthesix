# T-042 — Page enquête hydratée par workspace.json

- **Statut** : todo
- **Priorité** : P2 · **Effort** : élevé (découper en sous-lots a/b/c)
- **Outil recommandé** : Les deux (Claude : architecture + backend ;
  Codex : conversions mécaniques côté vue)
- **Dépendances** : T-021 (push local) recommandé ; indépendant de la phase 3

## Objectif

Les actions d'enquête ne régénèrent plus la page HTML complète (5 400 lignes
de générateur, workspace entier relu et re-rendu) : la page charge un
`workspace.json` adjacent et se re-rend côté client (composants Lit déjà en
place). La régénération HTML complète ne reste que pour la création initiale
et les migrations de gabarit.

## Contexte

Chaque action (save, note, entité, suppression…) appelle
`_refresh_investigation_page_file` (`main.py:2105-2124`) →
`generate_investigation_page` (`investigations/view.py:2655+`) qui relit tout
le workspace et réécrit tout le HTML ; beaucoup d'actions font ensuite
`tab.reload()` (perte de scroll/état, flash visuel — les actions « no-reload »
ont déjà été introduites pour une partie, voir worklog AI-20260622-013/016).
Coût O(taille enquête) par action, UX dégradée sur les grosses enquêtes.

Cible :
- `data/investigation_pages/<id>.html` : coquille stable (layout, scripts,
  i18n) générée rarement ;
- `data/investigation_pages/<id>.workspace.json` : données, réécrites à chaque
  mutation (écriture atomique comme `evidence/capture.py:_write_atomic`) ;
- la page fetch le JSON au chargement (`fetch` relatif fonctionne en
  `file://` ? **Non** — fetch/XHR sur `file:` est bloqué ; utiliser un
  `<script src="….workspace.js">` classique définissant
  `window.__synthesixWorkspace = {...}` — même mécanisme que les bundles,
  compatible avec la règle « script classique sans type=module ») ;
- après une mutation, le backend pousse un événement léger « workspace v+1 »
  (T-021) ; la page recharge le script de données (insertion d'un nouveau tag
  script versionné) et re-rend — sans `tab.reload()`.

## Fichiers concernés

- `investigations/view.py` : scission gabarit / données (sous-lot a : émettre
  `workspace.js` + faire consommer les données par le rendu client existant).
- `main.py` : `_refresh_investigation_page_file` écrit `workspace.js` seul ;
  `_open_or_refresh_investigation_page` remplace `reload()` par le push léger
  quand la page le supporte (détection de capacité via marqueur de version de
  gabarit dans le DOM).
- `frontend/src/` : composants — la plupart consomment déjà des données
  passées par attributs/propriétés ; sous-lot b : point d'entrée de re-rendu.
- `tests/test_investigation_view.py`.

## Étapes

1. **a** : générer `workspace.js` à côté du HTML ; le HTML le charge et le
   rendu initial l'utilise (parité totale, reload encore utilisé).
2. **b** : re-rendu client sur nouvelle version des données (sans reload) pour
   les sections déjà « no-reload » ; étendre progressivement.
3. **c** : basculer les actions restantes ; `tab.reload()` ne survit que pour
   les changements de gabarit (version de gabarit embarquée, comparée).
4. Vérifications visuelles AGENTS.md §8 (clair/sombre/vide/dense) à chaque
   sous-lot.

## Critères d'acceptation

- Une action « note » sur une enquête de 200 pages sauvées réécrit < 5 % des
  octets actuellement réécrits (mesurer : taille HTML vs JSON).
- Scroll et état UI conservés après chaque action migrée.
- Une page ouverte avec un ancien HTML (gabarit périmé) déclenche un reload
  propre — pas d'écran cassé.
- Suite `test_investigation_view` adaptée et verte.

## Commandes de test

```powershell
.venv\Scripts\python.exe -m unittest tests.test_investigation_view
cd frontend; npm run typecheck; npm run build; cd ..
```

Smoke visuel par sous-lot (thèmes, densité), consigné.

## Risques

- Gros chantier : la discipline des sous-lots a/b/c est bloquante ; chaque
  sous-lot livre un état stable committable.
- Divergence gabarit/données : gérée par la version de gabarit (étape 3).
- Contrat `window.synthesixPage` : inchangé — les actions continuent de
  passer par lui (AGENTS.md §5).
