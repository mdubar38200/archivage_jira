"""
Module principal pour l'archivage de projets Jira.
"""

import json
import logging
from pathlib import Path
from typing import List
from datetime import datetime

from jira import JIRA
from jira.exceptions import JIRAError


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JiraArchiver:
    """Classe pour gérer l'archivage de projets Jira."""

    def __init__(self, jira_url: str, username: str, api_token: str):
        """
        Initialise la connexion Jira.

        Args:
            jira_url: URL de l'instance Jira
            username: Nom d'utilisateur ou email
            api_token: Token API Jira
        """
        self.jira_url = jira_url
        try:
            self.jira = JIRA(server=jira_url, basic_auth=(username, api_token))
            logger.info(f"Connexion réussie à {jira_url}")
        except JIRAError as e:
            logger.error(f"Erreur de connexion à Jira: {e}")
            raise

    def load_project_keys(self, json_file: Path) -> List[str]:
        """
        Charge les clés de projets depuis un fichier JSON.

        Args:
            json_file: Chemin vers le fichier JSON contenant les clés de projets

        Returns:
            Liste des clés de projets

        Format attendu du JSON:
            {
                "projects": ["PROJ1", "PROJ2", "PROJ3"]
            }
        """
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, dict) and "projects" in data:
                project_keys = data["projects"]
            elif isinstance(data, list):
                project_keys = data
            else:
                raise ValueError("Format JSON non reconnu. Utilisez {'projects': [...]} ou [...]")

            logger.info(f"Chargé {len(project_keys)} clés de projets depuis {json_file}")
            return project_keys
        except Exception as e:
            logger.error(f"Erreur lors du chargement du fichier JSON: {e}")
            raise

    def archive_project(self, project_key: str) -> bool:
        """
        Archive un projet Jira spécifique.

        Args:
            project_key: Clé du projet à archiver

        Returns:
            True si l'archivage a réussi, False sinon
        """
        try:
            project = self.jira.project(project_key)

            # Vérifier si le projet existe
            if not project:
                logger.warning(f"Projet {project_key} introuvable")
                return False

            logger.info(f"Archivage du projet: {project_key} - {project.name}")

            # Note: L'API Jira ne fournit pas de méthode directe pour archiver
            # Il faut utiliser l'API REST directement
            archive_url = f"{self.jira_url}/rest/api/3/project/{project_key}/archive"

            try:
                response = self.jira._session.post(archive_url)

                if response.status_code == 204:
                    logger.info(f"✓ Projet {project_key} archivé avec succès")
                    return True
                elif response.status_code == 403:
                    logger.error(f"✗ Permissions insuffisantes pour archiver {project_key}")
                    return False
                else:
                    logger.error(
                        f"✗ Erreur lors de l'archivage de {project_key}: "
                        f"Status {response.status_code}"
                    )
                    return False
            except Exception as e:
                logger.error(f"✗ Erreur lors de l'archivage de {project_key}: {e}")
                return False

        except JIRAError as e:
            logger.error(f"✗ Erreur Jira pour le projet {project_key}: {e}")
            return False
        except Exception as e:
            logger.error(f"✗ Erreur inattendue pour {project_key}: {e}")
            return False

    def archive_projects_from_file(self, json_file: Path) -> dict:
        """
        Archive tous les projets listés dans le fichier JSON.

        Args:
            json_file: Chemin vers le fichier JSON contenant les clés de projets

        Returns:
            Dictionnaire avec les statistiques d'archivage
        """
        project_keys = self.load_project_keys(json_file)

        results = {
            "total": len(project_keys),
            "success": 0,
            "failed": 0,
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"Démarrage de l'archivage de {results['total']} projets")

        for project_key in project_keys:
            if self.archive_project(project_key):
                results["success"] += 1
            else:
                results["failed"] += 1

        logger.info(
            f"Archivage terminé: {results['success']} réussis, "
            f"{results['failed']} échoués sur {results['total']} projets"
        )

        return results

    def get_project_info(self, project_key: str) -> dict:
        """
        Récupère les informations d'un projet.

        Args:
            project_key: Clé du projet

        Returns:
            Dictionnaire avec les informations du projet
        """
        try:
            project = self.jira.project(project_key)
            return {
                "key": project.key,
                "name": project.name,
                "description": project.description if hasattr(project, 'description') else "",
                "lead": str(project.lead) if hasattr(project, 'lead') else "",
                "project_type": project.projectTypeKey if hasattr(project, 'projectTypeKey') else "",
            }
        except JIRAError as e:
            logger.error(f"Erreur lors de la récupération du projet {project_key}: {e}")
            return {}
