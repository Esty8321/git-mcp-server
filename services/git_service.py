from __future__ import annotations

import os
from typing import Optional

from models.result import ToolResult, ErrorInfo
from utils.paths import abspath, is_dir_empty
from utils.process import run_cmd_blocking
from utils.validate import validate_repo_dir
from utils import errors


class GitService:
    def clone(self, repo_url: str, dest_dir: str, timeout_sec: int = 60) -> ToolResult:
        dest_dir_abs = abspath(dest_dir)
        if os.path.exists(dest_dir_abs) and not os.path.isdir(dest_dir_abs):
            return ToolResult(
                ok=False,
                error=ErrorInfo(
                    code=errors.DEST_NOT_DIR,
                    message="Destination exists but is not a directory.",
                    details={"dest_dir": dest_dir_abs},
                ),
            )

        if os.path.isdir(dest_dir_abs) and not is_dir_empty(dest_dir_abs):
            return ToolResult(
                ok=False,
                error=ErrorInfo(
                    code=errors.DEST_NOT_EMPTY,
                    message="Destination directory exists and is not empty.",
                    details={"dest_dir": dest_dir_abs},
                ),
            )

        if not os.path.exists(dest_dir_abs):
            parent = os.path.dirname(dest_dir_abs)
            if parent:
                os.makedirs(parent, exist_ok=True)

        cmd = [
            "git",
            "-c", "core.longpaths=true",
            "-c", "credential.interactive=never",
            "clone",
            repo_url,
            dest_dir_abs,
        ]
        res = run_cmd_blocking(cmd, cwd=None, timeout_sec=timeout_sec, max_chars=4000)

        if not res.ok:
            code = errors.CMD_TIMEOUT if res.error == "timeout" else errors.CMD_FAILED
            return ToolResult(
                ok=False,
                error=ErrorInfo(
                    code=code,
                    message="git clone failed.",
                    hint="Check repo URL / credentials. This tool is non-interactive (no prompts).",
                    details={"repo_url": repo_url, "dest_dir": dest_dir_abs, **res.to_dict()},
                ),
            )

        return ToolResult(
            ok=True,
            data={
                "repo_url": repo_url,
                "dest_dir": dest_dir_abs,
                "git_dir_exists": os.path.isdir(os.path.join(dest_dir_abs, ".git")),
                "elapsed_sec": res.elapsed_sec,
                "stdout": res.stdout,
                "stderr": res.stderr,
            },
        )

    def status(self, repo_dir: str, timeout_sec: int = 30) -> ToolResult:
        ok, repo_dir_abs = validate_repo_dir(repo_dir)
        if not ok:
            return ToolResult(
                ok=False,
                error=ErrorInfo(
                    code=errors.NOT_A_GIT_REPO,
                    message="Not a git repository or repo_dir is not a directory.",
                    details={"repo_dir": repo_dir_abs},
                ),
            )

        res = run_cmd_blocking(["git", "status", "--porcelain"], cwd=repo_dir_abs, timeout_sec=timeout_sec, max_chars=4000)

        if not res.ok:
            return ToolResult(
                ok=False,
                error=ErrorInfo(code=errors.CMD_FAILED, message="git status failed.", details=res),
            )

        return ToolResult(ok=True, data={"repo_dir": repo_dir_abs, "status_porcelain": res.stdout})

    def diff(
        self,
        repo_dir: str,
        staged: bool,
        name_only: bool = False,
        stat: bool = False,
        max_chars: int = 20000,
        timeout_sec: int = 60,
    ) -> ToolResult:
        ok, repo_dir_abs = validate_repo_dir(repo_dir)
        if not ok:
            return ToolResult(
                ok=False,
                error=ErrorInfo(code=errors.NOT_A_GIT_REPO, message="Not a git repository.", details={"repo_dir": repo_dir_abs}),
            )

        args = ["git", "diff"]
        if staged:
            args.append("--staged")
        if name_only:
            args.append("--name-only")
        if stat:
            args.append("--stat")

        res = run_cmd_blocking(args, cwd=repo_dir_abs, timeout_sec=timeout_sec, max_chars=max_chars)
        if not res.ok:
            return ToolResult(ok=False, error=ErrorInfo(code=errors.CMD_FAILED, message="git diff failed.", details=res))

        return ToolResult(
            ok=True,
            data={
                "repo_dir": repo_dir_abs,
                "staged": staged,
                "name_only": name_only,
                "stat": stat,
                "diff": res.stdout,
                "stderr": res.stderr,
                "truncated": bool(res.stdout_truncated),
            },
        )

    def commit(self, repo_dir: str, message: str, timeout_sec: int = 60) -> ToolResult:
        ok, repo_dir_abs = validate_repo_dir(repo_dir)
        if not ok:
            return ToolResult(ok=False, error=ErrorInfo(code=errors.NOT_A_GIT_REPO, message="Not a git repository.", details={"repo_dir": repo_dir_abs}))

        status_res = run_cmd_blocking(["git", "status", "--porcelain"], cwd=repo_dir_abs, timeout_sec=timeout_sec, max_chars=4000)
        if not status_res.ok:
            return ToolResult(ok=False, error=ErrorInfo(code=errors.CMD_FAILED, message="git status failed.", details=status_res))

        if (status_res.stdout or "").strip() == "":
            return ToolResult(ok=True, data={"repo_dir": repo_dir_abs, "message": "Nothing to commit (working tree clean)."})

        add_res = run_cmd_blocking(["git", "add", "-A"], cwd=repo_dir_abs, timeout_sec=timeout_sec, max_chars=4000)
        if not add_res.ok:
            return ToolResult(ok=False, error=ErrorInfo(code=errors.CMD_FAILED, message="git add failed.", details=add_res))

        commit_res = run_cmd_blocking(
            ["git", "commit", "-m", message, "--no-gpg-sign"],
            cwd=repo_dir_abs,
            timeout_sec=timeout_sec,
            max_chars=4000,
        )
        if not commit_res.ok:
            return ToolResult(ok=False, error=ErrorInfo(code=errors.CMD_FAILED, message="git commit failed.", details=commit_res))

        return ToolResult(ok=True, data={"repo_dir": repo_dir_abs, "message": "Commit created successfully.", "stdout": commit_res.stdout, "stderr": commit_res.stderr})

    def current_branch(self, repo_dir_abs: str, timeout_sec: int = 20) -> Optional[str]:
        res = run_cmd_blocking(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_dir_abs, timeout_sec=timeout_sec, max_chars=2000)
        if not res.ok:
            return None
        return (res.stdout or "").strip()

    def has_upstream(self, repo_dir_abs: str, timeout_sec: int = 10) -> bool:
        res = run_cmd_blocking(
            ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
            cwd=repo_dir_abs,
            timeout_sec=timeout_sec,
            max_chars=2000,
        )
        return bool(res.ok)

    def push(
        self,
        repo_dir: str,
        remote: str = "origin",
        branch: str = "",
        set_upstream: bool = False,
        timeout_sec: int = 60,
    ) -> ToolResult:
        ok, repo_dir_abs = validate_repo_dir(repo_dir)
        if not ok:
            return ToolResult(ok=False, error=ErrorInfo(code=errors.NOT_A_GIT_REPO, message="Not a git repository.", details={"repo_dir": repo_dir_abs}))

        if not branch:
            branch = self.current_branch(repo_dir_abs, 20) or ""
            if not branch:
                return ToolResult(ok=False, error=ErrorInfo(code=errors.BRANCH_DETECT_FAILED, message="Failed to detect current branch.", details={"repo_dir": repo_dir_abs}))

        args = ["git", "push"]
        if set_upstream:
            args.append("-u")
        args += [remote, branch]

        res = run_cmd_blocking(args, cwd=repo_dir_abs, timeout_sec=timeout_sec, max_chars=4000)
        if not res.ok:
            return ToolResult(
                ok=False,
                error=ErrorInfo(
                    code=errors.CMD_FAILED,
                    message="git push failed.",
                    hint="This tool is non-interactive. For HTTPS, set credentials ahead of time or use SSH keys.",
                    details=res.to_dict(),
                ),
            )

        return ToolResult(
            ok=True,
            data={
                "repo_dir": repo_dir_abs, 
                "remote": remote, 
                "branch": branch, **res.to_dict()
                }
            )
