"""
Unit tests for domain availability checker tool.

Tests the domain_checker module's ability to check domain availability
across multiple extensions (.com, .ai, .io) with caching and error handling.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import whois

from src.tools.domain_checker import (
    check_domain_availability,
    batch_check_domains,
    DomainCache,
    clear_cache,
    _check_single_domain
)


class TestDomainCache:
    """Test the DomainCache class."""

    def test_cache_initialization(self):
        """Test cache initializes with correct TTL."""
        cache = DomainCache(ttl_minutes=10)
        assert cache.ttl == timedelta(minutes=10)
        assert len(cache.cache) == 0

    def test_cache_set_and_get(self):
        """Test setting and getting cache entries."""
        cache = DomainCache(ttl_minutes=5)

        result = {'example.com': True}
        cache.set('example.com', result)

        cached = cache.get('example.com')
        assert cached == result

    def test_cache_miss(self):
        """Test cache returns None for missing entries."""
        cache = DomainCache(ttl_minutes=5)
        assert cache.get('nonexistent.com') is None

    def test_cache_expiration(self):
        """Test cache entries expire after TTL."""
        cache = DomainCache(ttl_minutes=5)

        # Set cache entry
        result = {'example.com': True}
        cache.set('example.com', result)

        # Manually expire the entry by setting cached_at to past
        cache.cache['example.com']['cached_at'] = datetime.utcnow() - timedelta(minutes=6)

        # Should return None as entry is expired
        assert cache.get('example.com') is None

        # Expired entry should be removed from cache
        assert 'example.com' not in cache.cache


class TestCheckSingleDomain:
    """Test the _check_single_domain function."""

    @patch('src.tools.domain_checker.whois.whois')
    def test_domain_available(self, mock_whois):
        """Test detecting available domain."""
        # Mock WHOIS response for available domain
        mock_result = Mock()
        mock_result.registrar = None
        mock_result.creation_date = None
        mock_result.status = None
        mock_whois.return_value = mock_result

        assert _check_single_domain('available.com') is True
        mock_whois.assert_called_once_with('available.com')

    @patch('src.tools.domain_checker.whois.whois')
    def test_domain_taken(self, mock_whois):
        """Test detecting taken domain."""
        # Mock WHOIS response for registered domain
        mock_result = Mock()
        mock_result.registrar = 'GoDaddy'
        mock_result.creation_date = datetime(2020, 1, 1)
        mock_result.status = 'clientTransferProhibited'
        mock_whois.return_value = mock_result

        assert _check_single_domain('taken.com') is False
        mock_whois.assert_called_once_with('taken.com')

    @patch('src.tools.domain_checker.whois.whois')
    def test_whois_error_assumes_available(self, mock_whois):
        """Test that WHOIS errors result in assuming domain is available."""
        # Mock WHOIS error
        mock_whois.side_effect = whois.parser.PywhoisError("WHOIS lookup failed")

        # Should assume available on error
        assert _check_single_domain('error.com') is True

    @patch('src.tools.domain_checker.whois.whois')
    def test_unexpected_error_assumes_available(self, mock_whois):
        """Test that unexpected errors result in assuming domain is available."""
        # Mock unexpected error
        mock_whois.side_effect = Exception("Network error")

        # Should assume available on error
        assert _check_single_domain('error.com') is True


class TestCheckDomainAvailability:
    """Test the check_domain_availability function."""

    def setup_method(self):
        """Clear cache before each test."""
        clear_cache()

    @patch('src.tools.domain_checker._check_single_domain')
    def test_check_default_extensions(self, mock_check):
        """Test checking domain with default extensions (.com, .ai, .io)."""
        # Mock all domains as available
        mock_check.return_value = True

        result = check_domain_availability('TestBrand')

        assert 'testbrand.com' in result
        assert 'testbrand.ai' in result
        assert 'testbrand.io' in result
        assert result['testbrand.com'] is True
        assert result['testbrand.ai'] is True
        assert result['testbrand.io'] is True

        # Should have called check 3 times (once per extension)
        assert mock_check.call_count == 3

    @patch('src.tools.domain_checker._check_single_domain')
    def test_check_custom_extensions(self, mock_check):
        """Test checking domain with custom extensions."""
        mock_check.return_value = True

        result = check_domain_availability('TestBrand', extensions=['.com'])

        assert 'testbrand.com' in result
        assert 'testbrand.ai' not in result
        assert 'testbrand.io' not in result

        # Should have called check only once
        assert mock_check.call_count == 1

    @patch('src.tools.domain_checker._check_single_domain')
    def test_brand_name_normalization(self, mock_check):
        """Test that brand names are normalized to lowercase domain format."""
        mock_check.return_value = True

        # Test with spaces
        result = check_domain_availability('My Brand')
        assert 'mybrand.com' in result

        # Test with hyphens
        clear_cache()
        result = check_domain_availability('My-Brand')
        assert 'mybrand.com' in result

        # Test with uppercase
        clear_cache()
        result = check_domain_availability('MYBRAND')
        assert 'mybrand.com' in result

    @patch('src.tools.domain_checker._check_single_domain')
    def test_mixed_availability(self, mock_check):
        """Test handling mixed availability results."""
        # Mock different results for different domains
        def mock_check_side_effect(domain):
            if domain == 'testbrand.com':
                return False  # Taken
            else:
                return True  # Available

        mock_check.side_effect = mock_check_side_effect

        result = check_domain_availability('TestBrand')

        assert result['testbrand.com'] is False
        assert result['testbrand.ai'] is True
        assert result['testbrand.io'] is True

    @patch('src.tools.domain_checker._check_single_domain')
    def test_caching_behavior(self, mock_check):
        """Test that results are cached and reused."""
        mock_check.return_value = True

        # First call - should hit WHOIS
        result1 = check_domain_availability('TestBrand', extensions=['.com'])
        assert mock_check.call_count == 1

        # Second call - should use cache
        result2 = check_domain_availability('TestBrand', extensions=['.com'])
        assert mock_check.call_count == 1  # Should not increase

        # Results should be identical
        assert result1 == result2


class TestBatchCheckDomains:
    """Test the batch_check_domains function."""

    def setup_method(self):
        """Clear cache before each test."""
        clear_cache()

    @patch('src.tools.domain_checker._check_single_domain')
    def test_batch_check_multiple_brands(self, mock_check):
        """Test batch checking multiple brand names."""
        mock_check.return_value = True

        brand_names = ['Brand1', 'Brand2', 'Brand3']
        results = batch_check_domains(brand_names)

        # Should have results for all brands
        assert 'Brand1' in results
        assert 'Brand2' in results
        assert 'Brand3' in results

        # Each brand should have 3 extensions
        assert len(results['Brand1']) == 3
        assert len(results['Brand2']) == 3
        assert len(results['Brand3']) == 3

    @patch('src.tools.domain_checker._check_single_domain')
    def test_batch_check_custom_extensions(self, mock_check):
        """Test batch checking with custom extensions."""
        mock_check.return_value = True

        brand_names = ['Brand1', 'Brand2']
        results = batch_check_domains(brand_names, extensions=['.com', '.ai'])

        # Each brand should have 2 extensions
        assert len(results['Brand1']) == 2
        assert len(results['Brand2']) == 2
        assert 'brand1.com' in results['Brand1']
        assert 'brand1.ai' in results['Brand1']

    @patch('src.tools.domain_checker._check_single_domain')
    @patch('src.tools.domain_checker.time.sleep')
    def test_batch_check_rate_limiting(self, mock_sleep, mock_check):
        """Test that batch checking includes rate limiting delays."""
        mock_check.return_value = True

        brand_names = ['Brand1', 'Brand2', 'Brand3']
        batch_check_domains(brand_names)

        # Should have called sleep for rate limiting (once per brand)
        assert mock_sleep.call_count == 3


class TestClearCache:
    """Test the clear_cache function."""

    @patch('src.tools.domain_checker._check_single_domain')
    def test_clear_cache_functionality(self, mock_check):
        """Test that clear_cache removes all cached entries."""
        mock_check.return_value = True

        # Add some entries to cache
        check_domain_availability('Brand1')
        check_domain_availability('Brand2')

        # First call should not hit WHOIS due to cache
        mock_check.reset_mock()
        check_domain_availability('Brand1')
        assert mock_check.call_count == 0

        # Clear cache
        clear_cache()

        # After clearing, should hit WHOIS again
        check_domain_availability('Brand1')
        assert mock_check.call_count == 3  # 3 extensions


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
