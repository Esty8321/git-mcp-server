from __future__ import annotations

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ErrorInfo(BaseModel):
    code: str = Field(
        ...,
        description="A short, stable identifier for the error type (logic / validation / dependency)."
    )
    message: str = Field(
        ...,
        description="Human-readable message for the user or agent."
    )
    hint: Optional[str] = Field(
        None,
        description="Guidance for fixing the issue (e.g., gh auth login)."
    )
    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Technical or diagnostic details."
    )


class ToolResult(BaseModel):
    ok: bool = Field(
        ...,
        description="Indicates whether the operation succeeded."
    )
    data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Result or output of the operation."
    )
    error: Optional[ErrorInfo] = Field(
        None,
        description="Present only if ok is false."
    )
