# AWS SES Email Sender

A production-grade Python library for sending emails using AWS Simple Email Service (SES) with support for multiple AWS profiles.

## Features

- Send plain text and HTML emails
- Support for CC, BCC, and reply-to addresses
- Multiple AWS profile support, including a special 'latest' profile option
- Command-line interface for all operations
- AWS Lambda handler for serverless email sending
- Comprehensive test suite

## Installation

```bash
# Clone the repository
git clone https://github.com/jianhuanggo/aws_ses.git
cd aws_ses

# Install using pip
pip install -e .
```

## AWS Credentials

Before using this library, you need to have AWS credentials configured. You can set up credentials in several ways:

1. Using AWS CLI: `aws configure`
2. Environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
3. Shared credentials file: `~/.aws/credentials`
4. IAM roles for EC2 instances or Lambda functions

## Usage

### Basic Usage

```python
from aws_ses.ses_client import SESClient

# Create a client using the default profile
ses_client = SESClient()

# Or specify a profile and region
ses_client = SESClient(profile_name="my-profile", region_name="us-west-2")

# Use the special 'latest' profile (most recently added profile)
ses_client = SESClient(profile_name="latest", region_name="us-east-1")

# Send a simple email
response = ses_client.send_email(
    source="sender@example.com",
    to_addresses="recipient@example.com",
    subject="Hello from AWS SES",
    body_text="This is a test email sent using AWS SES."
)

print(f"Email sent! Message ID: {response['MessageId']}")
```

### Sending HTML Emails

```python
ses_client = SESClient(profile_name="latest")

html_body = """
<html>
<head></head>
<body>
    <h1>HTML Email Example</h1>
    <p>This is an <b>HTML</b> email sent using <i>AWS SES</i>.</p>
</body>
</html>
"""

response = ses_client.send_email(
    source="sender@example.com",
    to_addresses="recipient@example.com",
    subject="HTML Email Example",
    body_text="This is the plain text version of the email.",
    body_html=html_body
)
```

### Using CC, BCC, and Reply-To

```python
ses_client = SESClient()

response = ses_client.send_email(
    source="sender@example.com",
    to_addresses=["primary@example.com", "another-primary@example.com"],
    cc_addresses=["cc1@example.com", "cc2@example.com"],
    bcc_addresses=["bcc@example.com"],
    reply_to_addresses=["reply@example.com"],
    subject="Email with CC and BCC",
    body_text="This email demonstrates CC and BCC functionality."
)
```

### Verifying Email Addresses

Before you can send emails using SES, you need to verify the sender email address:

```python
ses_client = SESClient()
ses_client.verify_email_identity("sender@example.com")
```

### AWS Lambda Integration

You can use the included Lambda handler to send emails from AWS Lambda:

```python
# lambda_function.py
from aws_ses.lambda_handler import handler

def lambda_handler(event, context):
    return handler(event, context)
```

Example event:

```json
{
    "source": "sender@example.com",
    "to_addresses": "recipient@example.com",
    "subject": "Email from Lambda",
    "body_text": "This is a test email sent from AWS Lambda.",
    "body_html": "<html><body><h1>Hello from Lambda!</h1></body></html>",
    "cc_addresses": ["cc@example.com"],
    "bcc_addresses": ["bcc@example.com"],
    "reply_to_addresses": ["reply@example.com"],
    "profile_name": "default",
    "region_name": "us-east-1"
}
```

## Command-Line Interface

The package includes a command-line interface for common operations:

### Sending an Email

```bash
# Using default profile
aws-ses send --from sender@example.com --to recipient@example.com --subject "Test Email" --body-text "This is a test email."

# Using a specific profile
aws-ses --profile my-profile send --from sender@example.com --to recipient@example.com --subject "Test Email" --body-text "This is a test email."

# Using the 'latest' profile
aws-ses --profile latest send --from sender@example.com --to recipient@example.com --subject "Test Email" --body-text "This is a test email."

# With HTML content
aws-ses send --from sender@example.com --to recipient@example.com --subject "Test Email" --body-text "This is a test email." --body-html "<html><body><h1>Hello!</h1></body></html>"

# With CC and BCC
aws-ses send --from sender@example.com --to recipient1@example.com --to recipient2@example.com --cc cc@example.com --bcc bcc@example.com --reply-to reply@example.com --subject "Test Email" --body-text "This is a test email."
```

### Verifying an Email Address

```bash
aws-ses verify sender@example.com
```

### Listing Verified Email Addresses

```bash
aws-ses list-verified
```

### Checking Sending Quota

```bash
aws-ses quota
```

### Checking Sending Statistics

```bash
aws-ses stats
```

### Listing Available AWS Profiles

```bash
aws-ses list-profiles
```

## Sample Script

The package includes a sample script in `examples/sample_usage.py` that demonstrates various features:

```bash
# List available profiles
python examples/sample_usage.py --action list-profiles

# Send a simple email
python examples/sample_usage.py --profile latest --region us-east-1 --action send-simple

# Send an HTML email
python examples/sample_usage.py --profile default --action send-html

# Send an email with CC and BCC
python examples/sample_usage.py --action send-with-cc-bcc

# Verify an email address
python examples/sample_usage.py --action verify-email --email your-email@example.com

# List verified email addresses
python examples/sample_usage.py --action list-verified

# Check sending quota
python examples/sample_usage.py --action check-quota

# Check sending statistics
python examples/sample_usage.py --action check-stats

# Simulate Lambda invocation
python examples/sample_usage.py --action simulate-lambda

# Run all sample operations
python examples/sample_usage.py --action run-all
```

## Multiple AWS Profiles Support

The library supports using multiple AWS profiles, including a special 'latest' profile option that automatically selects the most recently added profile in your AWS credentials file.

### How the 'latest' Profile Works

When you specify `profile_name="latest"`, the library:

1. Retrieves all available profiles from your AWS credentials
2. Selects the last profile in the list (assumed to be the most recently added)
3. Uses that profile for AWS operations

This is useful when you frequently add new profiles and want to use the most recent one without remembering its name.

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=aws_ses
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Created by Devin AI for jianhuanggo.
