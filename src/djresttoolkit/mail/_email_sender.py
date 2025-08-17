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
    Handles the sending of emails using Django's EmailMultiAlternatives with support for
    plain text and HTML templates, context rendering, validation.

    This class performs the following tasks:
    1. Validates email participants (sender and recipients).
    2. Validates template file names (.txt for text, .html for HTML).
    3. Renders templates with provided context using Django's template engine.
    4. Sends the email to the specified recipients.

    """

    def __init__(
        self,
        email_content: EmailContent | EmailContentDict,
    ) -> None:
        """Initialize email sender class."""
        self.email_content = email_content
