# T-055 — Scheduler local du monitoring

- **Statut** : done
- **Priorité** : P1
- **Effort** : élevé
- **Outil recommandé** : Claude
- **Dépendances** : T-040, T-054

## Objectif

Exécuter les moniteurs arrivés à échéance sans bloquer l'interface, avec un
autostart explicitement activable et une commande ponctuelle utilisable par le
Planificateur de tâches Windows.

## Contexte

Synthesix reste local, sans serveur obligatoire. Le scheduler doit fonctionner
dans l'application ouverte et par lancement court lorsque l'application est
fermée.

## Étapes

1. Sélectionner atomiquement les moniteurs dus.
2. Ajouter une commande `python main.py --monitor-once`.
3. Réutiliser une instance navigateur ou un onglet dédié borné.
4. Appliquer concurrence limitée, jitter, timeout, retries et backoff.
5. Recalculer `next_check_at` après chaque tentative.
6. Suspendre après échecs répétés ou challenge nécessitant une intervention.
7. Déclencher une archive complète uniquement selon la politique configurée.

## Critères d'acceptation

- Deux workers ne sondent pas simultanément le même moniteur.
- La fermeture de Synthesix arrête proprement tabs et navigateur.
- Une panne d'un site n'empêche pas les autres moniteurs de s'exécuter.
- Le mode ponctuel retourne un code de sortie et un résumé déterministes.
- Aucune recherche multi-moteur n'est relancée par le monitoring.

## Commandes de test

```powershell
.venv\Scripts\python.exe -m unittest tests.test_monitoring tests.test_browser_service tests.test_main
git diff --check
```

## Risques

- Cadence excessive, bannissement ou CAPTCHA.
- Collision avec une recherche ou une capture analyste.
- Gestion du profil navigateur et des sessions authentifiées.

## Résultat

- Migration v20 : baux SQLite `lease_owner`/`lease_expires_at` et index des
  moniteurs dus.
- Scheduler intégré à l'application et commande
  `python main.py --monitor-once`.
- Boucle en arrière-plan désactivée par défaut afin de laisser l'analyste
  établir son VPN avant tout accès réseau ; activation explicite avec
  `SYNTHESIX_MONITOR_AUTOSTART=true`. Les lancements manuels restent actifs.
- Concurrence, batch, jitter, timeout, retries, backoff, durée de bail et seuil
  d'échecs configurables par variables d'environnement.
- Suspension immédiate sur authentification, challenge ou consentement ;
  suspension après échecs répétés pour les pannes transitoires.
- Politique d'archive `never` (défaut sûr) ou `on_change`; aucune recherche
  multi-moteur n'est appelée.
- Résumé ponctuel stable et codes de sortie `0`/`1`/`2`.

## Vérifications

- Tests unitaires des claims atomiques et de l'expiration des baux.
- Tests du plafond de concurrence, des retries, de l'isolation des erreurs, de
  la suspension et de la politique d'archive.
- Smoke `--monitor-once` sur une base temporaire vide : aucun navigateur lancé.
- Smoke Chrome headless réel sur `https://example.com/` : une observation
  `ok`, bail libéré et prochaine échéance recalculée.
