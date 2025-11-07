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

    def is_project_archived(self, project_key: str) -> bool:
        """
        Vérifie si un projet est déjà archivé.

        Args:
            project_key: Clé du projet à vérifier

        Returns:
            True si le projet est archivé, False sinon
        """
        try:
            # Utiliser l'API REST pour obtenir les détails complets du projet
            project_url = f"{self.jira_url}/rest/api/3/project/{project_key}"
            response = self.jira._session.get(project_url)

            if response.status_code == 200:
                project_data = response.json()
                is_archived = project_data.get('archived', False)
                return is_archived
            else:
                logger.warning(
                    f"Impossible de vérifier l'état d'archivage de {project_key}: "
                    f"Status {response.status_code}"
                )
                return False
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de l'état de {project_key}: {e}")
            return False

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

    def archive_project(self, project_key: str) -> dict:
        """
        Archive un projet Jira spécifique.

        Args:
            project_key: Clé du projet à archiver

        Returns:
            Dictionnaire avec le statut:
            {"status": "success"|"failed"|"already_archived"|"not_found", "message": str}
        """
        try:
            project = self.jira.project(project_key)

            # Vérifier si le projet existe
            if not project:
                logger.warning(f"Projet {project_key} introuvable")
                return {"status": "not_found", "message": "Projet introuvable"}

            # Vérifier si le projet est déjà archivé
            if self.is_project_archived(project_key):
                logger.info(f"⊙ Projet {project_key} - {project.name} déjà archivé, ignoré")
                return {"status": "already_archived", "message": "Projet déjà archivé"}

            logger.info(f"Archivage du projet: {project_key} - {project.name}")

            # Note: L'API Jira ne fournit pas de méthode directe pour archiver
            # Il faut utiliser l'API REST directement
            archive_url = f"{self.jira_url}/rest/api/3/project/{project_key}/archive"

            try:
                response = self.jira._session.post(archive_url)

                if response.status_code == 204:
                    logger.info(f"✓ Projet {project_key} archivé avec succès")
                    return {"status": "success", "message": "Archivage réussi"}
                elif response.status_code == 403:
                    logger.error(f"✗ Permissions insuffisantes pour archiver {project_key}")
                    return {"status": "failed", "message": "Permissions insuffisantes"}
                else:
                    logger.error(
                        f"✗ Erreur lors de l'archivage de {project_key}: "
                        f"Status {response.status_code}"
                    )
                    return {"status": "failed", "message": f"Erreur HTTP {response.status_code}"}
            except Exception as e:
                logger.error(f"✗ Erreur lors de l'archivage de {project_key}: {e}")
                return {"status": "failed", "message": str(e)}

        except JIRAError as e:
            logger.error(f"✗ Erreur Jira pour le projet {project_key}: {e}")
            return {"status": "failed", "message": f"Erreur Jira: {e}"}
        except Exception as e:
            logger.error(f"✗ Erreur inattendue pour {project_key}: {e}")
            return {"status": "failed", "message": str(e)}

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
            "already_archived": 0,
            "not_found": 0,
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"Démarrage de l'archivage de {results['total']} projets")

        for project_key in project_keys:
            result = self.archive_project(project_key)
            status = result.get("status", "failed")

            if status == "success":
                results["success"] += 1
            elif status == "already_archived":
                results["already_archived"] += 1
            elif status == "not_found":
                results["not_found"] += 1
            else:
                results["failed"] += 1

        logger.info(
            f"Archivage terminé: {results['success']} réussis, "
            f"{results['already_archived']} déjà archivés, "
            f"{results['not_found']} introuvables, "
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
            is_archived = self.is_project_archived(project_key)

            return {
                "key": project.key,
                "name": project.name,
                "description": project.description if hasattr(project, 'description') else "",
                "lead": str(project.lead) if hasattr(project, 'lead') else "",
                "project_type": project.projectTypeKey if hasattr(project, 'projectTypeKey') else "",
                "archived": is_archived,
            }
        except JIRAError as e:
            logger.error(f"Erreur lors de la récupération du projet {project_key}: {e}")
            return {}
