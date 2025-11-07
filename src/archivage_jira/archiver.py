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

    def get_project_issues(self, project_key: str, max_results: int = 1000) -> List[dict]:
        """
        Récupère toutes les issues d'un projet, y compris pour les projets archivés.

        Args:
            project_key: Clé du projet
            max_results: Nombre maximum d'issues à récupérer (par batch)

        Returns:
            Liste des issues avec leurs informations
        """
        try:
            issues_list = []
            start_at = 0

            logger.info(f"Récupération des issues du projet {project_key}...")

            while True:
                # JQL pour récupérer toutes les issues du projet
                jql = f"project = {project_key} ORDER BY created DESC"

                # Utiliser la nouvelle API REST v3 search/jql pour supporter les projets archivés
                # L'ancienne API /rest/api/3/search a été dépréciée
                search_url = f"{self.jira_url}/rest/api/3/search/jql"
                params = {
                    "jql": jql,
                    "startAt": start_at,
                    "maxResults": max_results,
                    "fields": "summary,status",
                    "includeArchived": "true"  # Paramètre clé pour les projets archivés
                }

                response = self.jira._session.get(search_url, params=params)

                if response.status_code != 200:
                    logger.error(
                        f"Erreur lors de la récupération des issues de {project_key}: "
                        f"Status {response.status_code}"
                    )
                    # Log de la réponse pour debug
                    try:
                        error_data = response.json()
                        logger.error(f"Détails de l'erreur: {error_data}")
                    except:
                        logger.error(f"Réponse: {response.text}")
                    break

                data = response.json()
                issues = data.get("issues", [])

                if not issues:
                    break

                for issue in issues:
                    issues_list.append({
                        "key": issue.get("key"),
                        "summary": issue.get("fields", {}).get("summary", ""),
                        "status": issue.get("fields", {}).get("status", {}).get("name", ""),
                    })

                # Si on a récupéré moins que max_results, on a tout
                if len(issues) < max_results:
                    break

                start_at += max_results

            logger.info(f"✓ {len(issues_list)} issues récupérées pour {project_key}")
            return issues_list

        except JIRAError as e:
            logger.error(f"Erreur lors de la récupération des issues de {project_key}: {e}")
            return []
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la récupération des issues: {e}")
            return []

    def get_all_archived_projects(self) -> List[str]:
        """
        Récupère la liste de tous les projets archivés.

        Returns:
            Liste des clés de projets archivés
        """
        try:
            archived_projects = []
            all_projects = self.jira.projects()

            logger.info(f"Vérification de l'état d'archivage de {len(all_projects)} projets...")

            for project in all_projects:
                if self.is_project_archived(project.key):
                    archived_projects.append(project.key)

            logger.info(f"✓ {len(archived_projects)} projets archivés trouvés")
            return archived_projects

        except JIRAError as e:
            logger.error(f"Erreur lors de la récupération des projets: {e}")
            return []
        except Exception as e:
            logger.error(f"Erreur inattendue: {e}")
            return []

    def export_archived_projects(self, output_file: Path, project_keys: List[str] = None) -> dict:
        """
        Exporte les projets archivés et leurs issues dans un fichier JSON.

        Args:
            output_file: Chemin du fichier JSON de sortie
            project_keys: Liste optionnelle de clés de projets à exporter.
                         Si None, exporte tous les projets archivés.

        Returns:
            Dictionnaire avec les statistiques d'export
        """
        try:
            # Si aucune liste fournie, récupérer tous les projets archivés
            if project_keys is None:
                logger.info("Recherche de tous les projets archivés...")
                project_keys = self.get_all_archived_projects()
            else:
                # Filtrer pour ne garder que les projets archivés
                logger.info(f"Vérification de l'état d'archivage de {len(project_keys)} projets...")
                archived_keys = []
                for key in project_keys:
                    if self.is_project_archived(key):
                        archived_keys.append(key)
                    else:
                        logger.warning(f"⚠ Projet {key} n'est pas archivé, ignoré")
                project_keys = archived_keys

            if not project_keys:
                logger.warning("Aucun projet archivé à exporter")
                return {
                    "total_projects": 0,
                    "total_issues": 0,
                    "timestamp": datetime.now().isoformat()
                }

            export_data = {
                "export_date": datetime.now().isoformat(),
                "total_projects": len(project_keys),
                "projects": []
            }

            total_issues = 0

            for project_key in project_keys:
                logger.info(f"Export du projet {project_key}...")
                project_info = self.get_project_info(project_key)

                if not project_info:
                    logger.warning(f"⚠ Impossible de récupérer les infos de {project_key}")
                    continue

                issues = self.get_project_issues(project_key)
                total_issues += len(issues)

                project_data = {
                    "key": project_info.get("key"),
                    "name": project_info.get("name"),
                    "description": project_info.get("description", ""),
                    "lead": project_info.get("lead", ""),
                    "project_type": project_info.get("project_type", ""),
                    "total_issues": len(issues),
                    "issues": issues
                }

                export_data["projects"].append(project_data)

            export_data["total_issues"] = total_issues

            # Écrire le fichier JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            logger.info(
                f"✓ Export terminé: {len(project_keys)} projets et "
                f"{total_issues} issues exportés vers {output_file}"
            )

            return {
                "total_projects": len(project_keys),
                "total_issues": total_issues,
                "output_file": str(output_file),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Erreur lors de l'export: {e}")
            raise
