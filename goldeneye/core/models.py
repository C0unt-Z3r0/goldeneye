"""
goldeneye/core/models.py
Modelos de dados do Goldeneye - SQLAlchemy ORM.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import enum


class Base(DeclarativeBase):
    pass


class AssessmentType(str, enum.Enum):
    INTERNO = "interno"
    EXTERNO = "externo"
    WEB = "web"
    COMPLETO = "completo"
    CONFIG = "configuracao"


class ProjectStatus(str, enum.Enum):
    DRAFT = "rascunho"
    IN_PROGRESS = "em_andamento"
    COMPLETED = "concluido"
    ARCHIVED = "arquivado"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    client: Mapped[str] = mapped_column(String(200), nullable=False)
    target: Mapped[str] = mapped_column(String(500), nullable=False)
    assessment_type: Mapped[AssessmentType] = mapped_column(
        SQLEnum(AssessmentType), default=AssessmentType.EXTERNO
    )
    status: Mapped[ProjectStatus] = mapped_column(
        SQLEnum(ProjectStatus), default=ProjectStatus.DRAFT
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    scope_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    project_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', client='{self.client}')>"
