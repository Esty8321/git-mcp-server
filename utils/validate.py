from __future__ import annotations

import os

from utils.paths import abspath, is_git_repo

def validate_repo_dir(repo_dir: str) -> tuple[bool, str]:
    repo_dir_abs = abspath(repo_dir)
    if not os.path.isdir(repo_dir_abs):
        return False, repo_dir_abs
    if not is_git_repo(repo_dir_abs):
        return False, repo_dir_abs
    return True, repo_dir_abs