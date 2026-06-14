# Installer les instructions AGENTS.md

Codex charge les instructions au démarrage d'une session. Il combine les règles globales et celles du projet, de la racine vers le dossier courant; le fichier le plus proche peut donc préciser ou remplacer les règles précédentes.

Documentation officielle: [Custom instructions with AGENTS.md](https://developers.openai.com/codex/guides/agents-md).

## Prérequis: Codex CLI

Les commandes de vérification nécessitent le CLI Codex. L'application Codex ou
l'extension d'un éditeur peut embarquer son propre exécutable sans ajouter la
commande `codex` au `PATH` du terminal.

Installation officielle sous Windows:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"
```

Alternative si Node.js et npm sont déjà installés:

```powershell
npm install -g @openai/codex
```

Fermer puis rouvrir PowerShell, puis vérifier:

```powershell
Get-Command codex
codex --version
```

Ces installations sont globales à l'utilisateur et ne doivent pas être
effectuées dans le virtualenv Python du projet.

## Installation globale

Les règles globales s'appliquent à tous les dépôts de l'utilisateur. Elles doivent rester génériques: style de réponse, sécurité et préférences de travail.

Linux, macOS ou WSL:

```bash
mkdir -p ~/.codex
nano ~/.codex/AGENTS.md
```

PowerShell:

```powershell
New-Item -ItemType Directory -Force "$HOME\.codex"
notepad "$HOME\.codex\AGENTS.md"
```

Ajouter ensuite les règles globales dans ce fichier. Si `~/.codex/AGENTS.override.md` existe et n'est pas vide, Codex le charge à la place du fichier global `AGENTS.md`.

## Installation dans un projet

Depuis la racine du dépôt:

```bash
touch AGENTS.md
```

Le fichier peut aussi être créé manuellement, puis versionné avec Git. Il doit contenir uniquement les conventions durables propres au projet: architecture, commandes, tests et contraintes de compatibilité.

## Vérification

Depuis la racine du dépôt:

```bash
codex --ask-for-approval never "Summarize the current instructions."
```

Pour vérifier les instructions actives depuis un sous-dossier:

```bash
codex --cd path/to/subdir --ask-for-approval never "Show which instruction files are active."
```

Relancer Codex après une modification: la chaîne d'instructions est reconstruite au début de chaque session.

Si PowerShell indique que `codex` n'est pas reconnu, installer le CLI comme
décrit dans la section Prérequis, puis ouvrir un nouveau terminal. Vérifier
également que le dossier d'installation est présent dans la variable `PATH`.

## Bonnes pratiques

- Utiliser `~/.codex/AGENTS.md` pour les préférences personnelles valables partout.
- Utiliser le `AGENTS.md` racine pour les règles partagées et versionnées du dépôt.
- Utiliser `AGENTS.override.md` pour remplacer les règles du même niveau, par exemple temporairement ou dans un sous-projet spécialisé.
- Dans un monorepo, placer un `AGENTS.md` ou `AGENTS.override.md` dans chaque service qui nécessite des commandes ou contraintes différentes.
- Garder chaque fichier court: son contenu consomme du contexte à chaque session et la taille combinée est limitée.
- Éviter les rappels génériques, les longues explications et les règles déjà imposées par les outils.
- Placer une règle au niveau le plus proche de son périmètre afin d'éviter les contradictions.
