"""
Email service using Mailgun for Astra Staging website.
Sends confirmation emails to customers and notifications to sales team.
"""
import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mailgun Configuration
MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY')
MAILGUN_DOMAIN = os.getenv('MAILGUN_DOMAIN', 'astrastaging.com')
MAILGUN_API_BASE = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"

# Email addresses
ADMIN_EMAIL = "sales@astrastaging.com"
SENDER_EMAIL = "Astra Staging <sales@astrastaging.com>"


class EmailService:
    """Mailgun Email Service for inquiry form submissions"""

    def __init__(self):
        self.api_key = MAILGUN_API_KEY
        self.domain = MAILGUN_DOMAIN
        self.api_base = MAILGUN_API_BASE
        self.sender = SENDER_EMAIL

    def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None, reply_to: str = None) -> dict:
        """
        Send an email using Mailgun API

        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML body of the email
            text_content: Plain text body (optional)
            reply_to: Reply-to email address (optional)

        Returns:
            dict with success status and message_id or error
        """
        if not self.api_key:
            logger.error("MAILGUN_API_KEY is not set")
            return {'success': False, 'error': 'Mailgun API key not configured'}

        if not text_content:
            text_content = "Please view this email in an HTML-compatible email client."

        data = {
            "from": self.sender,
            "to": [to_email],
            "subject": subject,
            "html": html_content,
            "text": text_content,
            "o:tracking": "no",
            "o:tracking-clicks": "no",
            "o:tracking-opens": "no"
        }

        if reply_to:
            data["h:Reply-To"] = reply_to

        try:
            response = requests.post(
                self.api_base,
                auth=("api", self.api_key),
                data=data
            )

            response.raise_for_status()
            result = response.json()

            logger.info(f"Email sent to {to_email}: {result.get('id', 'unknown')}")
            return {'success': True, 'message_id': result.get('id')}

        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                error_msg = f"{error_msg} - {e.response.text}"
            logger.error(f"Failed to send email to {to_email}: {error_msg}")
            return {'success': False, 'error': error_msg}
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return {'success': False, 'error': str(e)}

    def send_customer_confirmation(self, customer_data: dict) -> dict:
        """
        Send confirmation email to customer who submitted inquiry

        Args:
            customer_data: dict with name, email, phone, subject, message
        """
        name = customer_data.get('name', 'Valued Customer')
        email = customer_data.get('email')

        subject = "Thank You for Your Inquiry - Astra Staging"

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: #000; font-size: 24px; margin-bottom: 5px;">ASTRA STAGING</h1>
        <p style="color: #666; font-size: 14px; margin: 0;">Professional Home Staging Services</p>
    </div>

    <div style="background: #f9f9f9; border-radius: 8px; padding: 25px; margin-bottom: 25px;">
        <h2 style="color: #000; font-size: 20px; margin-top: 0;">Thank You for Contacting Us!</h2>
        <p>Dear {name},</p>
        <p>We have received your inquiry and appreciate your interest in Astra Staging's professional home staging services.</p>
        <p>One of our staging consultants will review your message and get back to you within <strong>24 hours</strong>.</p>
    </div>

    <div style="background: #fff; border: 1px solid #eee; border-radius: 8px; padding: 20px; margin-bottom: 25px;">
        <h3 style="color: #000; font-size: 16px; margin-top: 0; border-bottom: 1px solid #eee; padding-bottom: 10px;">Your Inquiry Details</h3>
        <p><strong>Name:</strong> {customer_data.get('name', 'N/A')}</p>
        <p><strong>Email:</strong> {customer_data.get('email', 'N/A')}</p>
        <p><strong>Phone:</strong> {customer_data.get('phone', 'Not provided')}</p>
        <p><strong>Subject:</strong> {customer_data.get('subject', 'General Inquiry')}</p>
        <p><strong>Message:</strong></p>
        <p style="background: #f5f5f5; padding: 15px; border-radius: 5px;">{customer_data.get('message', 'N/A')}</p>
    </div>

    <div style="text-align: center; margin-bottom: 25px;">
        <p style="margin-bottom: 15px;">In the meantime, feel free to reach us directly:</p>
        <p>
            <a href="tel:+18887444078" style="color: #000; text-decoration: none; font-weight: bold;">1-888-744-4078</a>
            &nbsp;&nbsp;|&nbsp;&nbsp;
            <a href="mailto:sales@astrastaging.com" style="color: #000; text-decoration: none; font-weight: bold;">sales@astrastaging.com</a>
        </p>
    </div>

    <div style="border-top: 1px solid #eee; padding-top: 20px; text-align: center; color: #666; font-size: 12px;">
        <p>Astra Staging | 3600A Laird Rd, Unit 12, Mississauga, ON L5L 0A3</p>
        <p>
            <a href="https://www.astrastaging.com" style="color: #666;">www.astrastaging.com</a>
        </p>
    </div>
</body>
</html>
"""

        text_content = f"""
Thank You for Your Inquiry - Astra Staging

Dear {name},

We have received your inquiry and appreciate your interest in Astra Staging's professional home staging services.

One of our staging consultants will review your message and get back to you within 24 hours.

Your Inquiry Details:
- Name: {customer_data.get('name', 'N/A')}
- Email: {customer_data.get('email', 'N/A')}
- Phone: {customer_data.get('phone', 'Not provided')}
- Subject: {customer_data.get('subject', 'General Inquiry')}
- Message: {customer_data.get('message', 'N/A')}

In the meantime, feel free to reach us directly:
- Phone: 1-888-744-4078
- Email: sales@astrastaging.com

Best regards,
Astra Staging Team

3600A Laird Rd, Unit 12, Mississauga, ON L5L 0A3
www.astrastaging.com
"""

        return self.send_email(email, subject, html_content, text_content, reply_to=ADMIN_EMAIL)

    def send_admin_notification(self, customer_data: dict, admin_email: str = None) -> dict:
        """
        Send notification email to admin/sales team about new inquiry
        Uses sandbox domain to handle sending to self (sales@astrastaging.com)

        Args:
            customer_data: dict with name, email, phone, subject, message
            admin_email: Override admin email for testing (default: ADMIN_EMAIL)
        """
        to_email = admin_email or ADMIN_EMAIL
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        customer_email = customer_data.get('email', '')

        form_subject = customer_data.get('subject', 'General Inquiry')
        subject = f"[{form_subject}] {customer_data.get('name', 'Unknown')} - Astra Staging"

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background: #000; color: #fff; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
        <h1 style="margin: 0; font-size: 20px;">New Website Inquiry</h1>
        <p style="margin: 5px 0 0; font-size: 14px; opacity: 0.8;">{timestamp}</p>
    </div>

    <div style="background: #f9f9f9; padding: 25px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 8px 8px;">
        <h2 style="color: #000; font-size: 18px; margin-top: 0; border-bottom: 2px solid #000; padding-bottom: 10px;">Contact Information</h2>

        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 10px 0; border-bottom: 1px solid #eee; font-weight: bold; width: 100px;">Name:</td>
                <td style="padding: 10px 0; border-bottom: 1px solid #eee;">{customer_data.get('name', 'N/A')}</td>
            </tr>
            <tr>
                <td style="padding: 10px 0; border-bottom: 1px solid #eee; font-weight: bold;">Email:</td>
                <td style="padding: 10px 0; border-bottom: 1px solid #eee;">
                    <a href="mailto:{customer_email}" style="color: #0066cc;">{customer_email or 'N/A'}</a>
                </td>
            </tr>
            <tr>
                <td style="padding: 10px 0; border-bottom: 1px solid #eee; font-weight: bold;">Phone:</td>
                <td style="padding: 10px 0; border-bottom: 1px solid #eee;">
                    <a href="tel:{customer_data.get('phone', '')}" style="color: #0066cc;">{customer_data.get('phone', 'Not provided')}</a>
                </td>
            </tr>
            <tr>
                <td style="padding: 10px 0; border-bottom: 1px solid #eee; font-weight: bold;">Subject:</td>
                <td style="padding: 10px 0; border-bottom: 1px solid #eee;">{customer_data.get('subject', 'General Inquiry')}</td>
            </tr>
        </table>

        <h3 style="color: #000; font-size: 16px; margin-top: 25px;">Message:</h3>
        <div style="background: #fff; border: 1px solid #ddd; border-radius: 5px; padding: 15px;">
            <p style="margin: 0; white-space: pre-wrap;">{customer_data.get('message', 'No message provided')}</p>
        </div>

        <div style="margin-top: 25px; padding: 15px; background: #e8f4e8; border-radius: 5px; text-align: center;">
            <p style="margin: 0; font-size: 14px;">
                <strong>Quick Actions:</strong><br>
                <a href="mailto:{customer_email}" style="color: #0066cc; margin-right: 15px;">Reply by Email</a>
                <a href="tel:{customer_data.get('phone', '')}" style="color: #0066cc;">Call Customer</a>
            </p>
        </div>
    </div>

    <div style="text-align: center; margin-top: 20px; color: #666; font-size: 12px;">
        <p>This is an automated notification from the Astra Staging website.</p>
    </div>
</body>
</html>
"""

        text_content = f"""
NEW WEBSITE INQUIRY - Astra Staging
====================================
Received: {timestamp}

CONTACT INFORMATION
-------------------
Name: {customer_data.get('name', 'N/A')}
Email: {customer_data.get('email', 'N/A')}
Phone: {customer_data.get('phone', 'Not provided')}
Subject: {customer_data.get('subject', 'General Inquiry')}

MESSAGE
-------
{customer_data.get('message', 'No message provided')}

---
This is an automated notification from the Astra Staging website.
"""

        # Use customer email as reply-to so admin can reply directly to customer
        return self.send_email(to_email, subject, html_content, text_content, reply_to=customer_email)


def send_inquiry_emails(customer_data: dict, admin_email: str = None) -> dict:
    """
    Convenience function to send both customer confirmation and admin notification

    Args:
        customer_data: dict with name, email, phone, subject, message
        admin_email: Override admin email for testing

    Returns:
        dict with customer_result and admin_result
    """
    email_service = EmailService()

    # Send confirmation to customer
    customer_result = email_service.send_customer_confirmation(customer_data)

    # Send notification to admin
    admin_result = email_service.send_admin_notification(customer_data, admin_email)

    return {
        'customer_result': customer_result,
        'admin_result': admin_result,
        'success': customer_result['success'] and admin_result['success']
    }


# Test function
if __name__ == "__main__":
    # Test data
    test_data = {
        'name': 'Test Customer',
        'email': 'fskenneth@gmail.com',
        'phone': '416-555-1234',
        'subject': 'Test Inquiry',
        'message': 'This is a test message from the contact form.'
    }

    # Test sending
    print("Testing email service...")
    result = send_inquiry_emails(test_data, admin_email='sales@astrastaging.com')
    print(f"Result: {result}")
