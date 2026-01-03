from __future__ import annotations

import os


def abspath(p: str) -> str:
    if p is None:
        return ""
    return (
        os.path.abspath(os.path.expanduser(str(p)))
        .strip()
        .strip('"')
        .strip("'")
        .rstrip("\\/")
    )


def is_dir_empty(path: str) -> bool:
    if not os.path.exists(path):
        return True
    if not os.path.isdir(path):
        return False
    return len(os.listdir(path)) == 0


def is_git_repo(repo_dir_abs: str) -> bool:
    return os.path.isdir(os.path.join(repo_dir_abs, ".git"))
