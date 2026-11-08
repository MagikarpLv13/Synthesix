@AGENTS.md

# CLAUDE.md — Instructions propres à Claude Code

Les règles communes du projet sont définies dans `AGENTS.md`.
Le présent fichier contient uniquement les règles spécifiques à Claude Code.

## 1. Démarrage d’une tâche

Avant toute modification non triviale :

1. lire `AI_WORKLOG.md` ;
2. vérifier la branche et l’état du dépôt :

```powershell
git branch --show-current
git status --short
```

3. identifier les fichiers, contrats et tests concernés ;
4. consulter Graphify lorsque le périmètre ou les dépendances sont inconnus ;
5. déclarer la tâche et les éventuels verrous dans `AI_WORKLOG.md`.

Ne pas modifier un fichier couvert par un verrou incompatible.

Pour une correction locale évidente et sans effet contractuel, agir directement sans produire un plan inutile.

## 2. Planification

Produire un plan court lorsque la tâche :

* touche plusieurs fichiers ;
* modifie un contrat ou un comportement transversal ;
* concerne le CDP, l’overlay, les données ou les migrations ;
* nécessite plusieurs étapes de validation ;
* présente un risque de régression important.

Le plan doit préciser :

* le résultat attendu ;
* les fichiers ou sous-systèmes concernés ;
* les invariants à préserver ;
* les tests prévus.

Découper les travaux importants en lots cohérents et vérifiables.

Ne pas effectuer de nettoyage, refactorisation ou renommage hors périmètre.

## 3. Exploration du code

Avant de modifier un comportement :

* rechercher ses définitions et références ;
* identifier les producteurs et consommateurs ;
* lire les tests existants ;
* vérifier les conventions des fichiers voisins.

Utiliser Graphify pour sélectionner les fichiers pertinents lorsque la localisation ou les dépendances ne sont pas évidentes.

Le graphe sert à orienter l’exploration. Le code source et les tests restent les sources de vérité.

Ne pas charger de larges portions du dépôt lorsque quelques fichiers ciblés suffisent.

## 4. Utilisation des sous-agents

Utiliser les sous-agents principalement pour :

* l’exploration en lecture seule ;
* l’inventaire des références ;
* l’analyse d’un sous-système ;
* la recherche de tests concernés ;
* la revue d’un diff ;
* la vérification d’hypothèses indépendantes.

Règles :

* un seul agent écrivain par fichier ou lot ;
* aucune écriture parallèle sur les mêmes fichiers ;
* transmettre explicitement le périmètre, les invariants et les exclusions ;
* rappeler aux sous-agents de lire les règles nécessaires ;
* demander un résultat synthétique et vérifiable ;
* contrôler leurs conclusions avant toute modification.

Ne pas multiplier les sous-agents pour une tâche simple. Chaque sous-agent consomme du contexte et des tokens supplémentaires.

## 5. Discipline d’édition

* Lire la section concernée avant de la modifier.
* Préserver le style et les conventions locales.
* Faire des modifications petites et ciblées.
* Corriger la cause racine plutôt qu’un symptôme lorsque cela reste dans le périmètre.
* Relire le diff après chaque modification structurelle.
* Modifier les sources TypeScript, jamais directement les bundles générés.
* Ne pas lancer de formatage global.
* Ne pas changer une API publique sans migration ou demande explicite.
* Ne jamais inventer un résultat de commande, de test ou d’observation.
* Ne jamais présenter une hypothèse comme un comportement vérifié.

En cas d’échec :

1. analyser la cause ;
2. tenter une correction raisonnable ;
3. documenter précisément ce qui reste bloquant ;
4. indiquer la prochaine action utile.

## 6. Validation

Exécuter les vérifications définies dans `AGENTS.md` selon le périmètre réel de la tâche.

Commencer par les tests les plus ciblés, puis élargir lorsque le changement est transversal.

Pour toute modification du frontend :

1. exécuter le typecheck ;
2. reconstruire les bundles ;
3. vérifier le diff des fichiers générés ;
4. effectuer les vérifications visuelles nécessaires.

Pour toute modification CDP ou overlay :

1. identifier les deux côtés du contrat ;
2. exécuter les tests ciblés ;
3. effectuer un smoke test réel lorsque possible ;
4. signaler explicitement les scénarios non testés.

Ne jamais déclarer un changement validé uniquement parce que le code paraît correct.

## 7. Gestion du contexte

Privilégier les lectures ciblées et les recherches précises.

Éviter de :

* relire plusieurs fois les mêmes fichiers sans raison ;
* charger intégralement un rapport lorsqu’une requête Graphify suffit ;
* recopier dans la conversation de longues portions de code inchangées ;
* répéter les règles déjà définies dans `AGENTS.md` ;
* conserver dans le contexte des sorties de commandes devenues inutiles.

Après une phase d’exploration importante, conserver une synthèse factuelle :

* fichiers pertinents ;
* contrats identifiés ;
* décision prise ;
* tests nécessaires ;
* risques restant à contrôler.

## 8. Suivi et relais

Lorsqu’une tâche doit être interrompue ou transmise, consigner dans `AI_WORKLOG.md` :

* l’objectif ;
* l’état actuel ;
* les fichiers modifiés ;
* les décisions prises ;
* les tests exécutés ;
* les résultats obtenus ;
* les inconnues ou blocages ;
* la prochaine action exacte.

Ne pas placer dans le journal :

* le raisonnement interne ;
* des hypothèses non qualifiées ;
* des logs bruts volumineux ;
* des données sensibles ;
* des informations sans utilité pour le prochain agent.

## 9. Communication

Pendant une tâche longue, fournir des points d’avancement courts et factuels.

Signaler rapidement :

* une contrainte découverte ;
* un conflit avec une règle existante ;
* un verrou bloquant ;
* un test en échec ;
* une modification de périmètre nécessaire.

Ne pas détailler les opérations évidentes ni répéter le plan à chaque étape.

## 10. Réponse finale

La réponse finale doit rester concise et contenir :

* le résultat obtenu ;
* les fichiers modifiés ;
* les tests réellement exécutés ;
* les vérifications non exécutées et leur raison ;
* les limites ou risques restants ;
* la prochaine action uniquement si elle est nécessaire.

Ne pas répéter l’intégralité du raisonnement, du diff ou des règles du projet.

Ne jamais déclarer un changement terminé ou validé sans preuve correspondante.
