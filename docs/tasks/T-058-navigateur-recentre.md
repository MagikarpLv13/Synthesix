# T-058 — Navigateur recentré sur les dorks et les profils

**Statut :** done — vérifié le 2026-10-30.
**Branche :** `codex/browser-refocus`.
**Origine :** recentrage demandé et autorisé par l'utilisateur le 2026-10-30.

## Objectif

Livrer le lancement recherche → résultats → profil sans le produit d'enquête,
avec conservation des données existantes et un paquet Windows prêt à ouvrir.

## Périmètre réalisé

- Sauvegarde des sources initiales dans `0e58af1`.
- `app/` sépare stockage SQLite, profils natifs, requêtes et cycle de vie.
- Collecte progressive et annulation propre dans l'orchestrateur existant.
- Page locale et composant Lit : plusieurs dorks, filtres, résultats dédupliqués,
  sélection du profil d'ouverture, création/renommage et historique.
- Retrait versionné des fonctions d'enquête, de monitoring et de l'overlay.
- Bundle unique et construction Windows, sans dépendance Node/Python à l'usage.
- Documentation et règles de conservation des données.

## Acceptation et preuves

- L'import du nouveau lancement n'importe aucun module d'enquête.
- La collecte n'importe aucun renderer de rapport.
- Les tests conservent les cas moteur/scoring/parsing, les entrées hostiles,
  l'isolation des chemins, les résultats progressifs et l'arrêt des tâches.
- Un test rejette les commandes depuis un onglet externe ou un accueil ayant
  navigué ; une inversion de ce garde a été détectée par le test.
- Le smoke Chrome exerce les clics et saisies réels, le transport CDP, la
  recherche avec moteurs simulés, l'historique, le rechargement, les thèmes,
  l'état vide, le texte long et les largeurs 1440/768/390.
- Deux vrais profils temporaires vérifient la persistance du stockage local
  synthétique et son absence dans l'autre persona.
- Le smoke de l'exécutable contrôle les ressources embarquées, la connexion de
  l'interface, le répertoire de données indépendant et la fermeture propre.

## Vérifications

```powershell
.venv\Scripts\python.exe -m unittest discover
cd frontend
npm run typecheck
npm run build
cd ..
.venv\Scripts\python.exe tests/manual/smoke_browser_app.py
.venv\Scripts\python.exe scripts/build_windows.py
.venv\Scripts\python.exe tests/manual/smoke_frozen_browser.py
```

Résultats exacts consignés à la clôture dans `AI_WORKLOG.md`.

## Limites

Aucun accès aux comptes réels ou aux données d'enquête. Pas de migration des
anciennes enquêtes, pas de liaison ZNELFP, pas de benchmark réseau. Chrome ou
Brave doit être installé ; le paquet local est non signé. Les anciennes tâches
liées au produit d'enquête restent historiques et ne doivent pas être relancées.

## Résultat final

222 tests unitaires réussis, typecheck et build réussis. Smoke Chrome réel de
l'interface avec moteurs simulés, persistance sur trois réouvertures de profil,
Bing réel et dernier exécutable Windows validés. Les données historiques restent
intactes ; le paquet est disponible dans `dist/Synthesix-Windows.zip`.
