from __future__ import annotations

from typing import Optional, Dict, List
import os, subprocess, time

from models.cmd_result import CmdResult

DEFAULT_ENV_OVERRIDES = {
    "GIT_TERMINAL_PROMPT": "0",
    "GCM_INTERACTIVE": "Never",
    "GIT_EDITOR": "true",
}

def _to_text(x) -> str:
    if x is None:
        return ""
    if isinstance(x, (bytes, bytearray)):
        return x.decode("utf-8", errors="replace")
    return str(x)


def _truncate(s: str, max_chars: int) -> tuple[str, bool]:
    s = s or ""
    if len(s) <= max_chars:
        return s, False
    return s[:max_chars] + "\n... [truncated]", True


def run_cmd_blocking(
    cmd: List[str],
    cwd: Optional[str],
    timeout_sec: int = 60,
    env_overrides: Optional[Dict[str, str]] = None,
    max_chars: int = 4000,
) -> CmdResult:
    cmd = [_to_text(c) for c in cmd]

    env = os.environ.copy()
    env.update(DEFAULT_ENV_OVERRIDES)
    if env_overrides:
        env.update(env_overrides)

    t0 = time.time()
    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        shell=False,
    )

    try:
        out_b, err_b = proc.communicate(timeout=timeout_sec)
        code = proc.returncode
        elapsed = round(time.time() - t0, 3)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate(timeout=1)
        elapsed = round(time.time() - t0, 3)
        return CmdResult(
            ok=False,
            error="timeout",
            cmd=" ".join(cmd),
            cwd=cwd,
            code=None,
            elapsed_sec=elapsed,
            stdout="",
            stderr=f"Command timed out after {timeout_sec}s",
            stdout_truncated=False,
            stderr_truncated=False,
        )

    out = _to_text(out_b).strip()
    err = _to_text(err_b).strip()
    out, out_tr = _truncate(out, max_chars)
    err, err_tr = _truncate(err, max_chars)

    return CmdResult(
        ok=(code == 0),
        cmd=" ".join(cmd),
        cwd=cwd,
        code=code,
        elapsed_sec=elapsed,
        stdout=out,
        stderr=err,
        stdout_truncated=out_tr,
        stderr_truncated=err_tr,
    )
