# Roadmap OSINT

Objectif : faire evoluer Synthesix vers un outil OSINT assiste par navigateur, utile a un enqueteur, sans transformer le projet en scraper fragile ou en systeme opaque.

## 1. Positionnement

Synthesix doit rester un outil d'aide a l'enquete :

- l'utilisateur garde le controle ;
- les recherches sont explicites et journalisees ;
- les comptes preconfigures restent locaux au profil navigateur ;
- aucun secret n'est hardcode ;
- les actions sensibles restent manuelles ou confirmees ;
- les donnees collectees doivent etre tracables avec leur source et leur date.

L'idee principale est bonne : reutiliser Zendriver/CDP pour automatiser des recherches repetitives sur plusieurs sources, tout en laissant l'enqueteur verifier les resultats dans le navigateur.

## 2. Moteurs de recherche candidats

### Priorite haute

- Google : deja implemente.
- Bing : deja implemente.
- Brave Search : deja implemente.
- DuckDuckGo : deja implemente.
- Startpage : interessant pour resultats Google-like, mais a verifier cote anti-bot et parsing.
- Qwant : interessant pour couverture Europe/France.
- SearXNG : tres interessant si l'utilisateur configure une instance fiable ; peut aussi agreger plusieurs moteurs.

### Priorite moyenne

- Mojeek : moteur independant, utile pour diversifier.
- Ecosia : souvent proche de Bing, utile mais probablement redondant.
- Yahoo Search : peut completer Bing, mais souvent redondant.
- Swisscows : utile selon le contexte, parsing a evaluer.
- Yep : moteur independant a surveiller.

### Priorite basse ou contexte specifique

- Yandex : utile selon zone geographique, mais a traiter comme option explicite.
- Baidu : utile seulement pour contexte Chine, avec contraintes de langue et anti-bot.
- Naver : utile pour contexte Coree.
- Seznam : utile pour contexte Tchequie.

## 3. Connecteurs OSINT par site

Ces connecteurs ne sont pas des moteurs de recherche generaux. Ce seraient des modules specialises qui ouvrent un site et pre-remplissent ou lancent une recherche dans son interface.

### Identite / pseudo

- Instagram : recherche de nom, pseudo, variations.
- TikTok : recherche de pseudo, nom affiche, bio.
- X / Twitter : recherche de pseudo, nom, mentions.
- Facebook : recherche de nom, pages, groupes publics.
- LinkedIn : recherche professionnelle, entreprise, nom.
- Reddit : pseudo, posts, commentaires.
- YouTube : chaines, videos, commentaires selon disponibilite.
- GitHub : pseudo, nom, emails exposes dans profils/repos.
- GitLab : pseudo et projets publics.
- Stack Overflow / Stack Exchange : profils et activite publique.

### Web ouvert et traces techniques

- GitHub code search.
- GitLab public search.
- npm.
- PyPI.
- Docker Hub.
- Pastebin-like sites si legalement et techniquement acceptable.
- Have I Been Pwned : uniquement via API officielle et avec cadre legal clair.
- crt.sh : certificats TLS par domaine.
- Shodan / Censys / ZoomEye : uniquement via API ou compte autorise.
- Wayback Machine.
- Common Crawl index, si besoin avance.

### Entreprises / domaines

- Whois/RDAP.
- DNS brut via resolvers publics.
- crt.sh.
- BuiltWith/Wappalyzer-like, si API ou usage autorise.
- OpenCorporates.
- Societe.com / Pappers pour contexte France, si compatible avec conditions d'utilisation.

## 4. Idee des comptes preconfigures

Faisable techniquement.

Approche recommandee :

- un profil navigateur dedie par enqueteur ou par dossier ;
- connexion manuelle initiale par l'utilisateur ;
- cookies et sessions conserves dans `zendriver-profile/` ou un profil configurable ;
- pas de stockage de mots de passe dans le code ;
- pas de bypass de captcha, 2FA ou controle anti-robot ;
- confirmation utilisateur avant toute action qui pourrait modifier un compte, poster, suivre, liker, envoyer un message ou transmettre des donnees.

Ce que Synthesix peut faire :

- ouvrir Instagram ou un autre site ;
- attendre que l'utilisateur soit connecte ;
- cliquer dans la barre de recherche ;
- saisir le nom ou pseudo ;
- afficher les resultats ;
- capturer l'URL, le titre, quelques elements visibles et une capture HTML/screenshot si utile.

Ce que Synthesix ne devrait pas faire par defaut :

- contourner les protections anti-bot ;
- scraper massivement des profils ;
- collecter des donnees privees non accessibles normalement ;
- envoyer des messages ou interagir avec des comptes ;
- stocker des credentials dans des fichiers projet.

## 5. Architecture proposee

### Niveau 1 : Search engines

Continuer le modele actuel :

- un fichier par moteur ;
- `construct_url()`;
- `parse_results()`;
- gestion timeout/retry via orchestrateur ;
- rapport unifie.

Exemples futurs :

- `startpage.py`
- `qwant.py`
- `mojeek.py`
- `searxng.py`

### Niveau 2 : Site search connectors

Ajouter un nouveau type de module, separe des moteurs web :

- `connectors/instagram.py`
- `connectors/tiktok.py`
- `connectors/github.py`
- `connectors/linkedin.py`

Interface possible :

```python
class SiteConnector:
    name: str

    async def search_identity(self, browser, query: str) -> SiteSearchResult:
        ...
```

Resultat possible :

```python
SiteSearchResult(
    source="Instagram",
    query="john doe",
    url="https://www.instagram.com/...",
    status="opened",
    artifacts={
        "screenshot": "...",
        "html": "...",
    },
)
```

### Niveau 3 : Workflows OSINT

Ajouter des workflows au-dessus :

- recherche web classique ;
- recherche de pseudo ;
- recherche de nom complet ;
- recherche d'entreprise ;
- recherche de domaine ;
- recherche de mail ;
- recherche de telephone ;
- recherche par image, plus tard.

Ces workflows orchestrent plusieurs moteurs/connecteurs, mais ne remplacent pas les modules de base.

## 6. UI / UX proposee

Ajouter des modes dans la home :

- Web Search : comportement actuel.
- Username Search : pseudo sur moteurs + sites.
- Name Search : nom/personne avec variantes.
- Domain Search : domaine, DNS, certificats, archives.
- Company Search : entreprise, registres, web.

Pour les sites necessitant login :

- bouton "Open source" ;
- statut "Logged in / Login required / Blocked / Manual action needed" ;
- pas d'automatisation agressive ;
- l'utilisateur peut reprendre la main dans l'onglet.

## 7. Ordre d'implementation recommande

### Etape 1 : socle connecteurs

- Creer `connectors/`.
- Definir `SiteConnector`.
- Definir `SiteSearchResult`.
- Ajouter un orchestrateur `site_search_orchestrator.py`.
- Ajouter tests unitaires sans navigateur avec faux connecteurs.

### Etape 2 : premier connecteur simple

Commencer par GitHub ou Reddit, pas Instagram.

Raison :

- moins fragile ;
- plus public ;
- plus testable ;
- moins de risque de compte bloque.

### Etape 3 : UI modes

- Ajouter un selecteur de mode sur la home.
- Garder Web Search par defaut.
- Ajouter Username Search en premier.

### Etape 4 : connecteurs avec session navigateur

- Instagram en mode assiste.
- TikTok en mode assiste.
- LinkedIn en mode assiste.

Principe : ouvrir, pre-remplir, laisser l'enqueteur verifier.

### Etape 5 : rapport OSINT

- Rapport par entite recherchee.
- Sources groupees par type.
- Statuts par source.
- Liens vers onglets et captures.
- Horodatage et requete exacte.

## 8. Risques principaux

- Fragilite UI : Instagram, TikTok, LinkedIn changent souvent leur DOM.
- Comptes bloques : automatisation trop rapide ou trop repetee.
- Conditions d'utilisation : certains sites limitent l'automatisation.
- Captchas et 2FA : doivent rester manuels.
- Faux positifs : un pseudo identique ne prouve pas une identite.
- Donnees sensibles : attention a la conservation locale des resultats.

## 9. Decision recommandee

Oui, l'idee est faisable.

La meilleure trajectoire est :

1. garder les moteurs web actuels stables ;
2. ajouter 2 ou 3 moteurs supplementaires faciles : Qwant, Startpage, SearXNG ;
3. creer un systeme de connecteurs OSINT separe ;
4. commencer par GitHub/Reddit ;
5. ajouter Instagram seulement en mode assiste, pas en scraping autonome.
