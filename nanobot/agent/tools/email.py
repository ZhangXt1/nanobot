"""Email sending tool."""

import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import Any

from nanobot.agent.tools.base import Tool
from nanobot.config.loader import load_config


class EmailTool(Tool):
    """Tool for sending emails using SMTP configuration from nanobot config."""
    
    @property
    def name(self) -> str:
        return "send_email"
    
    @property
    def description(self) -> str:
        return "Send an email to one or more recipients. Uses SMTP configuration from nanobot config."
    
    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "to": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Recipient email addresses",
                    "minItems": 1
                },
                "subject": {
                    "type": "string",
                    "description": "Email subject",
                    "minLength": 1
                },
                "body": {
                    "type": "string",
                    "description": "Email body (plain text or HTML)",
                    "minLength": 1
                },
                "is_html": {
                    "type": "boolean",
                    "description": "Whether the body is HTML (default: false)",
                    "default": False
                },
                "cc": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "CC recipient email addresses",
                    "default": []
                },
                "bcc": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "BCC recipient email addresses",
                    "default": []
                },
                "attachments": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Paths to files to attach",
                    "default": []
                }
            },
            "required": ["to", "subject", "body"]
        }
    
    async def execute(
        self,
        to: list[str],
        subject: str,
        body: str,
        is_html: bool = False,
        cc: list[str] = None,
        bcc: list[str] = None,
        attachments: list[str] = None,
    ) -> str:
        """Send an email using SMTP configuration from nanobot config."""
        try:
            # Load configuration
            config = load_config()
            email_config = config.channels.email
            
            if not email_config.enabled:
                return "Error: Email channel is not enabled in configuration"
            
            # Check if we have SMTP configuration
            if not email_config.smtp_host:
                return "Error: SMTP host is not configured"
            
            if not email_config.smtp_username:
                return "Error: SMTP username is not configured"
            
            if not email_config.from_address:
                return "Error: From address is not configured"
            
            # Prepare recipients
            cc = cc or []
            bcc = bcc or []
            attachments = attachments or []
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = email_config.from_address
            msg['To'] = ', '.join(to)
            if cc:
                msg['Cc'] = ', '.join(cc)
            msg['Subject'] = subject
            
            # Add body
            content_type = 'html' if is_html else 'plain'
            msg.attach(MIMEText(body, content_type, 'utf-8'))
            
            # Add attachments
            for attachment_path in attachments:
                try:
                    attachment_path = Path(attachment_path)
                    if not attachment_path.exists():
                        return f"Error: Attachment file not found: {attachment_path}"
                    
                    with open(attachment_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                    
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{attachment_path.name}"'
                    )
                    msg.attach(part)
                except Exception as e:
                    return f"Error attaching file {attachment_path}: {str(e)}"
            
            # All recipients
            all_recipients = to + cc + bcc
            
            # Connect to SMTP server and send
            try:
                if email_config.smtp_use_ssl:
                    server = smtplib.SMTP_SSL(email_config.smtp_host, email_config.smtp_port)
                else:
                    server = smtplib.SMTP(email_config.smtp_host, email_config.smtp_port)
                
                if email_config.smtp_use_tls and not email_config.smtp_use_ssl:
                    server.starttls()
                
                if email_config.smtp_username and email_config.smtp_password:
                    server.login(email_config.smtp_username, email_config.smtp_password)
                
                server.send_message(msg)
                server.quit()
                
                return f"Email sent successfully to {len(all_recipients)} recipient(s)"
                
            except smtplib.SMTPException as e:
                return f"Error sending email via SMTP: {str(e)}"
            except Exception as e:
                return f"Error connecting to SMTP server: {str(e)}"
                
        except Exception as e:
            return f"Error preparing email: {str(e)}"