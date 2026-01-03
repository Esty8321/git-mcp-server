from __future__ import annotations

from pydantic import BaseModel, Field


class OpenPrToBaseIn(BaseModel):
    repo_dir: str = Field(
        ...,
        description="Path to the local repository directory."
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Pull Request title."
    )
    body: str = Field(
        "",
        description="Pull Request description."
    )
    remote: str = Field(
        "origin",
        description="Remote to push from (default: origin)."
    )
    base: str = Field(
        "master",
        description="Base branch for the PR (e.g., main / master / develop)."
    )
    draft: bool = Field(
        False,
        description="If true: create a draft Pull Request."
    )
    timeout_sec: int = Field(
        90,
        ge=1,
        le=600,
        description="Timeout in seconds."
    )
