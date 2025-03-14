"""
AWS profile manager for handling multiple profiles including 'latest'.
"""
from typing import List, Optional

import boto3
from botocore.exceptions import ProfileNotFound


class ProfileManager:
    """
    Manages AWS profiles, including support for a special 'latest' profile.
    """

    @staticmethod
    def get_available_profiles() -> List[str]:
        """
        Get a list of all available AWS profiles.

        Returns:
            List[str]: List of available profile names
        """
        return boto3.Session().available_profiles

    @staticmethod
    def get_latest_profile() -> Optional[str]:
        """
        Get the most recently added AWS profile.
        Assumes the most recently added profile is the last one in the list.

        Returns:
            Optional[str]: The name of the latest profile, or None if no profiles exist
        """
        profiles = ProfileManager.get_available_profiles()
        if not profiles:
            return None
        return profiles[-1]

    @staticmethod
    def validate_profile(profile_name: str) -> bool:
        """
        Validate that a profile exists.

        Args:
            profile_name: The name of the profile to validate

        Returns:
            bool: True if the profile exists, False otherwise
        """
        if profile_name.lower() == "latest":
            # Check if any profiles exist
            return bool(ProfileManager.get_available_profiles())

        try:
            # Try to create a session with the profile to validate it
            boto3.Session(profile_name=profile_name)
            return True
        except ProfileNotFound:
            return False

    @staticmethod
    def resolve_profile_name(profile_name: Optional[str]) -> Optional[str]:
        """
        Resolve a profile name, handling the special 'latest' case.

        Args:
            profile_name: The profile name to resolve, or None to use default

        Returns:
            Optional[str]: The resolved profile name, or None to use default

        Raises:
            ValueError: If 'latest' is specified but no profiles exist
        """
        if not profile_name:
            return None

        if profile_name.lower() == "latest":
            latest_profile = ProfileManager.get_latest_profile()
            if not latest_profile:
                raise ValueError("No AWS profiles found when trying to use 'latest'")
            return latest_profile

        return profile_name
