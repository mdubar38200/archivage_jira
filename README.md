# Archivage Jira

Outil Python pour l'archivage automatique de projets Jira à partir d'un fichier JSON contenant les clés des projets.

## Prérequis

- Python 3.13 ou 3.14
- Un compte Jira avec les permissions d'administration de projets
- Un token API Jira

## Installation

### 1. Cloner le projet

```bash
git clone <url-du-repo>
cd archivage_jira
```

### 2. Créer un environnement virtuel

```bash
python3.13 -m venv venv
source venv/bin/activate  # Sur Linux/Mac
# ou
.\venv\Scripts\activate  # Sur Windows
```

### 3. Installer le package

Option A - Installation en mode développement (recommandé):
```bash
pip install -e .
```

Option B - Installation des dépendances uniquement:
```bash
pip install -r requirements.txt
```

### 4. Configuration

Copiez le fichier `.env.example` vers `.env` et remplissez vos informations:

```bash
cp .env.example .env
```

Éditez le fichier `.env`:

```env
JIRA_URL=https://votre-instance.atlassian.net
JIRA_USERNAME=votre-email@example.com
JIRA_API_TOKEN=votre_token_api
```

#### Créer un token API Jira

1. Allez sur https://id.atlassian.com/manage-profile/security/api-tokens
2. Cliquez sur "Create API token"
3. Donnez-lui un nom (ex: "Archivage Script")
4. Copiez le token généré et collez-le dans votre fichier `.env`

## Utilisation

### 1. Préparer le fichier JSON

Créez un fichier JSON contenant les clés des projets à archiver:

```json
{
  "projects": [
    "PROJ1",
    "PROJ2",
    "DEMO"
  ]
}
```

Ou au format simplifié:

```json
["PROJ1", "PROJ2", "DEMO"]
```

### 2. Vérifier les informations des projets (recommandé)

Avant d'archiver, vous pouvez vérifier les informations des projets:

```bash
python -m src.archivage_jira.main projects.json --info
```

Si vous avez installé avec `pip install -e .`, vous pouvez aussi utiliser:
```bash
python -m archivage_jira.main projects.json --info
```

### 3. Archiver les projets

```bash
python -m src.archivage_jira.main projects.json
```

Ou avec l'installation en mode développement:
```bash
python -m archivage_jira.main projects.json
```

### 4. Exporter les projets archivés

Exporter tous les projets archivés avec leurs issues dans un fichier JSON:

```bash
python -m src.archivage_jira.main --export-archived export.json
```

Exporter uniquement les projets archivés listés dans un fichier JSON:

```bash
python -m src.archivage_jira.main projects.json --export-archived export.json
```

### Options de ligne de commande

```bash
python -m src.archivage_jira.main --help
```

Options disponibles:
- `json_file`: Chemin vers le fichier JSON contenant les clés de projets (optionnel avec --export-archived)
- `--jira-url`: URL de l'instance Jira (optionnel si défini dans .env)
- `--username`: Nom d'utilisateur Jira (optionnel si défini dans .env)
- `--api-token`: Token API Jira (optionnel si défini dans .env)
- `--info`: Afficher uniquement les informations sans archiver
- `--export-archived OUTPUT_FILE`: Exporter les projets archivés et leurs issues vers un fichier JSON

## Structure du projet

```
archivage_jira/
├── src/
│   └── archivage_jira/
│       ├── __init__.py
│       ├── archiver.py      # Classe principale d'archivage
│       └── main.py           # Point d'entrée du script
├── .env.example              # Exemple de configuration
├── .gitignore
├── projects.example.json     # Exemple de fichier de projets
├── pyproject.toml           # Configuration Python 3.13+
├── requirements.txt         # Dépendances
└── README.md
```

## Fonctionnalités

- ✅ Archivage de projets Jira via API REST
- ✅ Vérification automatique de l'état d'archivage (évite d'archiver les projets déjà archivés)
- ✅ Export des projets archivés avec toutes leurs issues au format JSON
- ✅ Chargement des clés de projets depuis fichier JSON
- ✅ Logs détaillés de chaque opération
- ✅ Gestion des erreurs et permissions
- ✅ Mode information pour vérifier avant archivage (affiche l'état archivé)
- ✅ Statistiques détaillées : réussites, échecs, déjà archivés, introuvables
- ✅ Support Python 3.13/3.14

## Exemples

### Exemple 1: Archivage simple

```bash
python -m src.archivage_jira.main projects.json
```

### Exemple 2: Vérifier avant d'archiver

```bash
python -m src.archivage_jira.main projects.json --info
```

### Exemple 3: Utiliser des paramètres en ligne de commande

```bash
python -m src.archivage_jira.main projects.json \
  --jira-url https://mycompany.atlassian.net \
  --username myemail@company.com \
  --api-token mytoken123
```

### Exemple 4: Exporter tous les projets archivés

```bash
# Exporter tous les projets archivés de l'instance
python -m src.archivage_jira.main --export-archived archived_projects.json

# Exporter uniquement certains projets archivés
python -m src.archivage_jira.main projects.json --export-archived archived_projects.json
```

## Format du fichier JSON exporté

Lors de l'utilisation de `--export-archived`, le fichier JSON généré a la structure suivante:

**Note importante**: L'export récupère automatiquement **toutes les issues** des projets archivés grâce au paramètre `includeArchived=true` de l'API Jira. Les projets archivés et leurs issues sont donc pleinement accessibles.

```json
{
  "export_date": "2025-11-07T14:30:00.123456",
  "total_projects": 3,
  "total_issues": 150,
  "projects": [
    {
      "key": "PROJ1",
      "name": "Mon Projet 1",
      "description": "Description du projet",
      "lead": "john.doe",
      "project_type": "software",
      "total_issues": 45,
      "issues": [
        {
          "key": "PROJ1-1",
          "summary": "Titre de l'issue",
          "status": "Done"
        },
        {
          "key": "PROJ1-2",
          "summary": "Autre issue",
          "status": "In Progress"
        }
      ]
    }
  ]
}
```

Ce fichier contient:
- **export_date**: Date et heure de l'export
- **total_projects**: Nombre total de projets exportés
- **total_issues**: Nombre total d'issues exportées
- **projects**: Liste des projets avec leurs informations et issues
  - **key**: Clé du projet
  - **name**: Nom du projet (summary)
  - **description**: Description du projet
  - **lead**: Chef de projet
  - **project_type**: Type de projet
  - **total_issues**: Nombre d'issues dans ce projet
  - **issues**: Liste des issues du projet
    - **key**: Clé de l'issue
    - **summary**: Résumé/titre de l'issue
    - **status**: Statut actuel de l'issue

## Résolution de problèmes

### Erreur ModuleNotFoundError

Si vous obtenez `ModuleNotFoundError: No module named 'archivage_jira'`:
- Assurez-vous d'être dans le répertoire racine du projet
- Utilisez `python -m src.archivage_jira.main` au lieu de `python -m archivage_jira.main`
- Ou installez le package en mode développement: `pip install -e .`

### Erreur de permissions

Si vous obtenez une erreur 403, vérifiez que:
- Votre compte a les permissions d'archivage de projets
- Le token API est valide et non expiré

### Projet introuvable

Si un projet n'est pas trouvé:
- Vérifiez que la clé du projet est correcte (sensible à la casse)
- Assurez-vous d'avoir accès au projet

### Erreur de connexion

Si la connexion échoue:
- Vérifiez l'URL de votre instance Jira
- Vérifiez que le token API est correct
- Vérifiez votre connexion internet

### Issues des projets archivés

L'outil utilise le paramètre `includeArchived=true` de l'API REST Jira (v3) pour récupérer les issues des projets archivés. Cela signifie que:
- ✅ Les issues des projets archivés sont automatiquement incluses dans l'export
- ✅ Aucune configuration spéciale n'est nécessaire
- ℹ️ L'API REST v3 est utilisée directement pour garantir la compatibilité

## Développement

### Tests

```bash
pytest
```

### Formatage du code

```bash
black src/
```

### Linting

```bash
ruff check src/
```

## Sécurité

- Ne commitez JAMAIS votre fichier `.env` (il est dans `.gitignore`)
- Conservez vos tokens API en sécurité
- Utilisez des tokens avec les permissions minimales nécessaires

## Licence

À définir

## Contribution

Les contributions sont les bienvenues! N'hésitez pas à ouvrir une issue ou une pull request.
