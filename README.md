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

### 3. Installer les dépendances

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

### 3. Archiver les projets

```bash
python -m src.archivage_jira.main projects.json
```

### Options de ligne de commande

```bash
python -m src.archivage_jira.main --help
```

Options disponibles:
- `json_file`: Chemin vers le fichier JSON (obligatoire)
- `--jira-url`: URL de l'instance Jira (optionnel si défini dans .env)
- `--username`: Nom d'utilisateur Jira (optionnel si défini dans .env)
- `--api-token`: Token API Jira (optionnel si défini dans .env)
- `--info`: Afficher uniquement les informations sans archiver

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
- ✅ Chargement des clés de projets depuis fichier JSON
- ✅ Logs détaillés de chaque opération
- ✅ Gestion des erreurs et permissions
- ✅ Mode information pour vérifier avant archivage
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

## Résolution de problèmes

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
