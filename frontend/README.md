# Interface Synthesix

TypeScript strict, Lit et esbuild. Le composant `sx-browser-app` présente les
requêtes, les résultats, les profils et l'historique. `browser-home.ts` porte le
pont de commandes de l'accueil local ; les pages tierces ne reçoivent pas ce pont.

```powershell
npm install
npm run typecheck
npm run build
```

Le build produit uniquement `../assets/synthesix-ui.js`, un bundle IIFE chargé
par script classique depuis `file://`. Le committer avec les sources. Node
n'est pas nécessaire à l'utilisation de Synthesix. `npm run watch` est disponible.

Les autres composants enregistrés dans `src/index.ts` servent aux rapports HTML
indépendants. L'overlay et son extension ont été retirés du produit.

Conserver les tokens de `theme.css`, les chaînes traduisibles de `i18n.js`, le
focus visible et les libellés accessibles. Le composant principal traduit ses
chaînes dans son Shadow DOM et réagit aux changements de langue et de thème.

Le smoke réel se lance depuis la racine :

```powershell
.venv\Scripts\python.exe tests/manual/smoke_browser_app.py
```

Il vérifie les formulaires, le transport CDP, les résultats et l'historique avec
moteurs simulés, le rechargement, les thèmes clair/sombre, les largeurs
1440/768/390, le texte long et la persistance de profils temporaires.
