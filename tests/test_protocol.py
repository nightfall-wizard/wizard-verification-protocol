"""Tests for the verification protocol."""

import pytest
from src.wizard_verification.protocol import verify, VerificationResult


def test_verify_with_valid_input():
    """Test verification with valid input."""
    result = verify("test_wizard_input")
    assert result.verified is True
    assert result.reason == "Input format validated"


def test_verify_with_empty_input():
    """Test verification with empty input."""
    result = verify("")
    assert result.verified is False
    assert "Invalid input" in result.reason


def test_verify_with_none():
    """Test verification with None input."""
    result = verify(None)
    assert result.verified is False


def test_verification_result_is_success():
    """Test the is_success method."""
    result = VerificationResult(verified=True, reason="test")
    assert result.is_success() is True

    failed_result = VerificationResult(verified=False, reason="test")
    assert failed_result.is_success() is False
