"""
Command-line interface for AWS SES email sender.
"""
import sys
from typing import List, Optional

import click

from aws_ses.profile_manager import ProfileManager
from aws_ses.ses_client import SESClient


@click.group()
@click.option(
    "--profile",
    "-p",
    help="AWS profile to use. Use 'latest' for the most recently added profile.",
)
@click.option("--region", "-r", help="AWS region to use.")
@click.pass_context
def cli(ctx: click.Context, profile: Optional[str], region: Optional[str]) -> None:
    """AWS SES email sender with multiple profile support."""
    # Validate profile if provided
    if profile and not ProfileManager.validate_profile(profile):
        if profile.lower() == "latest" and not ProfileManager.get_available_profiles():
            click.echo("No AWS profiles found when trying to use 'latest'", err=True)
        else:
            click.echo(f"Profile '{profile}' not found", err=True)
        sys.exit(1)

    # Store in context for subcommands
    ctx.obj = {"profile": profile, "region": region}


@cli.command()
@click.option("--from", "from_email", required=True, help="Sender email address.")
@click.option("--to", required=True, multiple=True, help="Recipient email address(es).")
@click.option("--cc", multiple=True, help="CC recipient email address(es).")
@click.option("--bcc", multiple=True, help="BCC recipient email address(es).")
@click.option("--reply-to", multiple=True, help="Reply-to email address(es).")
@click.option("--subject", required=True, help="Email subject.")
@click.option("--body-text", required=True, help="Plain text email body.")
@click.option("--body-html", help="HTML email body.")
@click.pass_context
def send(
    ctx: click.Context,
    from_email: str,
    to: List[str],
    cc: List[str],
    bcc: List[str],
    reply_to: List[str],
    subject: str,
    body_text: str,
    body_html: Optional[str],
) -> None:
    """Send an email using AWS SES."""
    profile = ctx.obj.get("profile")
    region = ctx.obj.get("region")

    try:
        ses_client = SESClient(profile_name=profile, region_name=region)
        response = ses_client.send_email(
            source=from_email,
            to_addresses=list(to),
            subject=subject,
            body_text=body_text,
            body_html=body_html,
            cc_addresses=list(cc) if cc else None,
            bcc_addresses=list(bcc) if bcc else None,
            reply_to_addresses=list(reply_to) if reply_to else None,
        )
        click.echo(f"Email sent! Message ID: {response['MessageId']}")
    except Exception as e:
        click.echo(f"Error sending email: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("email")
@click.pass_context
def verify(ctx: click.Context, email: str) -> None:
    """Verify an email address with AWS SES."""
    profile = ctx.obj.get("profile")
    region = ctx.obj.get("region")

    try:
        ses_client = SESClient(profile_name=profile, region_name=region)
        ses_client.verify_email_identity(email)
        click.echo(
            f"Verification email sent to {email}. "
            "Check your inbox and follow the instructions to complete verification."
        )
    except Exception as e:
        click.echo(f"Error verifying email: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def list_verified(ctx: click.Context) -> None:
    """List all verified email addresses."""
    profile = ctx.obj.get("profile")
    region = ctx.obj.get("region")

    try:
        ses_client = SESClient(profile_name=profile, region_name=region)
        emails = ses_client.list_verified_email_addresses()
        if emails:
            click.echo("Verified email addresses:")
            for email in emails:
                click.echo(f"  - {email}")
        else:
            click.echo("No verified email addresses found.")
    except Exception as e:
        click.echo(f"Error listing verified emails: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def quota(ctx: click.Context) -> None:
    """Get the SES sending quota."""
    profile = ctx.obj.get("profile")
    region = ctx.obj.get("region")

    try:
        ses_client = SESClient(profile_name=profile, region_name=region)
        quota = ses_client.get_send_quota()
        click.echo("SES Sending Quota:")
        click.echo(f"  Max 24 Hour Send: {quota['Max24HourSend']}")
        click.echo(f"  Max Send Rate: {quota['MaxSendRate']} emails/second")
        click.echo(f"  Sent Last 24 Hours: {quota['SentLast24Hours']}")
    except Exception as e:
        click.echo(f"Error getting quota: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def stats(ctx: click.Context) -> None:
    """Get the SES sending statistics."""
    profile = ctx.obj.get("profile")
    region = ctx.obj.get("region")

    try:
        ses_client = SESClient(profile_name=profile, region_name=region)
        stats_data = ses_client.get_send_statistics()
        if stats_data.get("SendDataPoints"):
            click.echo("SES Sending Statistics:")
            for point in stats_data["SendDataPoints"]:
                timestamp = point.get("Timestamp", "Unknown")
                bounces = point.get("Bounces", 0)
                complaints = point.get("Complaints", 0)
                delivery_attempts = point.get("DeliveryAttempts", 0)
                rejects = point.get("Rejects", 0)
                
                click.echo(f"  Timestamp: {timestamp}")
                click.echo(f"    Delivery Attempts: {delivery_attempts}")
                click.echo(f"    Bounces: {bounces}")
                click.echo(f"    Complaints: {complaints}")
                click.echo(f"    Rejects: {rejects}")
        else:
            click.echo("No sending statistics available.")
    except Exception as e:
        click.echo(f"Error getting statistics: {e}", err=True)
        sys.exit(1)


@cli.command()
def list_profiles() -> None:
    """List all available AWS profiles."""
    profiles = ProfileManager.get_available_profiles()
    if profiles:
        click.echo("Available AWS profiles:")
        for profile in profiles:
            if profile == ProfileManager.get_latest_profile():
                click.echo(f"  - {profile} (latest)")
            else:
                click.echo(f"  - {profile}")
    else:
        click.echo("No AWS profiles found.")


def main() -> None:
    """Main entry point for the CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
