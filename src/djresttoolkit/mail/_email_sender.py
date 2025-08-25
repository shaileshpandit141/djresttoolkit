import logging
from smtplib import SMTPException
from typing import cast

from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from ._models import EmailContent
from ._types import EmailContentDict

# Set up logger
logger = logging.getLogger(__name__)


class EmailSender:
    """
    Sends templated emails using Django's EmailMultiAlternatives.

    Supports:
    - Plain text and HTML templates
    - Template rendering with context
    - Optional silent failure handling via `exceptions`

    Parameters
    ----------
    email_content : EmailContent | EmailContentDict
        The email data, including subject, sender, templates, and context.

    Methods
    -------
    send(to: list[str], exceptions: bool = False) -> bool
        Sends the email to the given recipients.
        - `exceptions=True` riase exceptions on failure and returns False if `exceptions=False`.

    Example
    -------
    >>> from mypackage._models import EmailContent, EmailTemplate
    >>> content = EmailContent(
    ...     subject="Hello",
    ...     from_email="noreply@example.com",
    ...     context={"username": "Alice"},
    ...     template=EmailTemplate(text="emails/welcome.txt", html="emails/welcome.html")
    ... )
    >>> sender = EmailSender(content)
    >>> sender.send(to=["user@example.com"])  # --> True/False

    """

    def __init__(
        self,
        email_content: EmailContent | EmailContentDict,
    ) -> None:
        """Initialize email sender class."""
        self._email_content = email_content

    @property
    def email_content(self) -> EmailContentDict:
        """Convert pydantic mode to python dict."""
        if isinstance(self._email_content, EmailContent):
            return cast(EmailContentDict, self._email_content.model_dump())
        return self._email_content

    def send(
        self,
        to: list[str],
        exceptions: bool = False,
    ) -> bool:
        """Send email to recipients."""
        unique_recipients = list(set(to))
        try:
            logger.info("Starting email sending process.")
            email = EmailMultiAlternatives(
                subject=self.email_content["subject"],
                body=render_to_string(
                    self.email_content["template"]["text"],
                    self.email_content["context"],
                ),
                from_email=self.email_content["from_email"],
                to=unique_recipients,
            )
            email.attach_alternative(
                content=render_to_string(
                    self.email_content["template"]["html"],
                    self.email_content["context"],
                ),
                mimetype="text/html",
            )
            email.send()
            logger.info(f"Email sent successfully to: {', '.join(unique_recipients)}")
            return True
        except (SMTPException, ValidationError) as error:
            logger.error(f"Error during sending email\nErrors: {error}")
            if exceptions:
                raise ValidationError("Error during sending email") from error
            return False
