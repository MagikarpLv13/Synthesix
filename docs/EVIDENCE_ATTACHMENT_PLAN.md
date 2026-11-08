# Rattachement des preuves et images aux entités

## Objectif

Permettre à l'analyste de dire immédiatement à quoi correspond une preuve
capturée depuis le navigateur Synthesix :

- capture localisée ;
- capture entière ;
- archive HTML/MHTML ;
- image visible sur une page, par exemple une photo de profil.

Le rattachement doit alimenter l'espace enquête sans dupliquer le modèle :
une preuve reste un `EvidenceCapture`, et son sens analyste est représenté par
une propriété sourcée attachée à une entité.

## Décision de stockage

Ne pas créer de nouvelle table dans un premier temps.

Créer une propriété sourcée via le flux existant des entités extraites :

- `record_evidence_capture(...)` continue de stocker les fichiers et le
  manifeste local ;
- un helper service dédié crée une entité extraite validée avec :
  - `investigation_entity_id` cible ;
  - `property_key`, par exemple `Photo de profil`, `Capture`, `Archive HTML` ;
  - `value_original`, par exemple le nom de la preuve ou l'URL source ;
  - `attributes.property_type`, le type choisi ou auto ;
  - `attributes.evidence_capture_id` ;
  - `attributes.evidence_kind` (`screenshot`, `page_archive`, `image_capture`) ;
  - `attributes.artifact_type` (`png`, `html`, `mhtml`, `text`) si pertinent.
- `attach_extracted_property(...)` reste le point d'attache vers l'entité graphe.

Avantage : zéro migration DB, provenance cohérente, export ZeroNeurone déjà
branché sur les propriétés sourcées.

## Lot 1 — Rattacher capture et archive existantes

### UX

Ajouter un panneau commun après ou avant l'action :

- entité cible ;
- nom de propriété ;
- type (`Auto`, `Texte`, `Nombre`, `Date`, `Date/heure`, `Géo`, `Pays`, `Lien`) ;
- libellé/nom de la preuve.

Pour une capture localisée ou entière, valeurs par défaut :

- propriété : `Capture écran` ;
- type : `Lien` ou `Texte` en auto selon export ;
- valeur : nom de capture.

Pour une archive HTML :

- propriété : `Archive HTML` ;
- type : `Lien` ;
- valeur : URL de la page ou nom d'archive.

### Technique

- Étendre le payload `capture_evidence_to_investigation` avec un bloc optionnel
  `attach`.
- Étendre le payload `archive_page_to_investigation` avec le même bloc.
- Après création de `EvidenceCapture`, appeler le helper service si `attach`
  est renseigné.
- Afficher le lien de source numéroté sur la propriété, comme pour les propriétés
  issues de texte sélectionné.

### Tests

- `tests.test_main` : le payload capture/archive transmet bien `attach`.
- `tests.test_investigations` : le helper crée une propriété sourcée avec
  `evidence_capture_id`.
- `tests.test_investigation_view` : la propriété attachée affiche son type et sa
  source.
- Smoke CDP live : capture région, capture page entière, archive HTML.

## Lot 2 — Capturer une image visible

### UX recommandée

Ajouter une action "image" dans l'overlay :

1. l'analyste clique sur l'action image ;
2. Synthesix passe en mode sélection d'image ;
3. les images sous le curseur sont surlignées ;
4. clic sur une image ;
5. le panneau de rattachement s'ouvre avec :
   - propriété par défaut `Photo de profil` ;
   - type `Lien` en auto ;
   - valeur par défaut `alt`, `src` ou titre de page.

### Technique v1

Capturer l'image telle qu'affichée, par coordonnées d'élément, plutôt que
tenter de télécharger le fichier source.

Raison : les images distantes peuvent être protégées par CORS, cookies, CDN ou
URLs temporaires. Une capture élément via le navigateur reste fidèle à ce que
l'analyste voit et s'intègre déjà au pipeline PNG.

Payload image :

- `src` / `currentSrc` ;
- `alt` ;
- rectangle CSS ;
- URL et titre de page ;
- nom de preuve ;
- bloc `attach`.

Le backend réutilise le pipeline `capture_png(...)` avec une sélection dérivée
du rectangle de l'image, puis attache la preuve via le helper du lot 1.

### Technique v2

Ajouter ensuite une tentative de téléchargement du fichier original quand c'est
fiable :

- même origine ou CORS compatible ;
- taille raisonnable ;
- hash SHA-256 et MIME validé ;
- fallback automatique vers capture élément si téléchargement impossible.

## Points de vigilance

- Ne pas stocker de données runtime dans Git.
- Ne pas ajouter de type métier `Photo de profil` dans la liste ZeroNeurone :
  c'est un nom de propriété, pas un `PropertyType`.
- Garder `Booléen` et `Choix` hors UI Synthesix.
- Toute évolution du JS injecté exige un test ciblé et un smoke CDP live.
- L'overlay injecté ne doit pas dépendre des fonts ou du CSS des pages locales.
