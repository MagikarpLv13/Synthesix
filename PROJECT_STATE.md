# PROJECT_STATE.md — État court du projet

Mise à jour : 2026-10-30. Source de vérité opérationnelle : `AI_WORKLOG.md`.

## Cible produit

Synthesix est une application locale prête à lancer pour les dorks
multi-requêtes, l'agrégation des résultats et les profils persistants de sock
puppets. L'investigation appartient à ZeroNeurone avec ZNELFP, séparément.

## État livré sur la branche

- Branche : `codex/browser-refocus`.
- Sources initiales préservées dans le commit `0e58af1` ; aucun profil, base
  runtime ni contenu d'enquête ajouté aux commits.
- `python main.py` lance désormais le navigateur recentré, sans import des
  modules d'enquête, sans overlay et sans scheduler de monitoring.
- Interface Lit : recherche, résultats progressifs, profils, historique ;
  dorks explicites préservés et mode automatique en phrase exacte disponible.
- `SearchOrchestrator.collect()` conserve concurrence bornée, isolation des
  moteurs, délais, reprises, annulation, scoring et déduplication. Aucun
  import de rendu de rapport dans ce parcours. Les utilitaires HTML restent
  disponibles séparément et leurs tests de liens sont conservés.
- `app/runtime.py` accepte les commandes uniquement depuis le document local
  d'accueil reconnu et conserve sa connexion CDP initialisée par target.
  Les heartbeats ne retransmettent pas les résultats à chaque passage.
- Les personas sont ouvertes nativement, sans attachement CDP, dans des
  répertoires séparés. Le profil neutre et celui de recherche sont distincts.
- Recherches et métadonnées des profils : `data/browser.sqlite`, schéma version 1.
  L'ancienne base `data/synthesix.db` et les preuves ne sont ni ouvertes ni migrées.
- Bundle unique `assets/synthesix-ui.js` ; les sources et bundles d'overlay,
  l'extension Synthesix, les modules d'enquête/analyse/preuves/export/monitoring
  et les tests propres aux fonctions retirées sont supprimés de cette branche.
- Construction Windows avec PyInstaller, dépendance de build uniquement ;
  paquet en dossier et archive ZIP, navigateur installé requis.

## Décisions actuelles

- Python 3.10+, Zendriver fixé et Chrome/Brave natif sont conservés.
- L'interface reste locale `file://`, avec Lit et bundle IIFE classique.
- Pas de serveur, de cloud ou de nouveau framework d'interface.
- Pas de gestion des mots de passe : la connexion se fait dans chaque persona.
- Pas de synchronisation des enquêtes ni de contrat ZNELFP inventé.
- Les décisions anciennes relatives à l'extension et aux preuves sont
  remplacées pour la cible produit ; leur historique reste dans les tâches et
  le journal. Le nouveau périmètre est explicité par DEC-002 et DEC-003.

## Vérifications

222 tests unitaires passent ; typecheck/build et smoke Chrome/profils/exécutable
sont validés. Une recherche Bing réelle a aussi abouti. Les détails figurent dans
`AI_WORKLOG.md`, lot AI-20261030-002. Les tests moteurs et leurs fixtures sont
conservés. Les tests d'enquêtes retirés correspondent aux fonctions supprimées ;
les gardes du nouveau lancement, du transport, de l'i18n et des profils sont
présentes dans les nouveaux tests.

## Limites connues

- Pas de migration automatique des anciennes enquêtes ou de l'ancien historique.
- Connexions à des comptes réels et utilisation de ZNELFP non testées.
- La validation du parcours UI emploie des moteurs simulés ; aucune garantie
  de disponibilité des moteurs externes et aucun gain de vitesse chiffré.
- Paquet Windows local non signé ; autres plateformes non empaquetées.
- Les fenêtres de personas restent indépendantes après fermeture de Synthesix.

Voir `README.md`, `docs/ARCHITECTURE_NAVIGATEUR.md` et la tâche T-058.
