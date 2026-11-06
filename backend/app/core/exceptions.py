from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from datetime import datetime, timezone


class CompilerXException(Exception):
    """Base domain exception for CompilerX."""
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class EntityNotFoundError(CompilerXException):
    def __init__(self, entity_name: str, entity_id: str):
        super().__init__(
            message=f"{entity_name} with identifier '{entity_id}' was not found.",
            code="ENTITY_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"entity": entity_name, "id": entity_id},
        )


class CompilationFailedError(CompilerXException):
    def __init__(self, stderr: str, exit_code: int):
        super().__init__(
            message="Compilation failed with syntax or semantic errors.",
            code="COMPILATION_FAILED",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"stderr": stderr, "exit_code": exit_code},
        )


class BenchmarkTimeoutError(CompilerXException):
    def __init__(self, timeout_sec: float):
        super().__init__(
            message=f"Benchmark execution exceeded hard deadline of {timeout_sec}s.",
            code="BENCHMARK_TIMEOUT",
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            details={"timeout_sec": timeout_sec},
        )


class SecurityPolicyViolationError(CompilerXException):
    def __init__(self, reason: str):
        super().__init__(
            message=f"Request violated security policy: {reason}",
            code="SECURITY_VIOLATION",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"reason": reason},
        )


async def compilerx_exception_handler(
    request: Request,
    exc: CompilerXException
) -> JSONResponse:
    """Standardized JSON envelope for all domain exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.code,
            "message": exc.message,
            "status_code": exc.status_code,
            "details": exc.details,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
