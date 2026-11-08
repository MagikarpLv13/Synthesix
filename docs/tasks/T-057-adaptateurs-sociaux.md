# T-057 — Adaptateurs de métriques pour les réseaux sociaux

- **Statut** : done
- **Priorité** : P2
- **Effort** : élevé
- **Outil recommandé** : Les deux
- **Dépendances** : T-054

## Objectif

Collecter les métriques publiques utiles des profils sociaux en privilégiant
les API officielles disponibles, avec extraction navigateur comme repli
explicite et testable.

## Périmètre initial

- Instagram
- TikTok
- Facebook
- X
- YouTube

## Étapes

1. Définir une interface d'adaptateur par profil.
2. Ajouter un registre domaine/profil vers adaptateur.
3. Implémenter YouTube API et X API lorsque des identifiants sont configurés.
4. Prévoir TikTok Research API uniquement pour les accès approuvés.
5. Ajouter des extracteurs navigateur séparés des API.
6. Versionner les parseurs et enregistrer leur provenance dans l'observation.
7. Tester les fixtures et détecter les ruptures de sélecteurs.

## Critères d'acceptation

- L'origine de chaque métrique est identifiable : API, DOM ou donnée absente.
- Un adaptateur cassé ne fait pas échouer les autres métriques.
- Aucun secret n'est écrit dans la base, les preuves ou les journaux.
- Les compteurs arrondis ou masqués portent un indicateur de précision.
- Le fallback navigateur respecte les limites, challenges et conditions
  d'accès de la plateforme.

## Commandes de test

```powershell
.venv\Scripts\python.exe -m unittest tests.test_monitoring
git diff --check
```

## Risques

- Accès API payant, restreint ou soumis à approbation.
- Changements fréquents du DOM.
- Limites contractuelles propres à chaque plateforme.

## Résultat — 2026-07-16

- Un registre relie les profils Facebook, Instagram, TikTok, X et YouTube à
  des adaptateurs versionnés.
- YouTube Data API, X API v2 et TikTok Research API sont utilisés en priorité
  lorsqu'un secret correspondant est fourni par l'environnement. Facebook et
  Instagram utilisent le repli navigateur dans ce périmètre initial.
- Le repli DOM est séparé des clients API et ne collecte qu'un snapshot borné :
  métadonnées, texte visible, liens, libellés accessibles, JSON-LD et résultats
  des sélecteurs CSS explicitement configurés.
- Chaque métrique conserve statut, type, valeur, précision et provenance
  (`api`, `dom` ou `absent`) avec nom et version du parseur. Les compteurs
  YouTube arrondis et les valeurs masquées restent explicitement marqués.
- Un échec API reste un avertissement isolé ; seules les métriques non résolues
  passent au DOM. Un sélecteur personnalisé garde la priorité sur l'API.
- Les secrets sont exclus des représentations de réglages et ne sont jamais
  recopiés dans les observations, erreurs, preuves ou métadonnées.
- Les fixtures couvrent YouTube, X, TikTok, Instagram, les ruptures de
  sélecteurs, le fallback, les valeurs masquées et la priorité des sélecteurs.
- Smokes réels : extraction DOM Chrome headless sur fixture locale, puis
  historique de provenance en thèmes clair/sombre à 884 px. Aucun appel réel
  aux API ni à une plateforme sociale n'a été exécuté.

## Extension Facebook — 2026-07-21

- Le parseur Facebook v3 collecte une fiche de profil dédiée : nom affiché,
  photo de profil, couverture, nombre d'amis, abonnés, biographie, détails
  visibles, liens externes et dernière publication. Il s'appuie sur les URL du
  profil, les attributs sémantiques et les libellés accessibles, sans dépendre
  des classes générées `x...`.
- Lorsque le bandeau fournit un compteur arrondi mais que la carte d'amis
  affiche un total exact, le total exact est retenu ; la valeur « en commun »
  est explicitement écartée.
- La première publication non épinglée fournit un identifiant stable, sa date
  affichée, son contenu textuel borné et son permalien canonique.
- Les paramètres temporaires de l'URL CDN de la photo et les libellés de date
  relatifs disposent d'une clé de comparaison stable afin d'éviter les faux
  changements.
- Le nombre de cartes virtualisées reste un diagnostic interne : il n'est pas
  exposé comme nombre total de publications, absent du DOM fiable.
- L'interface regroupe séparément l'identité Facebook, les informations
  visibles et la dernière publication. La photo est rendue en miniature avec
  un lien vers l'original ; chaque champ reste désactivable et l'analyste peut
  ajouter une cible CSS nommée pour adapter l'extraction à une évolution du DOM.
- Le smoke Chrome sur la page HTML Facebook complète fournie valide le nom du
  profil ciblé, le total exact d'amis, les photos de profil/couverture, les
  détails visibles et la dernière publication sans duplication de texte.
