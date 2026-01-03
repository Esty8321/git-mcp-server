from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


@dataclass(frozen=True)
class CmdResult:
    """
    Result of a blocking system command execution.
    This is an INTERNAL model (not exposed directly to MCP agents).
    """
    ok: bool
    cmd: str
    cwd: Optional[str]
    code: Optional[int]
    elapsed_sec: float
    stdout: str
    stderr: str
    stdout_truncated: bool
    stderr_truncated: bool
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to plain dict for embedding inside ToolResult.details.
        """
        return asdict(self)
