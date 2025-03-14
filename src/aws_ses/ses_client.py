"""
AWS SES client for sending emails.
"""
from typing import Dict, List, Optional, Union

import boto3
from botocore.exceptions import ClientError


class SESClient:
    """
    Client for interacting with AWS SES service.
    Supports multiple AWS profiles including a special 'latest' profile.
    """

    def __init__(self, profile_name: Optional[str] = None, region_name: Optional[str] = None):
        """
        Initialize the SES client with optional profile and region.

        Args:
            profile_name: AWS profile name to use. If 'latest', will use the most recently
                          added profile. If None, will use the default profile.
            region_name: AWS region to use. If None, will use the region from the profile.
        """
        self.profile_name = profile_name
        self.region_name = region_name
        self.session = self._create_session()
        self.client = self.session.client("ses", region_name=region_name)

    def _create_session(self) -> boto3.Session:
        """
        Create a boto3 session using the specified profile.
        If profile is 'latest', use the most recently added profile.

        Returns:
            boto3.Session: The created session
        """
        if not self.profile_name:
            return boto3.Session()

        if self.profile_name.lower() == "latest":
            # Get available profiles and select the most recently added one
            available_profiles = boto3.Session().available_profiles
            if not available_profiles:
                raise ValueError("No AWS profiles found")
            # Assuming the most recently added profile is the last one in the list
            self.profile_name = available_profiles[-1]

        return boto3.Session(profile_name=self.profile_name)

    def send_email(
        self,
        source: str,
        to_addresses: Union[str, List[str]],
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        cc_addresses: Optional[Union[str, List[str]]] = None,
        bcc_addresses: Optional[Union[str, List[str]]] = None,
        reply_to_addresses: Optional[Union[str, List[str]]] = None,
    ) -> Dict:
        """
        Send an email using AWS SES.

        Args:
            source: The email address that is sending the email
            to_addresses: The recipient email address(es)
            subject: The subject of the email
            body_text: The plain text version of the email body
            body_html: The HTML version of the email body (optional)
            cc_addresses: CC recipient email address(es) (optional)
            bcc_addresses: BCC recipient email address(es) (optional)
            reply_to_addresses: Reply-to email address(es) (optional)

        Returns:
            Dict: The response from the SES service

        Raises:
            ClientError: If there is an error sending the email
        """
        # Convert single email addresses to lists
        if isinstance(to_addresses, str):
            to_addresses = [to_addresses]
        if cc_addresses and isinstance(cc_addresses, str):
            cc_addresses = [cc_addresses]
        if bcc_addresses and isinstance(bcc_addresses, str):
            bcc_addresses = [bcc_addresses]
        if reply_to_addresses and isinstance(reply_to_addresses, str):
            reply_to_addresses = [reply_to_addresses]

        # Prepare the email message
        message: Dict = {
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": body_text}},
        }

        if body_html:
            message["Body"]["Html"] = {"Data": body_html}

        # Prepare the destination
        destination: Dict = {"ToAddresses": to_addresses}
        if cc_addresses:
            destination["CcAddresses"] = cc_addresses
        if bcc_addresses:
            destination["BccAddresses"] = bcc_addresses

        # Prepare the email parameters
        email_params: Dict = {
            "Source": source,
            "Destination": destination,
            "Message": message,
        }

        if reply_to_addresses:
            email_params["ReplyToAddresses"] = reply_to_addresses

        try:
            response = self.client.send_email(**email_params)
            return response
        except ClientError as e:
            # Log the error and re-raise
            print(f"Error sending email: {e}")
            raise

    def verify_email_identity(self, email_address: str) -> Dict:
        """
        Verify an email address with AWS SES.
        AWS will send a verification email to the address.

        Args:
            email_address: The email address to verify

        Returns:
            Dict: The response from the SES service

        Raises:
            ClientError: If there is an error verifying the email
        """
        try:
            response = self.client.verify_email_identity(EmailAddress=email_address)
            return response
        except ClientError as e:
            print(f"Error verifying email identity: {e}")
            raise

    def list_verified_email_addresses(self) -> List[str]:
        """
        List all verified email addresses.

        Returns:
            List[str]: List of verified email addresses

        Raises:
            ClientError: If there is an error listing the verified emails
        """
        try:
            response = self.client.list_identities(IdentityType="EmailAddress")
            return response.get("Identities", [])
        except ClientError as e:
            print(f"Error listing verified email addresses: {e}")
            raise

    def get_send_quota(self) -> Dict:
        """
        Get the SES sending quota.

        Returns:
            Dict: The SES sending quota information

        Raises:
            ClientError: If there is an error getting the quota
        """
        try:
            response = self.client.get_send_quota()
            return response
        except ClientError as e:
            print(f"Error getting send quota: {e}")
            raise

    def get_send_statistics(self) -> Dict:
        """
        Get the SES sending statistics.

        Returns:
            Dict: The SES sending statistics

        Raises:
            ClientError: If there is an error getting the statistics
        """
        try:
            response = self.client.get_send_statistics()
            return response
        except ClientError as e:
            print(f"Error getting send statistics: {e}")
            raise
