from typing import Any, TypedDict

from pydantic import EmailStr


class EmailTemplateDict(TypedDict):
    """Template for rendering email content."""

    text: str  # plain text version
    html: str  # HTML version    html: str  # HTML version


class EmailDict(TypedDict):
    """
    Represents a fully configured email message.

    This model combines the essential parts of an email, including:
    - subject line
    - from_email the sender email
    - a rendering context for template variables
    - associated text and/or HTML templates

    """

    subject: str
    from_email: EmailStr | None
    context: dict[str, Any] | None
    template: EmailTemplateDict
