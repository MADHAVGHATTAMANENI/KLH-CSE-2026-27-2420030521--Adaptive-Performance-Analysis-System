# CompilerX — Security Architecture & Threat Model (SecOps)
**AI-Powered Adaptive Code Optimization and Performance Analysis System**

---

| Field | Value |
|---|---|
| **Document Version** | 1.0.0 |
| **Status** | APPROVED — Security Specification |
| **Author** | Principal Software Architect & Technical Lead |
| **Target Course** | Adaptive Software Engineering (24CI3201), KL University |
| **Course Outcomes Covered** | CO3: Security Operations (SecOps) & Secure Software Engineering |
| **Standards Aligned** | OWASP Top 10 (2021), CIS Docker Benchmarks, NIST SP 800-190 |
| **Last Updated** | 2026-11-06 |

---

## 1. Threat Model & Zero-Trust Architecture

CompilerX provides a developer service where arbitrary users submit C and C++ source code to be compiled by Clang and executed on system hardware. Under standard operating conditions, executing unvalidated native code confers arbitrary machine control (Remote Code Execution).

Therefore, **CompilerX adopts an absolute Zero-Trust security model:**
> *All user-supplied source code, compiler flags, and stdin payloads are treated as actively hostile, malicious, and untrusted.*

### 1.1 Threat Actor Persona & Objectives
- **Attacker Profile:** Malicious internal or external user submitting exploit code via REST API endpoints.
- **Attack Objectives:**
  1. *Host Takeover:* Escaping container sandboxes to achieve root shell access on the host operating system.
  2. *Denial of Service (DoS):* Crashing or freezing the host machine through fork bombs, memory exhausters, CPU saturators, or recursive compiler macro expansions.
  3. *Filesystem Tampering / Exfiltration:* Reading sensitive host environment files (`/etc/passwd`, cloud credentials, database connection strings) or deleting host volumes.
  4. *Network Pivoting & Botnet Activity:* Establishing reverse shells, port scanning internal infrastructure, or generating outbound DDoS traffic.
  5. *Command Injection:* Injecting shell meta-characters through API parameters (e.g., in filename or compiler flag inputs).

---

## 2. Multi-Layered Defense-in-Depth Model

To prevent single-point-of-failure compromises, the system enforces isolation across six distinct physical and logical layers:

```
┌────────────────────────────────────────────────────────────────────────┐
│ Layer 1: Application Gateway & Input Validation (FastAPI / Pydantic)   │
│ [Payload Size Limits (1MB), Flag Whitelisting, Regex File Names]      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ Layer 2: Command Construction & Process Isolation                      │
│ [Zero Shell Interpolation (No shell=True), Programmatic Arg Vectors]  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ Layer 3: Container Namespaces & Network Boundary (Docker Engine)       │
│ [PID, Mount, IPC, Network Namespaces; --network none]                  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ Layer 4: Filesystem Jail & Ephemeral Storage                           │
│ [--read-only Rootfs, Ephemeral tmpfs (/tmp, /build), noexec/nosuid]    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ Layer 5: Linux Capabilities & Privilege De-escalation                  │
│ [--cap-drop=ALL, --security-opt=no-new-privileges:true, Non-root UID]  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ Layer 6: Kernel Syscall Filtration & Resource Quotas (Seccomp/cgroups) │
│ [Blocked: socket, clone, ptrace, mount; Limits: 256MB RAM, 64 PIDs]    │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Sandbox Container Hardening Specification

### 3.1 Network Isolation (`--network none`)
Every execution container is provisioned with `--network none`. The container's network namespace contains solely the loopback interface (`lo`), and outbound routing tables are non-existent.
- **Protection:** Completely neutralizes SSRF, botnet C2 connections, external data exfiltration, and local port scanning.
- **Verification Test:** C code calling `socket(AF_INET, SOCK_STREAM, 0)` and `connect()` immediately fails with `ENETUNREACH` or `EPERM`.

### 3.2 Filesystem Hardening & Read-Only Root
1. The container root filesystem is mounted strictly read-only (`--read-only`).
2. Write access is restricted to strictly bounded, in-memory `tmpfs` mounts:
   - `/tmp`: `size=64m,nodev,nosuid` (Ephemeral scratch workspace).
   - `/build`: `size=64m,nodev,nosuid` (Target directory for compiled binary artifact).
3. **Protection:** Prevents persistence across runs, filesystem tampering (`rm -rf /`), trojan binary installation, or modifying system libraries.

### 3.3 Linux Capability Stripping & Non-Root Execution
1. All standard Linux kernel capabilities are stripped: `--cap-drop=ALL`.
2. Escalation is prevented via `--security-opt=no-new-privileges:true`.
3. Processes inside the container run under an unprivileged user: `compilerx:uid=1001:gid=1001`.
4. **Protection:** Even if a zero-day vulnerability in Clang or the Linux kernel is triggered, the attacker has no administrative capabilities (`CAP_SYS_ADMIN`, `CAP_NET_ADMIN`, `CAP_DAC_OVERRIDE`) to access host devices.

### 3.4 Seccomp System-Call Filtering (`sandbox/seccomp.json`)
The Docker daemon enforces a custom **Secure Computing (Seccomp)** profile that blocks dangerous system calls at the kernel boundary:

| Syscall Group | Filter Action | Blocked Syscalls | Justification |
|---|---|---|---|
| **Network** | `SCMP_ACT_ERRNO (EPERM)` | `socket`, `bind`, `connect`, `listen`, `accept`, `sendto`, `recvfrom` | Zero network access permitted. |
| **Process Cloning** | `SCMP_ACT_ERRNO (EPERM)` | `clone` (beyond single thread), `fork` (beyond limit), `vfork` | Limits process hierarchy to harness runner. |
| **Pivoting & Debug**| `SCMP_ACT_ERRNO (EPERM)` | `ptrace`, `process_vm_readv`, `process_vm_writev` | Prevents inspecting other processes. |
| **System Modification**| `SCMP_ACT_ERRNO (EPERM)`| `mount`, `umount2`, `reboot`, `sethostname`, `init_module` | Prevents container jailbreaks. |
| **Standard Compute**| `SCMP_ACT_ALLOW` | `read`, `write`, `openat`, `close`, `mmap`, `brk`, `clock_gettime`, `exit_group` | Required for standard C/C++ execution. |

### 3.5 cgroups v2 Resource Budgets & Deadlines
To prevent host resource starvation, cgroups enforce strict hardware quotas:
- **CPU Quota:** `--cpus=1.0` (Container cannot consume more than 1 CPU core).
- **Memory Ceiling:** `--memory=256m`, `--memory-swap=256m` (Zero swap; memory hard-capped at 256 MB).
- **Process Ceiling:** `--pids-limit=64` (Hard process cap preventing fork bombs).
- **Wall-Clock Watchdog:** Execution supervisor enforces a 10.0-second hard deadline. If the process does not exit, it is sent `SIGKILL`.

---

## 4. Application Layer Security & Injection Defense

### 4.1 Zero Shell Interpolation
Under no circumstances does CompilerX invoke system shells (`/bin/sh`, `/bin/bash`, `sh -c`, `shell=True`).
- All compilations and executions use discrete argument vectors:
  ```python
  # SECURE: Explicit argument list passed to subprocess / Docker SDK
  cmd = ["clang", opt_level] + flags + ["-o", str(binary_path), str(source_path)]
  proc = await asyncio.create_subprocess_exec(*cmd, stdout=..., stderr=...)
  ```
- **Protection:** Completely eliminates shell command injection (e.g., `; rm -rf /;`, `$(cat /etc/passwd)`).

### 4.2 Compiler Flag Sanitization & Whitelist
User-supplied compiler flags are validated against an immutable, restrictive allowlist:
```python
ALLOWED_FLAGS = {
    "-Wall", "-Wextra", "-pedantic", "-Wno-unused-variable",
    "-std=c99", "-std=c11", "-std=c17", "-std=c++14", "-std=c++17", "-std=c++20",
    "-ffast-math", "-fno-math-errno", "-funroll-loops"
}
```
Any argument not present in this set triggers an immediate `422 Unprocessable Entity` validation exception before reaching the container daemon.

### 4.3 Input Validation & Size Controls
- **Source File Size Limit:** Maximum $1{,}048{,}576$ bytes (1 MB). Payloads exceeding this threshold are rejected with HTTP `413 Payload Too Large`.
- **Filename Validation:** Enforced via regex: `^[a-zA-Z0-9_\-.]+\.(c|cpp)$`. Rejects directory traversal paths (e.g. `../../etc/passwd`).
- **Input Sanitization:** Stdin payloads are limited to $64\text{ KB}$ to prevent buffer exhaustion.

---

## 5. DevSecOps & Automated Security Scanning (CO3)

In accordance with course outcome **CO3 (Security Operations)**, automated security checks are embedded into the continuous delivery pipeline:

```
[Git Push / Pull Request]
          │
          ├──► 1. Dependency Vulnerability Audit (pip-audit & npm audit)
          │
          ├──► 2. Container Security Scan (Trivy Scan on Dockerfile & Images)
          │
          └──► 3. Static Code Analysis (SonarQube / Ruff / Bandit)
```

### 5.1 Container Vulnerability Scanning with Trivy
Configured in `.github/workflows/security-scan.yml`:
```yaml
- name: Run Trivy Vulnerability Scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'compilerx-sandbox:latest'
    format: 'table'
    exit-code: '1'
    ignore-unfixed: true
    vuln-type: 'os,library'
    severity: 'CRITICAL,HIGH'
```
- Builds fail if any unpatched `HIGH` or `CRITICAL` vulnerabilities exist in the base sandbox image.

### 5.2 Python Static Application Security Testing (SAST)
- **Bandit & Ruff:** Scans backend Python code for common security pitfalls (use of `assert`, weak cryptographic hashing, unsafe subprocess invocations).

---

## 6. Security Event Auditing & Incident Logging

Security-relevant events are tagged and logged in structured JSON for auditing:
- `UNWHITELISTED_FLAG_REJECTED`: Records client IP, unapproved flag, and timestamp.
- `EXECUTION_TIMEOUT_TRIGGERED`: Records file ID, binary name, and elapsed duration before `SIGKILL`.
- `OOM_TERMINATION_DETECTED`: Records process ID and memory ceiling breach.
- `FORK_BOMB_MITIGATED`: Records PID limit exhaustion event.

---

*This document defines the official security architecture and SecOps controls for CompilerX.*

