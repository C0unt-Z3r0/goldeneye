"""
goldeneye/core/project_manager.py
Gerenciador de projetos - CRUD e estrutura de pastas.
"""

from pathlib import Path
from typing import Optional, List
from datetime import datetime

from goldeneye.core.database import get_db, init_db
from goldeneye.core.models import Project, AssessmentType, ProjectStatus

PROJECTS_DIR = Path.home() / "goldeneye" / "projects"


class ProjectManager:
    """Gerencia criação, listagem, carregamento e remoção de projetos."""

    def __init__(self):
        init_db()
        PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

    def create(self, name: str, client: str, target: str,
               assessment_type: AssessmentType = AssessmentType.EXTERNO,
               description: str = None) -> Project:
        """Cria um novo projeto no banco e no disco."""
        db = get_db()

        # Criar slug seguro para pasta
        slug = name.lower().replace(" ", "_").replace("/", "_")
        project_path = PROJECTS_DIR / slug
        project_path.mkdir(parents=True, exist_ok=True)

        # Subpastas
        (project_path / "scans").mkdir(exist_ok=True)
        (project_path / "evidence").mkdir(exist_ok=True)
        (project_path / "reports").mkdir(exist_ok=True)
        (project_path / "logs").mkdir(exist_ok=True)

        project = Project(
            name=name,
            client=client,
            target=target,
            assessment_type=assessment_type,
            status=ProjectStatus.DRAFT,
            description=description,
            project_path=str(project_path),
        )

        db.add(project)
        db.commit()
        db.refresh(project)
        db.close()

        return project

    def list_all(self) -> List[Project]:
        """Lista todos os projetos."""
        db = get_db()
        projects = db.query(Project).order_by(Project.updated_at.desc()).all()
        db.close()
        return projects

    def get_by_id(self, project_id: int) -> Optional[Project]:
        """Busca projeto por ID."""
        db = get_db()
        project = db.query(Project).filter(Project.id == project_id).first()
        db.close()
        return project

    def get_by_name(self, name: str) -> Optional[Project]:
        """Busca projeto por nome."""
        db = get_db()
        project = db.query(Project).filter(Project.name == name).first()
        db.close()
        return project

    def update_status(self, project_id: int, status: ProjectStatus):
        """Atualiza o status de um projeto."""
        db = get_db()
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            project.status = status
            project.updated_at = datetime.now()
            db.commit()
        db.close()

    def delete(self, project_id: int) -> bool:
        """Remove um projeto do banco."""
        db = get_db()
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            db.delete(project)
            db.commit()
            db.close()
            return True
        db.close()
        return False
