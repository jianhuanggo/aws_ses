"""
Unit tests for the ProfileManager class.
"""
import sys
import os

# Add the src directory to the path so we can import the aws_ses module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from unittest.mock import patch

from aws_ses.profile_manager import ProfileManager


class TestProfileManager:
    """Test cases for the ProfileManager class."""

    @patch("boto3.Session")
    def test_get_available_profiles(self, mock_session):
        """Test getting available profiles."""
        # Mock the available_profiles property
        mock_session.return_value.available_profiles = ["default", "dev", "prod"]
        
        profiles = ProfileManager.get_available_profiles()
        
        assert profiles == ["default", "dev", "prod"]
        mock_session.assert_called_once()

    @patch("aws_ses.profile_manager.ProfileManager.get_available_profiles")
    def test_get_latest_profile_with_profiles(self, mock_get_profiles):
        """Test getting the latest profile when profiles exist."""
        mock_get_profiles.return_value = ["default", "dev", "prod"]
        
        latest = ProfileManager.get_latest_profile()
        
        assert latest == "prod"
        mock_get_profiles.assert_called_once()

    @patch("aws_ses.profile_manager.ProfileManager.get_available_profiles")
    def test_get_latest_profile_no_profiles(self, mock_get_profiles):
        """Test getting the latest profile when no profiles exist."""
        mock_get_profiles.return_value = []
        
        latest = ProfileManager.get_latest_profile()
        
        assert latest is None
        mock_get_profiles.assert_called_once()

    @patch("boto3.Session")
    @patch("aws_ses.profile_manager.ProfileManager.get_available_profiles")
    def test_validate_profile_latest_with_profiles(self, mock_get_profiles, mock_session):
        """Test validating 'latest' profile when profiles exist."""
        mock_get_profiles.return_value = ["default", "dev", "prod"]
        
        result = ProfileManager.validate_profile("latest")
        
        assert result is True
        mock_get_profiles.assert_called_once()
        mock_session.assert_not_called()

    @patch("boto3.Session")
    @patch("aws_ses.profile_manager.ProfileManager.get_available_profiles")
    def test_validate_profile_latest_no_profiles(self, mock_get_profiles, mock_session):
        """Test validating 'latest' profile when no profiles exist."""
        mock_get_profiles.return_value = []
        
        result = ProfileManager.validate_profile("latest")
        
        assert result is False
        mock_get_profiles.assert_called_once()
        mock_session.assert_not_called()

    @patch("boto3.Session")
    def test_validate_profile_existing(self, mock_session):
        """Test validating an existing profile."""
        # No exception means profile exists
        result = ProfileManager.validate_profile("dev")
        
        assert result is True
        mock_session.assert_called_once_with(profile_name="dev")

    @patch("boto3.Session")
    def test_validate_profile_non_existing(self, mock_session):
        """Test validating a non-existing profile."""
        # Raise ProfileNotFound exception
        from botocore.exceptions import ProfileNotFound
        mock_session.side_effect = ProfileNotFound(profile="nonexistent")
        
        result = ProfileManager.validate_profile("nonexistent")
        
        assert result is False
        mock_session.assert_called_once_with(profile_name="nonexistent")

    @patch("aws_ses.profile_manager.ProfileManager.get_latest_profile")
    def test_resolve_profile_name_none(self, mock_get_latest):
        """Test resolving None profile name."""
        result = ProfileManager.resolve_profile_name(None)
        
        assert result is None
        mock_get_latest.assert_not_called()

    @patch("aws_ses.profile_manager.ProfileManager.get_latest_profile")
    def test_resolve_profile_name_normal(self, mock_get_latest):
        """Test resolving a normal profile name."""
        result = ProfileManager.resolve_profile_name("dev")
        
        assert result == "dev"
        mock_get_latest.assert_not_called()

    @patch("aws_ses.profile_manager.ProfileManager.get_latest_profile")
    def test_resolve_profile_name_latest_exists(self, mock_get_latest):
        """Test resolving 'latest' when profiles exist."""
        mock_get_latest.return_value = "prod"
        
        result = ProfileManager.resolve_profile_name("latest")
        
        assert result == "prod"
        mock_get_latest.assert_called_once()

    @patch("aws_ses.profile_manager.ProfileManager.get_latest_profile")
    def test_resolve_profile_name_latest_none(self, mock_get_latest):
        """Test resolving 'latest' when no profiles exist."""
        mock_get_latest.return_value = None
        
        with pytest.raises(ValueError, match="No AWS profiles found"):
            ProfileManager.resolve_profile_name("latest")
        
        mock_get_latest.assert_called_once()
