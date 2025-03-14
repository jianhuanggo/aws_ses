"""
Unit tests for the SESClient class.
"""
import sys
import os

# Add the src directory to the path so we can import the aws_ses module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from botocore.exceptions import ClientError
from moto import mock_aws

from aws_ses.ses_client import SESClient


@pytest.fixture
def mock_aws_credentials():
    """Mock AWS credentials for tests."""
    import os
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture
def ses_client(mock_aws_credentials):
    """Create a mocked SES client for testing."""
    with mock_aws():
        client = SESClient(region_name="us-east-1")
        # Verify a test email address for use in tests
        client.verify_email_identity("sender@example.com")
        client.verify_email_identity("recipient@example.com")
        yield client


class TestSESClient:
    """Test cases for the SESClient class."""

    def test_init_default(self, mock_aws_credentials):
        """Test initialization with default parameters."""
        client = SESClient()
        assert client.profile_name is None
        assert client.region_name is None
        assert client.session is not None
        assert client.client is not None

    def test_init_with_region(self, mock_aws_credentials):
        """Test initialization with region specified."""
        region = "us-west-2"
        client = SESClient(region_name=region)
        assert client.profile_name is None
        assert client.region_name == region
        assert client.session is not None
        assert client.client is not None

    def test_send_email_basic(self, ses_client):
        """Test sending a basic email."""
        response = ses_client.send_email(
            source="sender@example.com",
            to_addresses="recipient@example.com",
            subject="Test Subject",
            body_text="Test Body",
        )
        assert "MessageId" in response
        assert isinstance(response["MessageId"], str)

    def test_send_email_with_html(self, ses_client):
        """Test sending an email with HTML content."""
        response = ses_client.send_email(
            source="sender@example.com",
            to_addresses="recipient@example.com",
            subject="Test Subject",
            body_text="Test Body",
            body_html="<html><body><h1>Test HTML Body</h1></body></html>",
        )
        assert "MessageId" in response
        assert isinstance(response["MessageId"], str)

    def test_send_email_with_cc_bcc(self, ses_client):
        """Test sending an email with CC and BCC recipients."""
        response = ses_client.send_email(
            source="sender@example.com",
            to_addresses=["recipient@example.com", "recipient2@example.com"],
            cc_addresses=["cc@example.com"],
            bcc_addresses=["bcc@example.com"],
            reply_to_addresses=["reply@example.com"],
            subject="Test Subject",
            body_text="Test Body",
        )
        assert "MessageId" in response
        assert isinstance(response["MessageId"], str)

    def test_send_email_string_to_list_conversion(self, ses_client):
        """Test that string addresses are converted to lists."""
        response = ses_client.send_email(
            source="sender@example.com",
            to_addresses="recipient@example.com",
            cc_addresses="cc@example.com",
            bcc_addresses="bcc@example.com",
            reply_to_addresses="reply@example.com",
            subject="Test Subject",
            body_text="Test Body",
        )
        assert "MessageId" in response
        assert isinstance(response["MessageId"], str)

    def test_verify_email_identity(self, ses_client):
        """Test verifying an email identity."""
        response = ses_client.verify_email_identity("test@example.com")
        assert response is not None
        # The response should be a dict with metadata
        assert isinstance(response, dict)

    def test_list_verified_email_addresses(self, ses_client):
        """Test listing verified email addresses."""
        # We've already verified two emails in the fixture
        emails = ses_client.list_verified_email_addresses()
        assert isinstance(emails, list)
        assert len(emails) >= 2
        assert "sender@example.com" in emails
        assert "recipient@example.com" in emails

    def test_get_send_quota(self, ses_client):
        """Test getting the send quota."""
        quota = ses_client.get_send_quota()
        assert isinstance(quota, dict)
        assert "Max24HourSend" in quota
        assert "MaxSendRate" in quota
        assert "SentLast24Hours" in quota

    def test_get_send_statistics(self, ses_client):
        """Test getting send statistics."""
        stats = ses_client.get_send_statistics()
        assert isinstance(stats, dict)
        assert "SendDataPoints" in stats
