from typing import Any

from pydantic import BaseModel, field_validator


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


class EmailContent(BaseModel):
    """
    Represents the content of an email ready for rendering.

    This model combines the key parts of an email, including:
    - subject line
    - sender email (from_email)
    - rendering context for template variables
    - associated text and/or HTML templates

    Attributes
    ----------
    subject : str
        The subject line of the email.
    from_email : EmailStr | None
        Sender's email address.
    context : dict[str, Any] | None
        Optional context data used to render templates (e.g., {"username": "Alice"}).
    template : EmailTemplate
        Templates for the email body (.txt and/or .html).

    """

    subject: str
    from_email: str | None
    context: dict[str, Any] | None = None
    template: EmailTemplate
