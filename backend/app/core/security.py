from typing import List, Set


ALLOWED_OPTIMIZATION_LEVELS: Set[str] = {
    "-O0",
    "-O1",
    "-O2",
    "-O3",
    "-Os",
    "-Oz",
}

ALLOWED_COMPILER_FLAGS: Set[str] = {
    # Warnings & Diagnostics
    "-Wall",
    "-Wextra",
    "-pedantic",
    "-Wno-unused-variable",
    "-Wno-unused-parameter",
    "-Werror",
    # Language Standards
    "-std=c99",
    "-std=c11",
    "-std=c17",
    "-std=c++11",
    "-std=c++14",
    "-std=c++17",
    "-std=c++20",
    # Floating-Point & Math Optimizations
    "-ffast-math",
    "-fno-math-errno",
    "-fomit-frame-pointer",
    # Loop & Vectorization
    "-funroll-loops",
    "-fvectorize",
    "-fslp-vectorize",
}


class SecurityValidationError(Exception):
    """Raised when an unwhitelisted compiler flag or malicious input is detected."""
    pass


def validate_and_sanitize_flags(
    optimization_level: str,
    auxiliary_flags: List[str]
) -> List[str]:
    """
    Validates compiler flags against an explicit, immutable allowlist.
    Prevents shell command injection, path traversal, and malicious compiler plugins.
    """
    if optimization_level not in ALLOWED_OPTIMIZATION_LEVELS:
        raise SecurityValidationError(
            f"Optimization level '{optimization_level}' is not supported. "
            f"Allowed: {sorted(list(ALLOWED_OPTIMIZATION_LEVELS))}"
        )

    sanitized_flags = [optimization_level]

    for flag in auxiliary_flags:
        cleaned_flag = flag.strip()
        if not cleaned_flag:
            continue
        if cleaned_flag not in ALLOWED_COMPILER_FLAGS:
            raise SecurityValidationError(
                f"Compiler flag '{cleaned_flag}' is not permitted by the security policy."
            )
        sanitized_flags.append(cleaned_flag)

    return sanitized_flags

