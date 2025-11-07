"""
Script principal pour l'archivage de projets Jira.
"""

import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

from .archiver import JiraArchiver


def main():
    """Point d'entrée principal du programme."""
    parser = argparse.ArgumentParser(
        description="Outil d'archivage de projets Jira à partir d'un fichier JSON"
    )
    parser.add_argument(
        "json_file",
        type=Path,
        help="Chemin vers le fichier JSON contenant les clés de projets"
    )
    parser.add_argument(
        "--jira-url",
        type=str,
        help="URL de l'instance Jira (ou utilisez JIRA_URL dans .env)"
    )
    parser.add_argument(
        "--username",
        type=str,
        help="Nom d'utilisateur Jira (ou utilisez JIRA_USERNAME dans .env)"
    )
    parser.add_argument(
        "--api-token",
        type=str,
        help="Token API Jira (ou utilisez JIRA_API_TOKEN dans .env)"
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Afficher les informations des projets sans les archiver"
    )

    args = parser.parse_args()

    # Charger les variables d'environnement depuis .env
    load_dotenv()

    # Récupérer les informations de connexion
    jira_url = args.jira_url or os.getenv("JIRA_URL")
    username = args.username or os.getenv("JIRA_USERNAME")
    api_token = args.api_token or os.getenv("JIRA_API_TOKEN")

    # Vérifier que toutes les informations requises sont présentes
    if not all([jira_url, username, api_token]):
        print("❌ Erreur: Informations de connexion manquantes")
        print("Veuillez fournir:")
        print("  - JIRA_URL (via --jira-url ou .env)")
        print("  - JIRA_USERNAME (via --username ou .env)")
        print("  - JIRA_API_TOKEN (via --api-token ou .env)")
        sys.exit(1)

    # Vérifier que le fichier JSON existe
    if not args.json_file.exists():
        print(f"❌ Erreur: Le fichier {args.json_file} n'existe pas")
        sys.exit(1)

    try:
        # Initialiser l'archiveur
        archiver = JiraArchiver(jira_url, username, api_token)

        if args.info:
            # Mode information uniquement
            print(f"\n📋 Récupération des informations des projets depuis {args.json_file}\n")
            project_keys = archiver.load_project_keys(args.json_file)

            for project_key in project_keys:
                info = archiver.get_project_info(project_key)
                if info:
                    archived_status = "Oui ✓" if info.get('archived', False) else "Non"
                    print(f"Projet: {info.get('key', 'N/A')}")
                    print(f"  Nom: {info.get('name', 'N/A')}")
                    print(f"  Description: {info.get('description', 'N/A')}")
                    print(f"  Chef de projet: {info.get('lead', 'N/A')}")
                    print(f"  Type: {info.get('project_type', 'N/A')}")
                    print(f"  Archivé: {archived_status}")
                    print()
        else:
            # Mode archivage
            print(f"\n🗄️  Démarrage de l'archivage des projets depuis {args.json_file}\n")
            results = archiver.archive_projects_from_file(args.json_file)

            print("\n" + "=" * 60)
            print("📊 RÉSULTATS DE L'ARCHIVAGE")
            print("=" * 60)
            print(f"Total de projets traités: {results['total']}")
            print(f"✓ Archivés avec succès: {results['success']}")
            print(f"⊙ Déjà archivés (ignorés): {results['already_archived']}")
            print(f"? Introuvables: {results['not_found']}")
            print(f"✗ Échecs: {results['failed']}")
            print(f"Horodatage: {results['timestamp']}")
            print("=" * 60)

            if results['failed'] > 0:
                sys.exit(1)

    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
