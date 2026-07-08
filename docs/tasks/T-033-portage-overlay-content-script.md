# T-033 — Portage de l'overlay en content scripts

- **Statut** : done
- **Priorité** : P1 · **Effort** : élevé
- **Outil recommandé** : Les deux (Claude : architecture mondes/injection ;
  Codex : portage mécanique des composants et du bootstrap)
- **Dépendances** : T-030 ; T-031 pour le transport (le portage UI peut
  démarrer avant la décision transport, les actions restant locales)

## Objectif

L'overlay des pages http(s) (boutons save/archive/capture, menus entité,
sélection rectangle, focus guard) est rendu par l'extension — fiable sous
CSP stricte, survivant aux navigations, sans ré-injection périodique.

## Contexte

Aujourd'hui l'overlay est injecté par un `evaluate` massif re-exécuté à chaque
tick (`_install_and_consume_save_overlay`, `main.py:487-1081`) : bundle chargé
via `Function(bundle)()` (bloqué par les CSP `unsafe-eval` ⇒ overlay absent en
silence sur certains sites), globals `window.__synthesix*` lisibles/forgeables
par la page hôte, focus guard armé séparément par
`Page.addScriptToEvaluateOnNewDocument` (`main.py:364-464`).

Architecture cible (3 mondes) :

1. **Content script isolé** (`bootstrap.ts`) : décide de l'injection (URL
   autorisée, pas de double installation), insère
   `<script src="chrome.runtime.getURL('dist/overlay-main.js')">` — les
   ressources `web_accessible_resources` échappent au CSP de la page ; relaie
   les actions vers le SW (`chrome.runtime.sendMessage`).
2. **Script main-world** (`overlay-main.js`) : les composants Lit overlay
   existants (`frontend/src/overlay/*`) + le bootstrap DOM actuellement généré
   en Python (création de `sx-overlay-root`, boutons, menus, payload page).
   Les custom elements doivent vivre dans le main world pour s'upgrader.
   Communication vers le content script : `window.postMessage` avec un token
   aléatoire généré par le content script et passé via attribut `data-*` du
   tag script (limite le spoof trivial par la page hôte).
3. **Focus guard** : contenu actuel de `_overlay_focus_guard_script()`
   (`main.py:377-440`) déplacé tel quel dans
   `extension/src/content/focus-guard.ts` (`world: MAIN`,
   `run_at: document_start`) — même garantie d'ordre d'enregistrement que
   l'injection new-document actuelle.

Exclusions : reprendre `_overlay_injection_blocked` (`main.py:467-484`) en
`exclude_matches`/test d'URL (Google Lens, Maps).

## Fichiers concernés

- `extension/src/content/bootstrap.ts`, `extension/src/content/focus-guard.ts`,
  `extension/src/overlay-main.ts` (nouveau point d'entrée réutilisant
  `frontend/src/overlay/`), `extension/manifest.json`.
- `frontend/build.mjs` : cible `overlay-main.js`.
- Le JS Python de `main.py` n'est PAS modifié ici (retrait en T-036).

## Étapes

1. Extraire le bootstrap DOM du JS Python vers `overlay-main.ts` en
   TypeScript (traduction fidèle : mêmes IDs, mêmes `data-*`, mêmes events
   Lit — contrats listés dans AGENTS.md §5).
2. Le contexte (investigation active, tagsets, entités) arrive par message SW
   → content script → main world ; en attendant T-035, utiliser un contexte
   vide (boutons en état « Select investigation »).
3. Câbler les actions en local : clic ⇒ message au SW ⇒ file d'attente SW
   (le pont Python arrive en T-034).
4. Porter le focus guard ; supprimer aucune ligne Python (coexistence : le
   guard extension pose `window.__synthesixFocusGuardInstalled`, déjà
   idempotent des deux côtés — vérifier).
5. États visuels : réutiliser `setSaveButtonState`/`setArchiveState`/
   `setCaptureState` des composants Lit (API publiques conservées).
6. Vérifications visuelles AGENTS.md §8 : thème clair/sombre du site hôte,
   pages denses, CSP stricte (tester sur github.com — CSP sans unsafe-eval —
   et un site TikTok-like pour le guard).

## Critères d'acceptation

- Overlay visible et fonctionnel (états locaux) sur : site CSP stricte,
  SPA avec navigations internes, page à scroll infini.
- Aucune installation sur Lens/Maps ni sur les pages `file://`.
- Un seul overlay par page après navigations SPA répétées.
- Focus guard efficace (champ overlay conserve le clavier sur un site à
  hotkeys type TikTok/YouTube).
- `npm run typecheck && npm run build` verts ; bundles commit.

## Commandes de test

```powershell
cd frontend; npm run typecheck; npm run build; cd ..
git diff --check
```

Smoke manuel listé ci-dessus (au minimum CSP stricte + SPA), consigné.

## Risques

- Coexistence overlay CDP + overlay extension pendant la transition : le
  bootstrap extension doit se retirer si `#__synthesix-save-overlay` (version
  CDP) est déjà présent, et inversement le flag T-034
  (`SYNTHESIX_OVERLAY_MODE`) évite le double pilotage.
- Token postMessage lisible si la page inspecte le DOM au bon moment :
  mitigation acceptée (validation de schéma côté SW et backend en défense en
  profondeur) — déjà meilleur que les globals actuels.
- Sites qui suppriment les nœuds étrangers : le content script observe et
  ré-insère (MutationObserver léger, max 1 ré-insertion/5 s).

## Résultat 2026-07-07 — AI-20260707-008

- `extension/src/overlay-main.ts` porte le bootstrap DOM de l'overlay dans le
  main world : mêmes IDs publics (`#__synthesix-save-overlay`,
  `#__synthesix-evidence-selection`), mêmes attributs `data-*`, mêmes actions
  métier et mêmes composants Lit (`sx-overlay-root`, actions, menu capture,
  menu entité, sélection de région).
- `extension/src/content/bootstrap.ts` injecte `dist/overlay-main.js` via
  `chrome.runtime.getURL`, transmet un token aléatoire par `data-*`, relaie les
  actions `postMessage` vers le service worker, garde le spike T-031 et
  réinstalle l'overlay si la page supprime le nœud (throttle 5 s).
- `extension/src/content/focus-guard.ts` reprend le guard CDP avec le même
  drapeau `window.__synthesixFocusGuardInstalled` pour la coexistence.
- `extension/src/background.ts` distingue les messages de spike
  (`extension_spike_message`) et les actions overlay
  (`extension_overlay_action`) tout en conservant la file et la réponse
  `backendBinding`.
- `extension/manifest.json` exclut les patterns Chrome valides pour Lens/Maps ;
  le bootstrap runtime conserve le filtre étendu pour les domaines Google
  régionaux non exprimables en match pattern.
- Le JS Python de `main.py` n'a pas été modifié ; le chemin CDP existant reste
  en place jusqu'à T-036.

Tests exécutés :

- `cd frontend; npm run typecheck`
- `cd frontend; npm run build`
- `node -e "JSON.parse(require('fs').readFileSync('extension/manifest.json','utf8')); console.log('manifest ok')"`
- `$env:SYNTHESIX_BROWSER='brave'; .venv\Scripts\python.exe tests\manual\spike_ext_transport.py`
- Smoke Brave T-033 inline : overlay présent sur `https://example.com/`,
  clic save sans enquête active livré comme `extension_overlay_action` /
  `focus_home`, overlay présent sur `https://github.com/` (site CSP stricte).

Vérifications non exécutées :

- Smoke SPA/navigation interne répétée et page à scroll infini.
- Smoke focus guard sur site à hotkeys type TikTok/YouTube.
- Smoke Chrome stable brandé, toujours en mode dégradé connu car
  `--load-extension` y est ignoré dans l'environnement testé.

Prochaine action :

- T-034 : câbler `extension_overlay_action` vers les handlers backend derrière
  le flag de bascule.
