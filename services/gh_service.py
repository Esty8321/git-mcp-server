from __future__ import annotations

from models.result import ToolResult, ErrorInfo
from utils.process import run_cmd_blocking
from utils import errors

class GhService:
    def create_pr(
        self,
        repo_dir_abs: str,
        title: str,
        body: str,
        base: str,
        head: str,
        draft: bool,
        timeout_sec: int = 90,
    ) -> ToolResult:
        cmd = [
            "gh", "pr", "create",
            "--title", title,
            "--base", base,
            "--head", head,
            "--body", body or "",
        ]
        if draft:
            cmd.append("--draft")

        res = run_cmd_blocking(cmd, cwd=repo_dir_abs, timeout_sec=timeout_sec, max_chars=4000)
        if not res.ok:
            return ToolResult(
                ok=False,
                error=ErrorInfo(
                    code=errors.CMD_FAILED,
                    message="Failed to create PR using GitHub CLI.",
                    hint="Make sure GitHub CLI is installed and run: gh auth login (in a normal terminal).",
                    details=res.to_dict(),
                ),
            )

        return ToolResult(
            ok=True,
            data=res.to_dict()
        )
