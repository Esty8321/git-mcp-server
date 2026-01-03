from __future__ import annotations

from pydantic import BaseModel, Field, EmailStr


class SendEmailIn(BaseModel):
    to: EmailStr = Field(
        ...,
        description="Valid email address."
    )
    subject: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Email subject."
    )
    body: str = Field(
        ...,
        description="Plain text email content."
    )

