from typing import Optional
from sqlalchemy import Boolean, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, UUIDMixin


class Compilation(Base, UUIDMixin, TimestampMixin):
    """
    Compilation Entity
    Records every Clang compiler invocation, flags, diagnostics, and binary output.
    """
    __tablename__ = "compilations"

    source_file_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("source_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    optimization_level: Mapped[str] = mapped_column(String(4), nullable=False)
    compiler_flags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    stdout: Mapped[str] = mapped_column(Text, nullable=False, default="")
    stderr: Mapped[str] = mapped_column(Text, nullable=False, default="")
    exit_code: Mapped[int] = mapped_column(Integer, nullable=False)
    compilation_time_ms: Mapped[float] = mapped_column(Float, nullable=False)
    binary_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    binary_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Relationships
    source_file = relationship("SourceFile", backref="compilations")
    benchmark_runs = relationship(
        "BenchmarkRun",
        back_populates="compilation",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<Compilation(id='{self.id}', opt='{self.optimization_level}', "
            f"success={self.success}, time={self.compilation_time_ms:.1f}ms)>"
        )
