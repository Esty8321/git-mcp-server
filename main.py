from __future__ import annotations

import asyncio
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

from services.git_service import GitService
from services.gh_service import GhService
from services.email_service import EmailService
from models.git_models import GitCloneIn, GitDiffIn, GitCommitIn, GitPushIn, GitStatusIn
from models.gh_models import OpenPrToBaseIn
from models.email_models import SendEmailIn
from settings import build_settings, get_default_env_path

env_path = get_default_env_path()
load_dotenv(dotenv_path=env_path, override=False)

settings = build_settings()

mcp = FastMCP("git-mcp-server")

git = GitService()
gh = GhService()
email = EmailService(settings=settings)



@mcp.tool(description="""
Return repository status using 'git status --porcelain'.

Use when:
- You need to know if the working tree is clean or has changes.
- Before committing to decide whether a commit is needed.
- To check what files changed (porcelain output is machine-friendly).

Inputs:
- repo_dir: path to local git repository
- timeout_sec: command timeout

Returns (ToolResult):
- ok=true: data.status_porcelain contains the porcelain output (empty string means clean)
- ok=false: error.code/message and details
""")
async def git_status(repo_dir: str, timeout_sec: int = 30) -> dict:
    _ = GitStatusIn(repo_dir=repo_dir, timeout_sec=timeout_sec)  # validation
    res = await asyncio.to_thread(git.status, repo_dir, timeout_sec)
    return res.model_dump()



@mcp.tool(description="""
Clone a remote Git repository into a local directory (non-interactive).

Use when:
- You need to download a repository to a specific local path for further git operations.

Inputs:
- repo_url: repository URL (https/ssh)
- dest_dir: local directory path (must be empty or not exist)
- timeout_sec: command timeout (seconds)

Returns (ToolResult):
- ok=true: data contains dest_dir, elapsed_sec, stdout/stderr (may be truncated)
- ok=false: error.code + error.message + optional hint/details
""")
async def git_clone(repo_url: str, dest_dir: str, timeout_sec: int = 60) -> dict:
    _ = GitCloneIn(repo_url=repo_url, dest_dir=dest_dir, timeout_sec=timeout_sec)  # validation
    res = await asyncio.to_thread(git.clone, repo_url, dest_dir, timeout_sec)
    return res.model_dump()


@mcp.tool(description="""
Show git diff for a repository.

Use when:
- You need to inspect changes before committing or generating a commit message.
- For AI: use diff output to craft a meaningful commit message.

Options:
- staged: include staged changes (git diff --staged)
- name_only: list changed file names only
- stat: show diff stats
- max_chars: truncate output to avoid huge responses

Returns ToolResult with data.diff and data.truncated flag.
""")
async def git_diff(
    repo_dir: str,
    staged: bool = False,
    name_only: bool = False,
    stat: bool = False,
    max_chars: int = 20000,
    timeout_sec: int = 60,
) -> dict:
    _ = GitDiffIn(repo_dir=repo_dir, staged=staged, name_only=name_only, stat=stat, max_chars=max_chars, timeout_sec=timeout_sec)
    res = await asyncio.to_thread(git.diff, repo_dir, staged, name_only, stat, max_chars, timeout_sec)
    return res.model_dump()


@mcp.tool(description="""
Stage all changes and create a git commit (non-interactive).

Use when:
- You want to commit all local changes with a message.

Behavior:
- If working tree is clean, returns ok=true with message 'Nothing to commit'.

Returns ToolResult:
- ok=true: data.message + stdout/stderr
- ok=false: error.code + error.message + details
""")
async def git_commit(repo_dir: str, message: str, timeout_sec: int = 60) -> dict:
    _ = GitCommitIn(repo_dir=repo_dir, message=message, timeout_sec=timeout_sec)
    res = await asyncio.to_thread(git.commit, repo_dir, message, timeout_sec)
    return res.model_dump()


@mcp.tool(description="""
Push current branch (or specified branch) to a remote.

Use when:
- After committing, you need to push changes to GitHub/Git remote.

Notes:
- Non-interactive: will NOT open login prompts.
- Use set_upstream=true for first push of a new branch (git push -u).

Returns ToolResult.
""")
async def git_push(
    repo_dir: str,
    remote: str = "origin",
    branch: str = "",
    set_upstream: bool = False,
    timeout_sec: int = 60,
) -> dict:
    _ = GitPushIn(repo_dir=repo_dir, remote=remote, branch=branch, set_upstream=set_upstream, timeout_sec=timeout_sec)
    res = await asyncio.to_thread(git.push, repo_dir, remote, branch, set_upstream, timeout_sec)
    return res.model_dump()


@mcp.tool(description="""
Create a Pull Request from the current branch to a base branch using GitHub CLI (gh).

Use when:
- You already committed changes and want to open a PR.
- If branch has no upstream, the tool will push with upstream first.

Constraints:
- Refuses to open PR if current branch is main/master.

Returns ToolResult:
- ok=true: data contains gh command output
- ok=false: error includes a hint (e.g., run 'gh auth login')
""")
async def open_pr_to_base(
    repo_dir: str,
    title: str,
    body: str = "",
    remote: str = "origin",
    base: str = "master",
    draft: bool = False,
    timeout_sec: int = 90,
) -> dict:
    _ = OpenPrToBaseIn(repo_dir=repo_dir, title=title, body=body, remote=remote, base=base, draft=draft, timeout_sec=timeout_sec)

    # validate repo & detect branch
    res_validate = await asyncio.to_thread(lambda: __validate_repo_for_pr(repo_dir))
    if not res_validate["ok"]:
        return res_validate

    repo_dir_abs = res_validate["repo_dir_abs"]
    branch = await asyncio.to_thread(git.current_branch, repo_dir_abs, 20)
    if not branch:
        return {"ok": False, "data": {}, "error": {"code": "branch_detect_failed", "message": "Failed to detect current branch.", "details": {"repo_dir": repo_dir_abs}}}

    if branch in ("main", "master"):
        return {"ok": False, "data": {}, "error": {"code": "on_base_branch", "message": f"You are on '{branch}'. Switch to a feature branch to open a PR.", "details": {"current_branch": branch}}}

    # ensure upstream
    has_up = await asyncio.to_thread(git.has_upstream, repo_dir_abs, 10)
    if not has_up:
        push_res = await asyncio.to_thread(git.push, repo_dir_abs, remote, branch, True, timeout_sec)
        if not push_res.ok:
            return push_res.model_dump()

    pr_res = await asyncio.to_thread(gh.create_pr, repo_dir_abs, title, body, base, branch, draft, timeout_sec)
    return pr_res.model_dump()


def __validate_repo_for_pr(repo_dir: str) -> dict:
    from utils.validate import validate_repo_dir
    from models.result import ToolResult, ErrorInfo
    from utils import errors

    ok, repo_dir_abs = validate_repo_dir(repo_dir)
    if not ok:
        return ToolResult(ok=False, error=ErrorInfo(code=errors.NOT_A_GIT_REPO, message="Not a git repository.", details={"repo_dir": repo_dir_abs})).model_dump()
    return {"ok": True, "repo_dir_abs": repo_dir_abs}


@mcp.tool(description="""
Send an email notification (SMTP).

Use when:
- After opening a PR, you want to notify a reviewer by email.

Inputs:
- to: recipient email
- subject: email subject
- body: plain text content

Returns ToolResult:
- ok=true: confirmation
- ok=false: missing SMTP config or send failure
""")
def send_email(to: str, subject: str, body: str) -> dict:
    _ = SendEmailIn(to=to, subject=subject, body=body)
    res = email.send(to, subject, body)
    return res.model_dump()


if __name__ == "__main__":
    mcp.run()
