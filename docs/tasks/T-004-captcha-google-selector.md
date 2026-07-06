# T-004 — Détection captcha Google fiable

- **Statut** : todo
- **Priorité** : P1 · **Effort** : faible
- **Outil recommandé** : Claude (smoke CDP réel nécessaire)
- **Dépendances** : aucune

## Objectif

Garantir que le captcha Google est effectivement détecté et que l'utilisateur
a le temps de le résoudre, au lieu d'un échec silencieux.

## Contexte

`google.py:49` : `await self.tab.find("#captcha-form", timeout=0.1)`.
`Tab.find()` de zendriver cherche par **texte** (DOM.performSearch), pas par
sélecteur CSS garanti ; le comportement avec `#captcha-form` n'est pas prouvé,
et le timeout de 0,1 s est trop court juste après un timeout de chargement.
Si la détection échoue, `robot_check` retourne False et la recherche Google
est déclarée « timeout » au lieu de « challenge », ce qui fausse la couverture
et empêche la résolution manuelle.

## Fichiers concernés

- `google.py` : `robot_check`.
- `tests/test_engines.py` (ou nouveau test dédié).

## Étapes

1. Remplacer par `await self.tab.query_selector("#captcha-form")` (+ contrôle
   de l'URL `google.com/sorry/` en second indice, comme le font Brave/DDG avec
   leurs marqueurs).
2. Conserver `tab.activate()` puis attente longue existante
   (`wait_for_page_load(timeout=100)`) après détection.
3. Ajouter un test unitaire avec FakeTab : `query_selector` renvoie un nœud ⇒
   `robot_check` vrai ; renvoie None et URL normale ⇒ faux.
4. Smoke test réel : forcer un captcha Google (répéter des requêtes) ou au
   minimum vérifier sur une page `google.com/sorry/` archivée que le sélecteur
   correspond ; consigner le résultat dans la note de clôture.

## Critères d'acceptation

- `robot_check` détecte une page captcha Google réelle ou archivée.
- Statut de couverture `challenge` (et non `timeout`) remonté dans ce cas.
- Aucun changement de comportement quand il n'y a pas de captcha.

## Commandes de test

```powershell
.venv\Scripts\python.exe -m unittest tests.test_engines
```

Smoke CDP réel : lancer `python main.py`, recherche Google, observer les logs
(`Robot detected by Google` attendu en cas de challenge). Si le smoke n'est
pas réalisable pendant la tâche, l'indiquer explicitement à la clôture.

## Risques

- Google peut servir des variantes de page captcha sans `#captcha-form` :
  ajouter le repli URL `/sorry/` couvre le cas principal connu.
