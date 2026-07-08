# T-032 — Chargement de l'extension par Synthesix

- **Statut** : done
- **Priorité** : P1 · **Effort** : faible-moyen
- **Outil recommandé** : Claude
- **Dépendances** : T-030

## Objectif

`python main.py` charge l'extension automatiquement quand c'est possible,
détecte sa présence au démarrage, et guide l'utilisateur pour l'installation
unpacked persistante quand le chargement automatique n'est pas disponible.

## Contexte

Deux mécanismes, à combiner :

1. **Flags de lancement** : `--load-extension=<chemin extension/>` (+
   éventuellement `--disable-extensions-except=...`). Fonctionne sur Brave et
   Chromium ; **retiré de Chrome brandé stable ≥ 137** (mi-2025). Synthesix
   supporte les deux navigateurs (`browser_manager.py`, `BROWSER_COMMANDS`).
2. **Installation unpacked persistante** : le profil `zendriver-profile/` est
   persistant ; une installation manuelle unique via chrome://extensions
   (mode développeur) survit aux redémarrages. C'est le repli pour Chrome
   stable.

La détection de présence est indispensable dans les deux cas : sans
extension, Synthesix doit rester utilisable (mode dégradé : overlay CDP tant
que T-036 n'est pas fait ; ensuite, bannière d'instructions).

## Fichiers concernés

- `browser_manager.py` : ajout des flags via `Config.add_argument` (vérifier
  l'API zendriver 0.15.3) ; chemin extension résolu depuis `settings`.
- `settings.py` : `extension_dir` (défaut `extension/`),
  `SYNTHESIX_EXTENSION_MODE=auto|off` (off = comportement actuel).
- `main.py` (ou `browser/service.py` si T-020 est passé) : détection
  post-démarrage — un target `chrome-extension://` correspondant existe, ou
  marqueur `dataset.synthesixExt` présent après ouverture d'une page http(s)
  de test ; statut home informatif sinon.
- `extension/README.md` : procédure d'installation manuelle illustrée.
- `tests/test_browser_manager.py`.

## Étapes

1. Ajouter les flags au démarrage quand `extension/dist/manifest`… est présent
   et `SYNTHESIX_EXTENSION_MODE=auto`.
2. Implémenter la détection de présence (côté targets de préférence : pas
   besoin d'ouvrir une page) ; exposer `extension_available: bool`.
3. Message utilisateur clair quand absente : statut home avec lien vers la
   procédure (`extension/README.md`), une seule fois par session.
4. Vérifier l'ID d'extension : ID stable requis pour T-031/T-034 (dérivé du
   chemin pour une unpacked ; fixer un `key` dans `manifest.json` pour un ID
   déterministe — à faire ici).
5. Tests : flags présents/absents selon le mode ; détection simulée.
6. Smoke réel sur Brave (flag) et si possible Chrome stable (repli manuel) ;
   consigner les versions testées.

## Critères d'acceptation

- Brave/Chromium : extension active sans aucune action utilisateur.
- Chrome stable ≥ 137 : message d'installation clair, app fonctionnelle sans
  extension.
- `key` fixé ⇒ ID d'extension identique sur toutes les machines.
- `SYNTHESIX_EXTENSION_MODE=off` restaure exactement le comportement actuel.

## Commandes de test

```powershell
.venv\Scripts\python.exe -m unittest tests.test_browser_manager
```

Smoke réel : démarrage sur Brave (auto) + vérification détection.

## Risques

- Restrictions futures des navigateurs sur `--load-extension` : le repli
  unpacked persistant reste valide ; la détection rend la dégradation visible
  au lieu de silencieuse.
- `--disable-extensions-except` désactiverait les extensions personnelles de
  l'utilisateur dans ce profil : ne PAS l'ajouter par défaut (profil Synthesix
  dédié, mais rester conservateur) — flag documenté seulement.

## Résultat 2026-07-07

- `settings.py` expose `extension_dir` (`SYNTHESIX_EXTENSION_DIR`, défaut
  `extension/`) et `extension_mode` (`SYNTHESIX_EXTENSION_MODE=auto|off`,
  défaut `auto`).
- `browser_manager.py` ajoute `--load-extension=<extension/>` quand le build
  est présent et le mode actif, sans `--disable-extensions-except` par défaut.
  Le flag `--disable-features=DisableLoadExtensionCommandLineSwitch` est ajouté
  pour les builds Chrome qui l'honorent encore.
- Détection ajoutée par target CDP `chrome-extension://<id>/...` ; l'ID est
  dérivé du `key` fixé dans `extension/manifest.json`.
- `HeadlessBrowserManager.extension_available` expose l'état détecté ; `main.py`
  affiche un statut home non bloquant si l'extension n'est pas active, l'overlay
  CDP restant le chemin actif jusqu'à T-036.
- `extension/README.md` documente le mode auto/off et le repli d'installation
  unpacked persistante dans `zendriver-profile/`.

Tests :

- `.venv\Scripts\python.exe -m unittest tests.test_browser_manager tests.test_settings`
  — OK, 16 tests.
- `.venv\Scripts\python.exe -m unittest tests.test_main` — OK, 42 tests.
- `.venv\Scripts\python.exe -m py_compile browser_manager.py settings.py main.py tests\manual\spike_ext_transport.py`
  — OK.

Smoke réel :

- `tests/manual/spike_ext_transport.py` confirme que Chrome/Zendriver dans cet
  environnement ignore encore le chargement unpacked automatique : marqueur
  `dataset.synthesixExt` absent et seuls les targets d'extensions internes sont
  visibles. Le repli manuel persistant reste donc requis ici avant de reprendre
  T-031.
