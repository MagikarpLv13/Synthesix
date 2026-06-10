# Roadmap moteur d'investigation

Etat initial : 2026-06-09.

## Etat d'implementation

Phases 0 et 1 livrees :

- stockage SQLite local et migrations versionnees ;
- modele de dossiers, recherches, resultats et observations ;
- import unique de l'historique JSON existant ;
- creation, modification, archivage et suppression protegee des dossiers ;
- selection facultative d'un dossier depuis la page d'accueil ;
- rattachement des nouvelles recherches et de leurs resultats au dossier actif ;
- deduplication globale des resultats par URL canonique ;
- conservation du mode de recherche sans dossier ;
- effacement de l'historique sans suppression des dossiers ;
- page detaillee et locale pour chaque dossier ;
- notes, tags, favoris et statut analyste persistants ;
- filtres par texte, statut, tag, moteur, date et favori ;
- rattachement manuel d'une recherche sans dossier ;
- separation entre observations de recherche et pages retenues ;
- sauvegarde explicite d'une page depuis un bouton injecte par CDP ;
- provenance automatique vers la requete et les moteurs lorsque l'URL est connue ;
- referent et contexte de navigation conserves pour les sauvegardes manuelles ;
- dossiers archives consultables en lecture seule ;
- provenance des resultats jusqu'aux executions et rapports d'origine.

Prochaine phase P0 :

- capture PNG de la zone visible ou d'une zone rectangulaire : realisee ;
- manifeste de provenance PNG : realise ;
- calcul SHA-256 du PNG : realise ;
- capture HTML et MHTML : a faire ;
- verification interactive SHA-256 : realisee ;
- nettoyage des donnees sensibles avant ecriture.

## 1. Objectif

Faire evoluer Synthesix d'un agregateur multi-moteur vers un moteur
d'investigation local capable de :

- organiser les recherches dans des dossiers ;
- conserver la provenance des informations ;
- capturer des preuves reproductibles ;
- retrouver et comparer les observations dans le temps ;
- extraire des entites sans les presenter comme des identites confirmees ;
- exporter les elements et relations vers ZeroNeurone pour l'analyse visuelle.

Cette roadmap complete `OSINT_ROADMAP.md` sans reprendre son contenu.

## 2. Hors perimetre

Les sujets suivants restent exclusivement dans `OSINT_ROADMAP.md` :

- ajout de nouveaux moteurs de recherche ;
- connecteurs Instagram, TikTok, LinkedIn, GitHub, Reddit ou autres sites ;
- profils navigateur preconfigures et comptes connectes ;
- modes de recherche par nom, pseudo, entreprise, domaine, email ou telephone ;
- architecture generique des connecteurs de sites ;
- rapport OSINT groupe par type de source ;
- creation d'un graphe relationnel directement dans Synthesix.

Synthesix ne doit pas reimplementer les fonctions de graphe, carte, timeline,
centralite, clusters ou collaboration deja fournies par ZeroNeurone.

## 3. Principes

- L'enqueteur garde le controle des validations et des relations.
- Une observation n'est pas une preuve d'identite.
- Une relation deduite n'est jamais exportee comme un fait confirme.
- Chaque information conserve sa source, sa requete et sa date d'observation.
- Les captures et exports restent locaux par defaut.
- Les formats ouverts sont preferes aux formats internes opaques.
- Les fonctionnalites doivent rester utilisables sans service IA distant.
- Les ajouts doivent etre progressifs et ne pas casser la recherche actuelle.

## 4. Modele fonctionnel cible

### Dossier d'investigation

Un dossier contient :

- un identifiant stable ;
- un titre ;
- une reference libre ;
- une description ;
- des tags ;
- une date de creation et de derniere modification ;
- les recherches executees ;
- les resultats retenus ;
- les notes et statuts de l'enqueteur ;
- les preuves capturees ;
- les entites extraites ;
- les exports produits.

### Recherche

Une recherche conserve :

- la requete saisie ;
- la requete exacte envoyee a chaque moteur ;
- les filtres ;
- les moteurs selectionnes ;
- les variantes eventuelles ;
- les dates de debut et de fin ;
- les erreurs, captchas et timeouts ;
- le nombre de resultats brut, deduplique et retenu.

### Resultat

Un resultat conserve :

- une URL canonique ;
- l'URL initiale et l'URL finale ;
- le titre et la description ;
- les moteurs qui l'ont retourne ;
- la date de premiere et de derniere observation ;
- les scores detailles ;
- un statut analyste ;
- des tags, notes et favoris ;
- les preuves et fichiers associes.

### Preuve

Une preuve conserve :

- la source exacte ;
- la date UTC de capture ;
- le type d'artefact ;
- le hash SHA-256 ;
- les informations techniques disponibles ;
- l'outil et la version ayant produit la capture ;
- le lien avec la recherche et le resultat d'origine.

### Entite extraite

Une entite conserve :

- une valeur normalisee ;
- un type propose ;
- le texte ou document source ;
- la date d'observation ;
- une confiance technique ;
- un statut `proposee`, `validee` ou `rejetee`.

## 5. Fonctionnalites prioritaires

### P0 - Dossiers d'investigation

Objectif : remplacer l'historique global par une organisation exploitable.

Fonctionnalites :

- creer, renommer, archiver et supprimer un dossier ;
- choisir un dossier actif avant une recherche ;
- rattacher une recherche existante a un dossier ;
- ne jamais ajouter automatiquement tous les resultats au dossier ;
- retenir explicitement une page consultee depuis le navigateur ;
- ajouter des notes et tags ;
- marquer un resultat :
  - `a_verifier`
  - `pertinent`
  - `ecarte`
  - `confirme`
- ajouter ou retirer un favori ;
- filtrer les resultats par statut, tag, moteur et date ;
- conserver un mode sans dossier pour ne pas casser l'usage actuel.

Architecture suggeree :

- stockage SQLite local ;
- migrations versionnees ;
- repository dedie aux dossiers, recherches et resultats ;
- import initial de l'historique JSON existant ;
- aucun ORM lourd necessaire pour la premiere version.

Criteres de validation :

- une recherche peut etre lancee sans dossier comme aujourd'hui ;
- une recherche peut etre rattachee a un dossier ;
- une recherche rattachee ne cree aucun element retenu sans action analyste ;
- une page consultee peut etre sauvegardee explicitement avec sa provenance ;
- les notes, tags et statuts persistent apres redemarrage ;
- la suppression d'un dossier demande une confirmation ;
- les artefacts ne sont pas supprimes silencieusement.

### P0 - Capture de preuves et provenance

Objectif : permettre de justifier ce qui a ete observe, quand et comment.

Artefacts proposes :

- capture d'ecran PNG ;
- HTML brut ;
- snapshot MHTML via CDP quand disponible ;
- URL initiale et finale ;
- chaine de redirections ;
- en-tetes de reponse utiles ;
- statut HTTP ;
- date UTC ;
- hash SHA-256 de chaque artefact ;
- manifeste JSON.

Actions UI :

- `Capture evidence` depuis un resultat ;
- `Open evidence` ;
- `Verify hash` ;
- commentaire analyste optionnel.

Regles :

- aucune capture automatique massive par defaut ;
- l'utilisateur choisit les resultats a capturer ;
- les donnees de session sensibles ne doivent pas etre ecrites dans le manifeste ;
- les en-tetes `Cookie`, `Authorization` et equivalents sont exclus ;
- le manifeste indique clairement les echecs partiels.

Criteres de validation :

- le hash d'une capture peut etre recalcule et verifie ;
- une preuve reste lisible hors ligne quand le format le permet ;
- le manifeste permet de retrouver le dossier, la recherche et l'URL source ;
- une capture en echec ne fait pas passer le resultat en preuve valide.

### P1 - Scoring explicable et consensus multi-moteur

Objectif : rendre le classement comprehensible et plus robuste.

Remplacer le score unique opaque par des composantes :

- correspondance exacte dans le titre ;
- correspondance exacte dans la description ;
- correspondance des termes requis ;
- presence sur plusieurs moteurs ;
- conformite aux filtres ;
- recence lorsque la date est connue ;
- statut ou validation manuelle ;
- penalites explicites.

Affichage propose :

```text
Score 8.5
+4.0 expression exacte dans le titre
+2.0 retourne par 3 moteurs
+1.5 termes presents dans la description
+1.0 filtre de domaine respecte
```

Consensus :

- afficher les moteurs ayant retourne le resultat ;
- distinguer une URL retournee par un moteur d'une URL confirmee par plusieurs ;
- ne pas confondre popularite et veracite ;
- ne pas attribuer automatiquement un score de confiance factuelle.

Criteres de validation :

- chaque score peut etre explique ;
- les poids sont centralises et testes ;
- le comportement actuel des expressions exactes reste protege ;
- le consensus ne remplace jamais la verification humaine.

### P1 - Index local et recherche transversale

Objectif : transformer l'historique en base documentaire locale.

Fonctionnalites :

- index SQLite FTS5 ;
- recherche dans les titres, descriptions, URLs, notes et tags ;
- filtres par dossier, moteur, date, statut et domaine ;
- resultat `deja observe` ;
- date de premiere et derniere observation ;
- acces aux anciennes preuves et captures ;
- recherche hors ligne dans les donnees deja collectees.

Criteres de validation :

- une recherche locale ne lance aucun moteur externe ;
- les nouveaux resultats sont indexes automatiquement ;
- la reconstruction complete de l'index est possible ;
- la suppression d'un dossier retire proprement ses donnees indexees.

### P1 - Comparaison temporelle et surveillance

Objectif : identifier les changements sans relire manuellement tous les rapports.

Premiere version :

- enregistrer une recherche comme surveillance ;
- relance uniquement manuelle ;
- comparer avec l'execution precedente ;
- afficher :
  - nouveaux resultats
  - resultats disparus
  - URL deja connues
  - titres ou descriptions modifies
- produire un rapport de difference.

Version ulterieure :

- planification locale optionnelle ;
- frequence minimale configurable ;
- limite globale de concurrence ;
- notification locale ;
- suspension automatique apres echecs repetes ou captcha.

Regles :

- aucune surveillance agressive ;
- pas de boucle infinie en cas de panne ;
- captchas et actions manuelles restent visibles ;
- la planification doit pouvoir etre totalement desactivee.

### P2 - Variantes de requete assistees

Objectif : reduire les angles morts sans cacher les requetes executees.

Variantes possibles :

- avec et sans accents ;
- ordre inverse ;
- initiales ;
- tirets, espaces et underscores ;
- variantes de casse ;
- translitteration ;
- fautes probables ;
- variantes linguistiques configurees ;
- variantes ajoutees manuellement.

UX :

- Synthesix propose les variantes ;
- l'utilisateur les valide avant execution ;
- chaque variante peut etre activee ou desactivee ;
- le rapport affiche la variante ayant trouve chaque resultat ;
- une limite empeche l'explosion combinatoire.

Criteres de validation :

- aucune variante n'est lancee silencieusement ;
- la requete exacte reste consultable ;
- les doublons entre variantes sont fusionnes ;
- la limite de variantes est configurable.

### P2 - Resume de couverture

Cette fonctionnalite remplace l'idee de "matrice de requete".

Elle devient utile uniquement lorsqu'une recherche contient plusieurs variantes et
plusieurs moteurs. Son objectif n'est pas d'analyser les resultats, mais de verifier
que toutes les combinaisons prevues ont bien ete executees.

Exemple :

| Variante | Google | Bing | Brave | DuckDuckGo |
| --- | --- | --- | --- | --- |
| `"anna lindberg"` | 12 | 8 | 6 | 9 |
| `"lindberg anna"` | 3 | timeout | 1 | 2 |
| `"a lindberg"` | captcha | 4 | 2 | 5 |

Utilite :

- voir qu'un moteur n'a pas repondu ;
- distinguer `0 resultat` d'un timeout ou captcha ;
- identifier les variantes utiles ;
- eviter de croire qu'une recherche a ete complete alors qu'une partie a echoue ;
- relancer seulement les cellules en erreur.

Decision produit :

- ne pas en faire un ecran principal ;
- afficher un resume compact en fin de recherche ;
- n'implementer cette vue qu'apres les variantes de requete ;
- conserver le rapport actuel pour consulter les resultats eux-memes.

### P2 - Extraction d'entites

Objectif : transformer les pages et documents retenus en observations structurees.

Types initiaux :

- email ;
- telephone ;
- URL ;
- domaine ;
- adresse IPv4/IPv6 ;
- pseudo probable ;
- identifiant technique ;
- coordonnees geographiques explicites.

Types plus ambigus, a ajouter ensuite :

- personne ;
- organisation ;
- lieu ;
- date ou evenement ;
- nom de produit ou service.

Pipeline :

1. extraire le texte visible ;
2. detecter les candidats ;
3. normaliser sans perdre la valeur originale ;
4. conserver le passage source ;
5. proposer les entites a l'utilisateur ;
6. enregistrer seulement les validations ou rejets explicites.

Regles :

- utiliser d'abord des extracteurs deterministes ;
- ne pas imposer de dependance IA ;
- ne pas fusionner deux personnes sur la seule similarite de nom ;
- conserver les faux positifs rejetes pour eviter de les reproposer.

### P2 - Export ZeroNeurone

Objectif : transferer les observations retenues vers ZeroNeurone sans construire un
graphe concurrent dans Synthesix.

ZeroNeurone prend en charge l'import/export ZIP, CSV, JSON, GraphML et GeoJSON.
La premiere cible recommandee est GraphML, car ce format represente naturellement
des noeuds, des liens et leurs proprietes.

#### Export GraphML initial

Noeuds exportables :

- dossier ;
- recherche ;
- resultat web ;
- preuve ;
- entite validee ;
- document ou fichier analyse.

Relations exportables :

- `CONTAINS`
- `FOUND_BY`
- `OBSERVED_IN`
- `MENTIONS`
- `LINKS_TO`
- `CAPTURED_AS`
- `SAME_CONTENT_AS`
- `VALIDATED_BY`

Proprietes minimales :

- identifiant Synthesix stable ;
- label ;
- type ;
- URL source ;
- moteur ;
- requete ;
- date UTC d'observation ;
- statut analyste ;
- confiance ;
- hash SHA-256 ;
- notes ;
- chemin local vers l'artefact, si disponible.

Regles d'export :

- exporter par defaut uniquement les resultats retenus et entites validees ;
- permettre un export complet sur action explicite ;
- marquer les relations comme `observee`, `deduite` ou `confirmee` ;
- ne jamais exporter une relation deduite comme confirmee ;
- utiliser des identifiants stables pour permettre les reexports ;
- echapper et valider toutes les valeurs GraphML ;
- inclure un manifeste JSON avec la version du schema d'export ;
- ne pas dependre d'une ontologie ZeroNeurone imposee.

Formats complementaires :

- CSV `nodes.csv` et `edges.csv` pour inspection manuelle ;
- JSON Synthesix complet pour archivage et reimport ;
- GeoJSON uniquement lorsque des coordonnees validees existent.

Compatibilite :

- tester l'import contre une version ZeroNeurone explicitement documentee ;
- conserver des fixtures minimales d'import ;
- versionner le schema `synthesix-zeroneurone` ;
- isoler l'adaptateur dans un module dedie ;
- ne pas coder directement contre un format interne non documente de ZeroNeurone.

Criteres de validation :

- ZeroNeurone importe le fichier sans erreur ;
- les labels, URLs, dates et relations restent lisibles ;
- un reexport du meme dossier conserve les identifiants ;
- les entites rejetees ne sont pas exportees par defaut ;
- aucune preuve locale n'est transmise sans action explicite.

### P3 - Analyse technique des URLs

Objectif : enrichir les resultats avec des informations reproductibles.

Informations proposees :

- URL initiale ;
- URL finale ;
- chaine de redirections ;
- statut HTTP ;
- domaine en Unicode et punycode ;
- domaine enregistrable ;
- parametres de tracking identifies ;
- type de contenu ;
- taille ;
- temps de reponse ;
- en-tetes de securite utiles ;
- hash du contenu lorsque la capture est autorisee.

Regles :

- ne pas retirer automatiquement des parametres pouvant modifier le contenu ;
- afficher la version nettoyee comme suggestion ;
- limiter les requetes supplementaires ;
- reutiliser les donnees CDP deja disponibles avant de refaire un appel reseau.

### P3 - Analyse de documents

Objectif : exploiter les fichiers explicitement selectionnes par l'enqueteur.

Fonctionnalites :

- calcul de hashes ;
- detection du type reel ;
- extraction de texte ;
- metadata EXIF, IPTC, XMP et C2PA lorsque disponibles ;
- auteur, logiciel, dates et chemins exposes ;
- extraction d'emails, URLs et domaines ;
- OCR optionnel ;
- detection de doublons par hash ;
- lien entre le document, son URL et ses entites validees.

Regles :

- pas de telechargement massif automatique ;
- taille maximale configurable ;
- analyse dans un repertoire local dedie ;
- ne jamais executer le document ;
- signaler les formats non pris en charge ;
- OCR et ExifTool restent des integrations optionnelles.

### P3 - Exports interoperables

Formats proposes :

- JSON structure Synthesix ;
- CSV resultats ;
- CSV entites ;
- manifeste SHA-256 ;
- GraphML ZeroNeurone ;
- GeoJSON pour les observations geolocalisees ;
- STIX 2.1 pour les observables cyber compatibles ;
- WACZ pour les archives web lorsque la chaine de capture le permet.

Priorite :

1. JSON Synthesix versionne ;
2. CSV ;
3. GraphML ZeroNeurone ;
4. manifeste de preuve ;
5. GeoJSON ;
6. STIX 2.1 ;
7. WACZ.

## 6. Architecture proposee

Modules possibles :

```text
investigations/
    models.py
    repository.py
    service.py
    migrations/

evidence/
    capture.py
    manifest.py
    hashing.py

analysis/
    entities.py
    urls.py
    documents.py
    changes.py

exports/
    json_export.py
    csv_export.py
    zeroneurone.py
    geojson.py
    stix.py
    wacz.py
```

Regles d'architecture :

- les moteurs restent responsables de la collecte ;
- l'orchestrateur reste responsable de l'execution multi-moteur ;
- le stockage ne depend pas de Zendriver ;
- la capture navigateur reste async ;
- les analyseurs de fichiers lourds passent par `asyncio.to_thread()` ou un worker ;
- les exports consomment des modeles structures, jamais le HTML du rapport ;
- les schemas SQLite et JSON sont versionnes.

## 7. Ordre d'implementation recommande

### Phase 0 - Modele et stockage

- definir les identifiants stables ;
- definir les modeles dossier, recherche, resultat et preuve ;
- ajouter SQLite et les migrations ;
- importer l'historique JSON existant ;
- conserver une compatibilite sans dossier.

Livrable : dossiers persistants sans changement du moteur de recherche.

### Phase 1 - Workflow analyste

- selection du dossier actif ;
- notes, tags, favoris et statuts ;
- filtres dans les resultats ;
- page de dossier ;
- tests de persistence et migration.

Livrable : Synthesix devient utilisable pour suivre une enquete.

### Phase 2 - Provenance et preuves

- manifeste de provenance ;
- SHA-256 ;
- capture PNG, HTML et MHTML ;
- verification des hashes ;
- ouverture hors ligne ;
- nettoyage des en-tetes sensibles.

Livrable : un resultat peut etre transforme en preuve tracable.

### Phase 3 - Scoring et index local

- decomposition du score ;
- consensus multi-moteur ;
- SQLite FTS5 ;
- recherche locale ;
- premiere et derniere observation.

Livrable : classement explicable et recherche transversale locale.

### Phase 4 - Comparaison temporelle

- surveillance manuelle ;
- comparaison entre executions ;
- rapport nouveaux/disparus/modifies ;
- gestion des echecs partiels.

Livrable : detection de changements sans planificateur automatique.

### Phase 5 - Variantes et couverture

- generation assistee de variantes ;
- validation utilisateur ;
- limite de combinaisons ;
- resume de couverture compact ;
- relance ciblee des erreurs.

Livrable : recherche plus complete sans execution opaque.

### Phase 6 - Entites et export ZeroNeurone

- extraction deterministe initiale ;
- validation/rejet des entites ;
- relations observees ;
- export GraphML ;
- CSV noeuds/liens ;
- manifeste d'export ;
- test d'import ZeroNeurone.

Livrable : transfert fiable vers ZeroNeurone pour l'analyse visuelle.

### Phase 7 - Analyse URL et documents

- redirections et en-tetes ;
- hashes de contenu ;
- metadata fichiers ;
- extraction de texte ;
- OCR optionnel ;
- detection de doublons.

Livrable : enrichissement technique des resultats selectionnes.

### Phase 8 - Formats avances

- GeoJSON ;
- STIX 2.1 ;
- WACZ ;
- signature ou scellement optionnel des manifestes ;
- documentation d'interoperabilite.

Livrable : dossiers partageables avec des outils externes.

## 8. Dependances et strategie

Dependances standard ou legeres :

- `sqlite3` standard library ;
- `hashlib` standard library ;
- `zipfile` standard library ;
- `xml.etree.ElementTree` ou `lxml` deja present pour GraphML ;
- `urllib.parse` pour les URLs.

Dependances optionnelles :

- ExifTool installe sur la machine ;
- moteur OCR local ;
- bibliotheque STIX uniquement quand l'export STIX est implemente ;
- outil WARC/WACZ uniquement quand le format est prioritaire.

Ne pas ajouter toutes les dependances avancees au socle initial.

## 9. Risques

### Integrite des preuves

Risque : presenter une capture incomplete comme une preuve complete.

Reduction :

- manifeste ;
- hash ;
- type de capture explicite ;
- erreurs partielles visibles ;
- date UTC ;
- version de Synthesix.

### Faux positifs d'entites

Risque : fusionner des personnes, pseudos ou organisations differents.

Reduction :

- statut `proposee` par defaut ;
- validation humaine ;
- passage source ;
- confiance separee de la veracite.

### Explosion du volume

Risque : variantes, preuves et surveillances generent trop de donnees.

Reduction :

- limites ;
- quotas par dossier ;
- captures manuelles ;
- politique de retention ;
- deduplication par hash.

### Compatibilite ZeroNeurone

Risque : evolution des formats d'import.

Reduction :

- GraphML standard en premiere cible ;
- schema d'export versionne ;
- fixture d'import ;
- adaptateur isole ;
- validation contre une version ZeroNeurone identifiee.

### Donnees sensibles

Risque : exporter des cookies, tokens, chemins ou informations personnelles.

Reduction :

- liste d'en-tetes interdits ;
- apercu avant export ;
- export explicite ;
- stockage local ;
- documentation de retention et suppression.

## 10. Definition de termine

Une phase est terminee uniquement si :

- les migrations et formats sont versionnes ;
- les tests unitaires couvrent le comportement principal ;
- les erreurs n'endommagent pas le dossier ;
- les actions sensibles demandent confirmation ;
- les rapports indiquent les echecs partiels ;
- la documentation utilisateur est mise a jour ;
- un test manuel multi-OS est documente si CDP ou fichiers sont impliques.

## 11. Sources techniques

- ZeroNeurone : https://zeroneurone.com/
- Documentation ZeroNeurone : https://doc.zeroneurone.com/fr/
- Chrome DevTools Protocol Page :
  https://chromedevtools.github.io/devtools-protocol/tot/Page/
- Chrome DevTools Protocol Network :
  https://chromedevtools.github.io/devtools-protocol/tot/Network/
- WACZ : https://specs.webrecorder.net/wacz/
- STIX 2.1 : https://oasis-open.github.io/cti-documentation/stix/intro.html
- ExifTool : https://exiftool.org/
