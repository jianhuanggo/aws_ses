"""
Unit tests for the AWS Lambda handler.
"""
import sys
import os

# Add the src directory to the path so we can import the aws_ses module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import json
import os
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from aws_ses.lambda_handler import handler


@pytest.fixture
def mock_aws_credentials():
    """Mock AWS credentials for tests."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture
def valid_event():
    """Create a valid Lambda event for testing."""
    return {
        "source": "sender@example.com",
        "to_addresses": "recipient@example.com",
        "subject": "Test Subject",
        "body_text": "Test Body",
        "body_html": "<html><body><h1>Test HTML Body</h1></body></html>",
        "cc_addresses": ["cc@example.com"],
        "bcc_addresses": ["bcc@example.com"],
        "reply_to_addresses": ["reply@example.com"],
        "profile_name": "default",
        "region_name": "us-east-1"
    }


@pytest.fixture
def minimal_event():
    """Create a minimal valid Lambda event for testing."""
    return {
        "source": "sender@example.com",
        "to_addresses": "recipient@example.com",
        "subject": "Test Subject",
        "body_text": "Test Body"
    }


@pytest.fixture
def invalid_event():
    """Create an invalid Lambda event for testing (missing required fields)."""
    return {
        "source": "sender@example.com",
        # Missing to_addresses
        "subject": "Test Subject",
        # Missing body_text
    }


class TestLambdaHandler:
    """Test cases for the Lambda handler."""

    @patch("aws_ses.lambda_handler.SESClient")
    def test_handler_success(self, mock_ses_client, valid_event, mock_aws_credentials):
        """Test successful email sending through Lambda."""
        # Mock the SESClient instance
        mock_client_instance = MagicMock()
        mock_ses_client.return_value = mock_client_instance
        
        # Mock the send_email method to return a successful response
        mock_client_instance.send_email.return_value = {"MessageId": "test-message-id"}
        
        # Call the handler
        response = handler(valid_event, {})
        
        # Verify the response
        assert response["statusCode"] == 200
        assert "body" in response
        
        body = json.loads(response["body"])
        assert body["message"] == "Email sent successfully"
        assert body["messageId"] == "test-message-id"
        
        # Verify SESClient was initialized with the correct parameters
        mock_ses_client.assert_called_once_with(
            profile_name=valid_event["profile_name"],
            region_name=valid_event["region_name"]
        )
        
        # Verify send_email was called with the correct parameters
        mock_client_instance.send_email.assert_called_once_with(
            source=valid_event["source"],
            to_addresses=valid_event["to_addresses"],
            subject=valid_event["subject"],
            body_text=valid_event["body_text"],
            body_html=valid_event["body_html"],
            cc_addresses=valid_event["cc_addresses"],
            bcc_addresses=valid_event["bcc_addresses"],
            reply_to_addresses=valid_event["reply_to_addresses"]
        )

    @patch("aws_ses.lambda_handler.SESClient")
    def test_handler_minimal_event(self, mock_ses_client, minimal_event, mock_aws_credentials):
        """Test Lambda with minimal valid event."""
        # Mock the SESClient instance
        mock_client_instance = MagicMock()
        mock_ses_client.return_value = mock_client_instance
        
        # Mock the send_email method to return a successful response
        mock_client_instance.send_email.return_value = {"MessageId": "test-message-id"}
        
        # Call the handler
        response = handler(minimal_event, {})
        
        # Verify the response
        assert response["statusCode"] == 200
        assert "body" in response
        
        body = json.loads(response["body"])
        assert body["message"] == "Email sent successfully"
        assert body["messageId"] == "test-message-id"
        
        # Verify SESClient was initialized with the correct parameters
        mock_ses_client.assert_called_once_with(
            profile_name=None,
            region_name=None
        )
        
        # Verify send_email was called with the correct parameters
        mock_client_instance.send_email.assert_called_once_with(
            source=minimal_event["source"],
            to_addresses=minimal_event["to_addresses"],
            subject=minimal_event["subject"],
            body_text=minimal_event["body_text"],
            body_html=None,
            cc_addresses=None,
            bcc_addresses=None,
            reply_to_addresses=None
        )

    def test_handler_invalid_event(self, invalid_event, mock_aws_credentials):
        """Test Lambda with invalid event (missing required fields)."""
        # Call the handler
        response = handler(invalid_event, {})
        
        # Verify the response
        assert response["statusCode"] == 400
        assert "body" in response
        
        body = json.loads(response["body"])
        assert "Missing required parameters" in body["message"]

    @patch("aws_ses.lambda_handler.SESClient")
    def test_handler_with_environment_variables(self, mock_ses_client, minimal_event, mock_aws_credentials):
        """Test Lambda using environment variables for profile and region."""
        # Set environment variables
        os.environ["AWS_PROFILE"] = "env_profile"
        os.environ["AWS_REGION"] = "us-west-2"
        
        # Mock the SESClient instance
        mock_client_instance = MagicMock()
        mock_ses_client.return_value = mock_client_instance
        
        # Mock the send_email method to return a successful response
        mock_client_instance.send_email.return_value = {"MessageId": "test-message-id"}
        
        # Call the handler
        response = handler(minimal_event, {})
        
        # Verify SESClient was initialized with environment variables
        mock_ses_client.assert_called_once_with(
            profile_name="env_profile",
            region_name="us-west-2"
        )
        
        # Clean up environment variables
        del os.environ["AWS_PROFILE"]
        del os.environ["AWS_REGION"]

    @patch("aws_ses.lambda_handler.SESClient")
    def test_handler_error_handling(self, mock_ses_client, valid_event, mock_aws_credentials):
        """Test error handling in Lambda."""
        # Mock the SESClient instance
        mock_client_instance = MagicMock()
        mock_ses_client.return_value = mock_client_instance
        
        # Mock the send_email method to raise an exception
        error_message = "Test error message"
        mock_client_instance.send_email.side_effect = Exception(error_message)
        
        # Call the handler
        response = handler(valid_event, {})
        
        # Verify the response
        assert response["statusCode"] == 500
        assert "body" in response
        
        body = json.loads(response["body"])
        assert "Error sending email" in body["message"]
        assert error_message in body["message"]

    @patch("aws_ses.lambda_handler.SESClient")
    def test_handler_client_error(self, mock_ses_client, valid_event, mock_aws_credentials):
        """Test handling of boto3 ClientError in Lambda."""
        # Mock the SESClient instance
        mock_client_instance = MagicMock()
        mock_ses_client.return_value = mock_client_instance
        
        # Mock the send_email method to raise a ClientError
        error_response = {"Error": {"Code": "MessageRejected", "Message": "Email address not verified"}}
        mock_client_instance.send_email.side_effect = ClientError(error_response, "SendEmail")
        
        # Call the handler
        response = handler(valid_event, {})
        
        # Verify the response
        assert response["statusCode"] == 500
        assert "body" in response
        
        body = json.loads(response["body"])
        assert "Error sending email" in body["message"]
        assert "MessageRejected" in body["message"]
