# T-042 — Page enquête hydratée par workspace.json

- **Statut** : done
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

## Résultat — sous-lot a (2026-07-10)

- Chaque page d'enquête génère maintenant un script adjacent
  `<id>.workspace.js`, écrit atomiquement, qui définit
  `window.__synthesixWorkspace` et est chargé par script classique depuis la
  coquille HTML. Ce mécanisme reste compatible avec les pages `file://`.
- Les actions déjà sans rechargement n'écrivent plus la coquille HTML : elles
  mettent à jour le script de données seul. La création de page et les actions
  qui rechargent encore conservent la génération complète, donc la parité
  visuelle actuelle est préservée.
- Le gabarit annonce sa capacité via
  `data-synthesix-workspace-template="1"`. Le re-rendu client sur nouvelle
  version de données et la suppression de `tab.reload()` restent les objectifs
  des sous-lots b/c.

## Résultat — sous-lot b1 (2026-07-10)

- Chaque sauvegarde déjà sans rechargement incrémente une révision du workspace,
  met à jour le script adjacent puis pousse un appel CDP léger vers l'onglet
  source. Le script est rechargé avec un paramètre de version, sans navigation
  et donc sans perte du scroll ou de l'état de l'inspecteur.
- Le gabarit expose maintenant `window.synthesixPage.reloadWorkspace(version)`.
  Après chargement, il met à jour les métriques de synthèse et émet l'événement
  `synthesix-workspace-update` avec les nouvelles données et leur version.
- Les sections détaillées conservent encore leur mise à jour optimiste
  existante ; elles seront progressivement re-rendues à partir de cet événement
  dans le sous-lot b2.

## Résultat — sous-lot b2a (2026-07-10)

- Les propriétés d'entité sont la première section détaillée réconciliée à
  partir du workspace : chaque ligne porte désormais sa clé stable. Au
  chargement initial comme lors de `synthesix-workspace-update`, les propriétés
  absentes sont retirées, les valeurs sont actualisées et les propriétés
  manquantes sont ajoutées.
- Une suppression suivie d'un refresh ne réaffiche donc plus la propriété
  provenant de la coquille HTML périmée.

## Résultat — sous-lot b2b (2026-07-10)

- La même réconciliation supprime maintenant, au chargement et après push, les
  éléments absents du workspace : pages enregistrées, propriétés extraites,
  entités, preuves, exports et moniteurs. Les compteurs exports/moniteurs et
  preuves associés sont recalculés.
- Les mutations non destructives détaillées (relations, métadonnées et états
  d'entités extraites) restent à re-rendre entièrement avant la clôture de la
  tâche : T-042 demeure donc `in_progress`.

## Résultat — sous-lot b2 final (2026-07-10)

- Les résultats, métadonnées/tags des entités, relations, états et métadonnées
  des propriétés extraites sont maintenant réconciliés avec le workspace à
  l'ouverture et après une mutation sans rechargement.
- Le workspace est compacté en gzip dans le script classique, puis décompressé
  par `DecompressionStream` côté Chromium. Mesure synthétique sur 200 pages :
  HTML 1 390 744 octets, workspace 6 803 octets (0,49 %) — le critère `< 5 %`
  est atteint.
- Le script est exécuté dans Node pendant les tests afin de vérifier la vraie
  décompression et l'hydratation du payload. Reste le smoke visuel/CDP sur une
  enquête réelle avant passage `done`.

## Validation finale (2026-07-10)

- Smoke utilisateur exécuté et approuvé : les mutations et les refreshs de
  page se comportent correctement. T-042 est clôturée.
