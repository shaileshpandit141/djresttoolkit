from typing import Any, TypedDict


class EmailTemplateDict(TypedDict):
    """Template for rendering email content."""

    text: str  # plain text version
    html: str  # HTML version    html: str  # HTML version


class EmailContentDict(TypedDict):
    """
    Represents a fully configured email message.

    This model combines the essential parts of an email, including:
    - subject line
    - from_email the sender email
    - a rendering context for template variables
    - associated text and/or HTML templates

    """

    subject: str
    from_email: str | None
    context: dict[str, Any] | None
    template: EmailTemplateDict
