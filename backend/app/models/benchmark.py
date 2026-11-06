from datetime import datetime
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, UUIDMixin


class BenchmarkSuite(Base, UUIDMixin, TimestampMixin):
    """
    Benchmark Suite Entity
    Orchestrates an end-to-end benchmark run across -O0, -O1, -O2, and -O3.
    """
    __tablename__ = "benchmark_suites"

    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_file_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("source_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    runs_per_level: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    stdin_payload: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    results: Mapped[List["BenchmarkSuiteResult"]] = relationship(
        "BenchmarkSuiteResult",
        back_populates="suite",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    runs: Mapped[List["BenchmarkRun"]] = relationship(
        "BenchmarkRun",
        back_populates="suite",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class BenchmarkRun(Base, UUIDMixin, TimestampMixin):
    """
    Individual Benchmark Execution Run
    Stores metrics captured from a single invocation of compiled binary.
    """
    __tablename__ = "benchmark_runs"

    compilation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("compilations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    suite_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("benchmark_suites.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    run_index: Mapped[int] = mapped_column(Integer, nullable=False)
    wall_time_ms: Mapped[float] = mapped_column(Float, nullable=False)
    user_cpu_time_ms: Mapped[float] = mapped_column(Float, nullable=False)
    sys_cpu_time_ms: Mapped[float] = mapped_column(Float, nullable=False)
    peak_memory_kb: Mapped[int] = mapped_column(Integer, nullable=False)
    exit_code: Mapped[int] = mapped_column(Integer, nullable=False)
    stdout: Mapped[str] = mapped_column(Text, nullable=False, default="")
    stderr: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # Relationships
    compilation = relationship("Compilation", back_populates="benchmark_runs")
    suite = relationship("BenchmarkSuite", back_populates="runs")


class BenchmarkSuiteResult(Base, UUIDMixin, TimestampMixin):
    """
    Aggregated Benchmark Statistics per Optimization Level
    """
    __tablename__ = "benchmark_suite_results"

    suite_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("benchmark_suites.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    optimization_level: Mapped[str] = mapped_column(String(4), nullable=False)
    mean_time_ms: Mapped[float] = mapped_column(Float, nullable=False)
    median_time_ms: Mapped[float] = mapped_column(Float, nullable=False)
    stddev_time_ms: Mapped[float] = mapped_column(Float, nullable=False)
    min_time_ms: Mapped[float] = mapped_column(Float, nullable=False)
    max_time_ms: Mapped[float] = mapped_column(Float, nullable=False)
    variance_cv_percent: Mapped[float] = mapped_column(Float, nullable=False)
    speedup_vs_o0: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    peak_memory_kb: Mapped[int] = mapped_column(Integer, nullable=False)
    binary_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    has_high_variance: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relationships
    suite = relationship("BenchmarkSuite", back_populates="results")
