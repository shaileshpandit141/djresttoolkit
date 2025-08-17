from typing import Any

from pydantic import BaseModel, EmailStr, field_validator


class EmailTemplate(BaseModel):
    """Template for rendering email content."""

    text: str  # plain text version
    html: str  # HTML version

    @field_validator("text")
    @classmethod
    def validate_text_template(cls, v: str) -> str:
        if not v.endswith(".txt"):
            raise ValueError("Text template must end with .txt")
        return v

    @field_validator("html")
    @classmethod
    def validate_html_template(cls, v: str) -> str:
        if not v.endswith(".html"):
            raise ValueError("HTML template must end with .html")
        return v


class Email(BaseModel):
    """
    Represents a fully configured email message.

    This model combines the essential parts of an email, including:
    - subject line
    - from_email the sender email
    - a rendering context for template variables
    - associated text and/or HTML templates

    Attributes
    ----------
    subject : str
        The subject line of the email.
    from_email : EmailStr | None
        The from_email of the sender email
    context : dict[str, Any] | None, default=None
        Optional context data used to render template variables
        inside the email body (e.g., {"username": "Alice"}).
    template : EmailTemplate
        The templates used for the email body. Can include plain text
        (.txt) and/or HTML (.html) versions.
    """

    subject: str
    from_email: EmailStr | None
    context: dict[str, Any] | None = None
    template: EmailTemplate
