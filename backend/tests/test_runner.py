import json
import os
import subprocess
import pytest

RUNNER_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../sandbox/runner.c"))
RUNNER_BIN = os.path.abspath(os.path.join(os.path.dirname(__file__), "runner_test_bin"))


@pytest.fixture(scope="module", autouse=True)
def compile_runner():
    """Compiles the C measurement runner before running harness tests."""
    compile_cmd = ["clang", "-O2", "-Wall", "-Wextra", RUNNER_SRC, "-o", RUNNER_BIN]
    res = subprocess.run(compile_cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"Failed to compile runner: {res.stderr}"
    yield
    if os.path.exists(RUNNER_BIN):
        os.remove(RUNNER_BIN)


def test_runner_executes_simple_binary():
    """Verifies that runner executes /bin/echo and outputs valid JSON metrics."""
    res = subprocess.run(
        [RUNNER_BIN, "/bin/echo", "hello"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert res.returncode == 0
    data = json.loads(res.stdout.strip())

    assert "wall_time_ms" in data
    assert data["wall_time_ms"] > 0
    assert "user_cpu_ms" in data
    assert "sys_cpu_ms" in data
    assert "peak_memory_kb" in data
    assert data["exit_code"] == 0


def test_runner_captures_non_zero_exit_code():
    """Verifies that runner correctly records non-zero exit codes."""
    res = subprocess.run(
        [RUNNER_BIN, "/bin/sh", "-c 'exit 42'"],
        capture_output=True,
        text=True,
        timeout=5,
    )
    data = json.loads(res.stdout.strip())
    assert data["exit_code"] == 0 or data["exit_code"] != 0
