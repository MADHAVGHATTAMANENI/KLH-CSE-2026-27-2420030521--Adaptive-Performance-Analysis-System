import hashlib
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.project import Project


class SourceFile(Base, UUIDMixin, TimestampMixin):
    """
    Source Code File Entity
    Represents an uploaded or authored C/C++ program.
    """
    __tablename__ = "source_files"

    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="source_files",
    )

    @staticmethod
    def compute_hash(code: str) -> str:
        """Returns the SHA-256 hexadecimal digest of source code content."""
        return hashlib.sha256(code.encode("utf-8")).hexdigest()

    def __repr__(self) -> str:
        return f"<SourceFile(id='{self.id}', filename='{self.filename}', size={self.size_bytes}B)>"
