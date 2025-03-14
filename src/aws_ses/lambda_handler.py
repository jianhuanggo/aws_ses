"""
AWS Lambda handler for sending emails via SES.
"""
import json
import os
from typing import Any, Dict, Optional, Union

from aws_ses.ses_client import SESClient


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for sending emails via SES.

    Expected event format:
    {
        "source": "sender@example.com",
        "to_addresses": ["recipient@example.com"] or "recipient@example.com",
        "subject": "Email Subject",
        "body_text": "Email body in plain text",
        "body_html": "Email body in HTML" (optional),
        "cc_addresses": ["cc@example.com"] or "cc@example.com" (optional),
        "bcc_addresses": ["bcc@example.com"] or "bcc@example.com" (optional),
        "reply_to_addresses": ["reply@example.com"] or "reply@example.com" (optional),
        "profile_name": "aws_profile_name" (optional),
        "region_name": "aws_region" (optional)
    }

    Args:
        event: Lambda event containing email details
        context: Lambda context

    Returns:
        Dict: Response containing status and message ID if successful
    """
    try:
        # Extract parameters from the event
        source = event.get("source")
        to_addresses = event.get("to_addresses")
        subject = event.get("subject")
        body_text = event.get("body_text")
        body_html = event.get("body_html")
        cc_addresses = event.get("cc_addresses")
        bcc_addresses = event.get("bcc_addresses")
        reply_to_addresses = event.get("reply_to_addresses")
        
        # Get profile and region from event or environment variables
        profile_name = event.get("profile_name") or os.environ.get("AWS_PROFILE")
        region_name = event.get("region_name") or os.environ.get("AWS_REGION")

        # Validate required parameters
        if not all([source, to_addresses, subject, body_text]):
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "Missing required parameters. Required: source, to_addresses, subject, body_text"
                })
            }

        # Initialize SES client
        ses_client = SESClient(profile_name=profile_name, region_name=region_name)
        
        # Send the email
        response = ses_client.send_email(
            source=source,
            to_addresses=to_addresses,
            subject=subject,
            body_text=body_text,
            body_html=body_html,
            cc_addresses=cc_addresses,
            bcc_addresses=bcc_addresses,
            reply_to_addresses=reply_to_addresses,
        )
        
        # Return success response
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Email sent successfully",
                "messageId": response["MessageId"]
            })
        }
        
    except Exception as e:
        # Return error response
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": f"Error sending email: {str(e)}"
            })
        }
