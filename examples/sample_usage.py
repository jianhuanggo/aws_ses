"""
Sample script demonstrating various ways to use the AWS SES client.
"""
import argparse
import json
import sys
from typing import Dict, List, Optional

from aws_ses.profile_manager import ProfileManager
from aws_ses.ses_client import SESClient


def send_simple_email(
    profile_name: Optional[str], region_name: Optional[str]
) -> None:
    """
    Send a simple plain text email.
    
    Args:
        profile_name: AWS profile to use
        region_name: AWS region to use
    """
    print("Sending a simple plain text email...")
    
    ses_client = SESClient(profile_name=profile_name, region_name=region_name)
    
    response = ses_client.send_email(
        source="sender@example.com",
        to_addresses="recipient@example.com",
        subject="Simple Text Email",
        body_text="This is a simple plain text email sent using AWS SES.",
    )
    
    print(f"Email sent! Message ID: {response['MessageId']}")


def send_html_email(
    profile_name: Optional[str], region_name: Optional[str]
) -> None:
    """
    Send an email with both plain text and HTML content.
    
    Args:
        profile_name: AWS profile to use
        region_name: AWS region to use
    """
    print("Sending an email with HTML content...")
    
    ses_client = SESClient(profile_name=profile_name, region_name=region_name)
    
    html_body = """
    <html>
    <head></head>
    <body>
        <h1>HTML Email Example</h1>
        <p>This is an <b>HTML</b> email sent using <i>AWS SES</i>.</p>
        <p>It includes:</p>
        <ul>
            <li>Formatted text</li>
            <li>HTML elements</li>
            <li>And more!</li>
        </ul>
    </body>
    </html>
    """
    
    response = ses_client.send_email(
        source="sender@example.com",
        to_addresses="recipient@example.com",
        subject="HTML Email Example",
        body_text="This is the plain text version of the email for clients that don't support HTML.",
        body_html=html_body,
    )
    
    print(f"HTML email sent! Message ID: {response['MessageId']}")


def send_email_with_cc_bcc(
    profile_name: Optional[str], region_name: Optional[str]
) -> None:
    """
    Send an email with CC and BCC recipients.
    
    Args:
        profile_name: AWS profile to use
        region_name: AWS region to use
    """
    print("Sending an email with CC and BCC recipients...")
    
    ses_client = SESClient(profile_name=profile_name, region_name=region_name)
    
    response = ses_client.send_email(
        source="sender@example.com",
        to_addresses=["primary@example.com", "another-primary@example.com"],
        cc_addresses=["cc1@example.com", "cc2@example.com"],
        bcc_addresses=["bcc@example.com"],
        reply_to_addresses=["reply@example.com"],
        subject="Email with CC and BCC",
        body_text="This email demonstrates CC and BCC functionality.",
    )
    
    print(f"Email with CC/BCC sent! Message ID: {response['MessageId']}")


def verify_email_address(
    profile_name: Optional[str], region_name: Optional[str], email: str
) -> None:
    """
    Verify an email address with AWS SES.
    
    Args:
        profile_name: AWS profile to use
        region_name: AWS region to use
        email: Email address to verify
    """
    print(f"Verifying email address: {email}...")
    
    ses_client = SESClient(profile_name=profile_name, region_name=region_name)
    
    ses_client.verify_email_identity(email)
    
    print(
        f"Verification email sent to {email}. "
        "Check your inbox and follow the instructions to complete verification."
    )


def list_verified_emails(
    profile_name: Optional[str], region_name: Optional[str]
) -> None:
    """
    List all verified email addresses.
    
    Args:
        profile_name: AWS profile to use
        region_name: AWS region to use
    """
    print("Listing verified email addresses...")
    
    ses_client = SESClient(profile_name=profile_name, region_name=region_name)
    
    emails = ses_client.list_verified_email_addresses()
    
    if emails:
        print("Verified email addresses:")
        for email in emails:
            print(f"  - {email}")
    else:
        print("No verified email addresses found.")


def check_sending_quota(
    profile_name: Optional[str], region_name: Optional[str]
) -> None:
    """
    Check the SES sending quota.
    
    Args:
        profile_name: AWS profile to use
        region_name: AWS region to use
    """
    print("Checking SES sending quota...")
    
    ses_client = SESClient(profile_name=profile_name, region_name=region_name)
    
    quota = ses_client.get_send_quota()
    
    print("SES Sending Quota:")
    print(f"  Max 24 Hour Send: {quota['Max24HourSend']}")
    print(f"  Max Send Rate: {quota['MaxSendRate']} emails/second")
    print(f"  Sent Last 24 Hours: {quota['SentLast24Hours']}")


def check_sending_statistics(
    profile_name: Optional[str], region_name: Optional[str]
) -> None:
    """
    Check the SES sending statistics.
    
    Args:
        profile_name: AWS profile to use
        region_name: AWS region to use
    """
    print("Checking SES sending statistics...")
    
    ses_client = SESClient(profile_name=profile_name, region_name=region_name)
    
    stats = ses_client.get_send_statistics()
    
    if stats.get("SendDataPoints"):
        print("SES Sending Statistics:")
        for point in stats["SendDataPoints"]:
            timestamp = point.get("Timestamp", "Unknown")
            bounces = point.get("Bounces", 0)
            complaints = point.get("Complaints", 0)
            delivery_attempts = point.get("DeliveryAttempts", 0)
            rejects = point.get("Rejects", 0)
            
            print(f"  Timestamp: {timestamp}")
            print(f"    Delivery Attempts: {delivery_attempts}")
            print(f"    Bounces: {bounces}")
            print(f"    Complaints: {complaints}")
            print(f"    Rejects: {rejects}")
    else:
        print("No sending statistics available.")


def list_aws_profiles() -> None:
    """List all available AWS profiles."""
    profiles = ProfileManager.get_available_profiles()
    
    if profiles:
        print("Available AWS profiles:")
        for profile in profiles:
            if profile == ProfileManager.get_latest_profile():
                print(f"  - {profile} (latest)")
            else:
                print(f"  - {profile}")
    else:
        print("No AWS profiles found.")


def simulate_lambda_invocation(
    profile_name: Optional[str], region_name: Optional[str]
) -> None:
    """
    Simulate invoking the Lambda function locally.
    
    Args:
        profile_name: AWS profile to use
        region_name: AWS region to use
    """
    from aws_ses.lambda_handler import handler
    
    print("Simulating Lambda invocation...")
    
    # Create a sample event
    event = {
        "source": "sender@example.com",
        "to_addresses": "recipient@example.com",
        "subject": "Test from Lambda Simulation",
        "body_text": "This is a test email from a simulated Lambda invocation.",
        "profile_name": profile_name,
        "region_name": region_name
    }
    
    # Call the handler
    response = handler(event, None)
    
    # Print the response
    print("Lambda response:")
    print(json.dumps(response, indent=2))


def main() -> None:
    """Main function to demonstrate various AWS SES operations."""
    parser = argparse.ArgumentParser(description="AWS SES Sample Usage")
    parser.add_argument(
        "--profile", 
        help="AWS profile to use. Use 'latest' for the most recently added profile."
    )
    parser.add_argument("--region", help="AWS region to use.")
    parser.add_argument(
        "--action",
        choices=[
            "send-simple",
            "send-html",
            "send-with-cc-bcc",
            "verify-email",
            "list-verified",
            "check-quota",
            "check-stats",
            "list-profiles",
            "simulate-lambda",
            "run-all"
        ],
        required=True,
        help="Action to perform"
    )
    parser.add_argument("--email", help="Email address for verification")
    
    args = parser.parse_args()
    
    # Validate profile if provided
    if args.profile and not ProfileManager.validate_profile(args.profile):
        if args.profile.lower() == "latest" and not ProfileManager.get_available_profiles():
            print("No AWS profiles found when trying to use 'latest'", file=sys.stderr)
        else:
            print(f"Profile '{args.profile}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Execute the requested action
    if args.action == "send-simple":
        send_simple_email(args.profile, args.region)
    elif args.action == "send-html":
        send_html_email(args.profile, args.region)
    elif args.action == "send-with-cc-bcc":
        send_email_with_cc_bcc(args.profile, args.region)
    elif args.action == "verify-email":
        if not args.email:
            print("Email address is required for verification", file=sys.stderr)
            sys.exit(1)
        verify_email_address(args.profile, args.region, args.email)
    elif args.action == "list-verified":
        list_verified_emails(args.profile, args.region)
    elif args.action == "check-quota":
        check_sending_quota(args.profile, args.region)
    elif args.action == "check-stats":
        check_sending_statistics(args.profile, args.region)
    elif args.action == "list-profiles":
        list_aws_profiles()
    elif args.action == "simulate-lambda":
        simulate_lambda_invocation(args.profile, args.region)
    elif args.action == "run-all":
        print("Running all sample operations...\n")
        list_aws_profiles()
        print("\n" + "-" * 50 + "\n")
        
        try:
            send_simple_email(args.profile, args.region)
            print("\n" + "-" * 50 + "\n")
            
            send_html_email(args.profile, args.region)
            print("\n" + "-" * 50 + "\n")
            
            send_email_with_cc_bcc(args.profile, args.region)
            print("\n" + "-" * 50 + "\n")
            
            list_verified_emails(args.profile, args.region)
            print("\n" + "-" * 50 + "\n")
            
            check_sending_quota(args.profile, args.region)
            print("\n" + "-" * 50 + "\n")
            
            check_sending_statistics(args.profile, args.region)
            print("\n" + "-" * 50 + "\n")
            
            simulate_lambda_invocation(args.profile, args.region)
            
            if args.email:
                print("\n" + "-" * 50 + "\n")
                verify_email_address(args.profile, args.region, args.email)
        except Exception as e:
            print(f"Error during sample operations: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
