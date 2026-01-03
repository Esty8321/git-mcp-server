from __future__ import annotations

from pydantic import BaseModel, Field

class GitCloneIn(BaseModel):
    repo_url: str = Field(
        ...,
        description="Repository URL."
    )
    dest_dir: str = Field(
        ...,
        description="Local destination path for cloning."
    )
    timeout_sec: int = Field(
        60,
        ge=1,
        le=600,
        description="Timeout in seconds."
    )


class GitStatusIn(BaseModel):
    repo_dir: str = Field(
        ...,
        description="Path to the local repository directory."
    )
    timeout_sec: int = Field(
        30,
        ge=1,
        le=300,
        description="Timeout in seconds."
    )


class GitDiffIn(BaseModel):
    repo_dir: str = Field(
        ...,
        description="Path to the local repository directory."
    )
    staged: bool = Field(
        False,
        description="If true: diff staged changes (git diff --staged)."
    )
    name_only: bool = Field(
        False,
        description="If true: return only file names (git diff --name-only)."
    )
    stat: bool = Field(
        False,
        description="If true: return statistics (git diff --stat)."
    )
    max_chars: int = Field(
        20000,
        ge=1000,
        le=200000,
        description="Maximum number of characters to return before truncation."
    )
    timeout_sec: int = Field(
        60,
        ge=1,
        le=600,
        description="Timeout in seconds."
    )


class GitCommitIn(BaseModel):
    repo_dir: str = Field(
        ...,
        description="Path to the local repository directory."
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Commit message."
    )
    timeout_sec: int = Field(
        60,
        ge=1,
        le=600,
        description="Timeout in seconds."
    )


class GitPushIn(BaseModel):
    repo_dir: str = Field(
        ...,
        description="Path to the local repository directory."
    )
    remote: str = Field(
        "origin",
        description="Remote name (default: origin)."
    )
    branch: str = Field(
        "",
        description="Branch name. If empty, the current branch will be detected."
    )
    set_upstream: bool = Field(
        False,
        description="If true: use git push -u (create upstream)."
    )
    timeout_sec: int = Field(
        60,
        ge=1,
        le=600,
        description="Timeout in seconds."
    )
