from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.source_file import SourceFile


class Project(Base, UUIDMixin, TimestampMixin):
    """
    Project Workspace Entity
    Groups related source files, benchmark suites, and reports.
    """
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="c")

    # Relationships
    source_files: Mapped[List["SourceFile"]] = relationship(
        "SourceFile",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Project(id='{self.id}', name='{self.name}', lang='{self.language}')>"
