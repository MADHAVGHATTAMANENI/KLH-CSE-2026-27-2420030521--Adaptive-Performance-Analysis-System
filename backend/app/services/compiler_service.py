import asyncio
import os
import shutil
import time
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.exceptions import (
    CompilationFailedError,
    EntityNotFoundError,
    SecurityPolicyViolationError,
)
from app.core.logging import logger
from app.core.security import SecurityValidationError, validate_and_sanitize_flags
from app.models.compilation import Compilation
from app.models.source_file import SourceFile


class CompilerService:
    """
    Compiler Orchestration Service
    Handles secure Clang/LLVM compilation with whitelisted flags, timeout enforcement,
    diagnostic extraction, and binary artifact tracking.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def compile_source_file(
        self,
        source_file_id: str,
        optimization_level: str = "-O0",
        compiler_flags: Optional[List[str]] = None,
    ) -> Compilation:
        """
        Compiles a stored C/C++ source file using Clang.
        """
        flags = compiler_flags or []

        # 1. Validate flags against security policy
        try:
            sanitized_flags = validate_and_sanitize_flags(optimization_level, flags)
        except SecurityValidationError as e:
            raise SecurityPolicyViolationError(str(e))

        # 2. Retrieve source file
        stmt = select(SourceFile).where(SourceFile.id == source_file_id)
        result = await self.db.execute(stmt)
        source_file = result.scalar_one_or_none()
        if not source_file:
            raise EntityNotFoundError("SourceFile", source_file_id)

        # 3. Determine compiler tool based on file extension
        is_cpp = source_file.filename.endswith((".cpp", ".hpp", ".cc", ".cxx"))
        compiler_bin = shutil.which("clang++") if is_cpp else shutil.which("clang")
        if not compiler_bin:
            compiler_bin = "clang++" if is_cpp else "clang"

        # 4. Prepare temporary working directory
        build_dir = os.path.abspath(f"/tmp/compilerx_builds/{source_file.id}_{optimization_level.replace('-', '')}")
        os.makedirs(build_dir, exist_ok=True)

        src_path = os.path.join(build_dir, source_file.filename)
        bin_path = os.path.join(build_dir, f"bin_{optimization_level.replace('-', '')}")

        with open(src_path, "w", encoding="utf-8") as f:
            f.write(source_file.content)

        # 5. Programmatic command array (NO shell=True)
        # sanitized_flags already contains optimization_level as first item
        cmd = [compiler_bin] + sanitized_flags + ["-fdiagnostics-color=never", "-o", bin_path, src_path]

        logger.info(
            "compilation_started",
            file_id=source_file_id,
            opt_level=optimization_level,
            flags=sanitized_flags,
            cmd=" ".join(cmd),
        )

        start_time = time.perf_counter()
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(),
                timeout=settings.COMPILATION_TIMEOUT_SEC,
            )
            exit_code = proc.returncode or 0
        except asyncio.TimeoutError:
            try:
                proc.kill()
            except Exception:
                pass
            raise CompilationFailedError(
                stderr=f"Compilation timed out after {settings.COMPILATION_TIMEOUT_SEC} seconds.",
                exit_code=124,
            )
        finally:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        stdout_str = stdout_bytes.decode("utf-8", errors="replace")
        stderr_str = stderr_bytes.decode("utf-8", errors="replace")
        success = (exit_code == 0)

        binary_size = None
        persisted_bin_path = None
        if success and os.path.exists(bin_path):
            binary_size = os.path.getsize(bin_path)
            persisted_bin_path = bin_path

        # 6. Persist compilation record
        compilation = Compilation(
            source_file_id=source_file.id,
            optimization_level=optimization_level,
            compiler_flags=flags,
            success=success,
            stdout=stdout_str,
            stderr=stderr_str,
            exit_code=exit_code,
            compilation_time_ms=round(elapsed_ms, 2),
            binary_size_bytes=binary_size,
            binary_path=persisted_bin_path,
        )
        self.db.add(compilation)
        await self.db.flush()
        await self.db.refresh(compilation)

        logger.info(
            "compilation_finished",
            compilation_id=compilation.id,
            success=success,
            exit_code=exit_code,
            time_ms=compilation.compilation_time_ms,
            binary_size=binary_size,
        )

        return compilation
