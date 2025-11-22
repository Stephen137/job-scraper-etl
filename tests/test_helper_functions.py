# Tests for Job Scraper Helper Functions
# Run with: python -m pytest tests/test_helper_functions.py -v

import pytest
from unittest.mock import Mock, MagicMock
from bs4 import BeautifulSoup

# Import helper functions - adjust import paths as needed
from helper_functions.addresses import extract_addresses
from helper_functions.contract_type import extract_type
from helper_functions.job_level import extract_level


class TestExtractAddresses:
    """Test suite for extract_addresses function"""
    
    def create_mock_page(self, html_content):
        """Helper to create a mock Playwright page object"""
        mock_page = Mock()
        mock_page.wait_for_selector = Mock(return_value=None)
        mock_page.content = Mock(return_value=html_content)
        return mock_page
    
    def test_extract_addresses_success(self):
        """Test successful address extraction with valid HTML"""
        html = """
        <html>
            <span data-test="text-currentLocation1">Kraków, Prądnik Biały</span>
            <span data-test="text-currentLocation2">Lekarska 1</span>
        </html>
        """
        mock_page = self.create_mock_page(html)
        
        result = extract_addresses(mock_page)
        
        assert result['address_1'] == 'Kraków, Prądnik Biały'
        assert result['address_2'] == 'Lekarska 1'
        mock_page.wait_for_selector.assert_called_once()
    
    def test_extract_addresses_missing_address_1(self):
        """Test when address_1 span is missing"""
        html = """
        <html>
            <span data-test="text-currentLocation2">Lekarska 1</span>
        </html>
        """
        mock_page = self.create_mock_page(html)
        
        result = extract_addresses(mock_page)
        
        assert result['address_1'] is None
        assert result['address_2'] == 'Lekarska 1'
    
    def test_extract_addresses_missing_address_2(self):
        """Test when address_2 span is missing"""
        html = """
        <html>
            <span data-test="text-currentLocation1">Kraków, Prądnik Biały</span>
        </html>
        """
        mock_page = self.create_mock_page(html)
        
        result = extract_addresses(mock_page)
        
        assert result['address_1'] == 'Kraków, Prądnik Biały'
        assert result['address_2'] is None
    
    def test_extract_addresses_both_missing(self):
        """Test when both addresses are missing"""
        html = "<html><body>No address data</body></html>"
        mock_page = self.create_mock_page(html)
        
        result = extract_addresses(mock_page)
        
        assert result['address_1'] is None
        assert result['address_2'] is None
    
    def test_extract_addresses_empty_html(self):
        """Test with empty HTML"""
        mock_page = self.create_mock_page("")
        
        result = extract_addresses(mock_page)
        
        assert result['address_1'] is None
        assert result['address_2'] is None
    
    def test_extract_addresses_timeout_exception(self):
        """Test when page.wait_for_selector times out"""
        mock_page = Mock()
        mock_page.wait_for_selector = Mock(side_effect=TimeoutError("Selector not found"))
        
        result = extract_addresses(mock_page)
        
        # Should return None values due to exception handling
        assert result['address_1'] is None
        assert result['address_2'] is None
    
    def test_extract_addresses_returns_dict(self):
        """Test that function always returns a dictionary"""
        html = "<html></html>"
        mock_page = self.create_mock_page(html)
        
        result = extract_addresses(mock_page)
        
        assert isinstance(result, dict)
        assert 'address_1' in result
        assert 'address_2' in result
    
    def test_extract_addresses_with_whitespace(self):
        """Test that whitespace is properly stripped"""
        html = """
        <html>
            <span data-test="text-currentLocation1">  Kraków, Prądnik Biały  </span>
            <span data-test="text-currentLocation2">  Lekarska 1  </span>
        </html>
        """
        mock_page = self.create_mock_page(html)
        
        result = extract_addresses(mock_page)
        
        assert result['address_1'] == 'Kraków, Prądnik Biały'
        assert result['address_2'] == 'Lekarska 1'
    
    def test_extract_addresses_with_special_characters(self):
        """Test extraction with Polish special characters"""
        html = """
        <html>
            <span data-test="text-currentLocation1">Łódź, Śródmieście</span>
            <span data-test="text-currentLocation2">Ul. Piotrkowska 99</span>
        </html>
        """
        mock_page = self.create_mock_page(html)
        
        result = extract_addresses(mock_page)
        
        assert result['address_1'] == 'Łódź, Śródmieście'
        assert result['address_2'] == 'Ul. Piotrkowska 99'
    
    def test_extract_addresses_page_content_called(self):
        """Test that page.content() is called"""
        html = """
        <html>
            <span data-test="text-currentLocation1">Address 1</span>
        </html>
        """
        mock_page = self.create_mock_page(html)
        
        extract_addresses(mock_page)
        
        mock_page.content.assert_called()


class TestExtractType:
    """Test suite for extract_type function"""
    
    def create_mock_page(self, html_content):
        """Helper to create a mock Playwright page object"""
        mock_page = Mock()
        mock_page.wait_for_selector = Mock(return_value=None)
        mock_page.content = Mock(return_value=html_content)
        return mock_page
    
    def test_extract_type_success(self):
        """Test successful contract type extraction"""
        html = """
        <html>
            <span data-test="text-contractName">Contract of employment</span>
        </html>
        """
        mock_page = self.create_mock_page(html)
        
        result = extract_type(mock_page)
        
        assert result == 'Contract of employment'
        mock_page.wait_for_selector.assert_called_once()
    
    def test_extract_type_b2b(self):
        """Test extraction of B2B contract type"""
        html = """
        <html>
            <span data-test="text-contractName">B2B</span>
        </html>
        """
        mock_page = self.create_mock_page(html)
        
        result = extract_type(mock_page)
        
        assert result == 'B2B'
    
    def test_extract_type_temporary(self):
        """Test extraction of temporary contract"""
        html = """
        <html>
            <span data-test="text-contractName">Temporary contract</span>
        </html>
        """
        mock_page = self.create_mock_page(html)
        
        result = extract_type(mock_page)
        
        assert result == 'Temporary contract'
    
    def test_extract_type_missing(self):
        """Test when contract type span is missing"""
        html = "<html><body>No contract data</body></html>"
        mock_page = self.create_mock_page(html)
        
        result = extract_type(mock_page)
        
        assert result is None
    
    def test_extract_type_empty_html(self):
        """Test with empty HTML"""
        mock_page = self.create_mock_page("")
        
        result = extract_type(mock_page)
        
        assert result is None
    
    def test_extract_type_timeout_exception(self):
        """Test when page.wait_for_selector times out"""
        mock_page = Mock()
        mock_page.wait_for_selector = Mock(side_effect=TimeoutError("Selector not found"))
        
        result = extract_type(mock_page)
        
        assert result is None
    
    def test_extract_type_with_whitespace(self):
        """Test that whitespace is properly stripped"""
        html = """
        <html>
            <span data-test="text-contractName">  Permanent contract  </span>
        </html>
        """
        mock_page = self.create_mock_page(html)
        
        result = extract_type(mock_page)
        
        assert result == 'Permanent contract'
    
    def test_extract_type_with_special_characters(self):
        """Test extraction with special characters"""
        html = """
        <html>
            <span data-test="text-contractName">Umowa o pracę (PL)</span>
        </html>
        """
        mock_page = self.create_mock_page(html)
        
        result = extract_type(mock_page)
        
        assert result == 'Umowa o pracę (PL)'
    
    def test_extract_type_page_content_called(self):
        """Test that page.content() is called"""
        html = "<html><span data-test='text-contractName'>Type</span></html>"
        mock_page = self.create_mock_page(html)
        
        extract_type(mock_page)
        
        mock_page.content.assert_called()
    
    def test_extract_type_returns_string_or_none(self):
        """Test that function returns either string or None"""
        html = "<html><span data-test='text-contractName'>Contract</span></html>"
        mock_page = self.create_mock_page(html)
        
        result = extract_type(mock_page)
        
        assert isinstance(result, str) or result is None
    
    def test_extract_type_general_exception(self):
        """Test that any exception returns None"""
        mock_page = Mock()
        mock_page.wait_for_selector = Mock(side_effect=Exception("Unexpected error"))
        
        result = extract_type(mock_page)
        
        assert result is None


class TestExtractLevel:
    """Test suite for extract_level function"""
    
    def create_mock_page(self, html_content):
        """Helper to create a mock Playwright page object"""
        mock_page = Mock()
        mock_page.wait_for_selector = Mock(return_value=None)
        mock_page.content = Mock(return_value=html_content)
        return mock_page
    
    def test_extract_level_mid(self):
        """Test successful extraction of mid-level position"""
        html = """
        <html>
            <span data-test="content-positionLevels">mid</span>
        </html>
        """
        mock_page = self.create_mock_page(html)
        
        result = extract_level(mock_page)
        
        assert result == 'mid'
        mock_page.wait_for_selector.assert_called_once()
    
    def test_extract_level_junior(self):
        """Test extraction of junior level position"""
        html = """
        <html>
            <span data-test="content-positionLevels">junior</span>
        </html>
        """
        mock_page = self.create_mock_page(html)
        
        result = extract_level(mock_page)
        
        assert result == 'junior'
    
    def test_extract_level_senior(self):
        """Test extraction of senior level position"""
        html = """
        <html>
            <span data-test="content-positionLevels">senior</span>
        </html>
        """
        mock_page = self.create_mock_page(html)
        
        result = extract_level(mock_page)
        
        assert result == 'senior'
    
    def test_extract_level_lead(self):
        """Test extraction of lead level position"""
        html = """
        <html>
            <span data-test="content-positionLevels">lead</span>
        </html>
        """
        mock_page = self.create_mock_page(html)
        
        result = extract_level(mock_page)
        
        assert result == 'lead'
    
    def test_extract_level_intern(self):
        """Test extraction of intern level position"""
        html = """
        <html>
            <span data-test="content-positionLevels">intern</span>
        </html>
        """
        mock_page = self.create_mock_page(html)
        
        result = extract_level(mock_page)
        
        assert result == 'intern'
    
    def test_extract_level_missing(self):
        """Test when job level span is missing"""
        html = "<html><body>No level data</body></html>"
        mock_page = self.create_mock_page(html)
        
        result = extract_level(mock_page)
        
        assert result is None
    
    def test_extract_level_empty_html(self):
        """Test with empty HTML"""
        mock_page = self.create_mock_page("")
        
        result = extract_level(mock_page)
        
        assert result is None
    
    def test_extract_level_timeout_exception(self):
        """Test when page.wait_for_selector times out"""
        mock_page = Mock()
        mock_page.wait_for_selector = Mock(side_effect=TimeoutError("Selector not found"))
        
        result = extract_level(mock_page)
        
        assert result is None
    
    def test_extract_level_with_whitespace(self):
        """Test that whitespace is properly stripped"""
        html = """
        <html>
            <span data-test="content-positionLevels">  mid-level  </span>
        </html>
        """
        mock_page = self.create_mock_page(html)
        
        result = extract_level(mock_page)
        
        assert result == 'mid-level'
    
    def test_extract_level_general_exception(self):
        """Test that any exception returns None"""
        mock_page = Mock()
        mock_page.wait_for_selector = Mock(side_effect=Exception("Unexpected error"))
        
        result = extract_level(mock_page)
        
        assert result is None
    
    def test_extract_level_page_content_called(self):
        """Test that page.content() is called"""
        html = "<html><span data-test='content-positionLevels'>Level</span></html>"
        mock_page = self.create_mock_page(html)
        
        extract_level(mock_page)
        
        mock_page.content.assert_called()
    
    def test_extract_level_returns_string_or_none(self):
        """Test that function returns either string or None"""
        html = "<html><span data-test='content-positionLevels'>senior</span></html>"
        mock_page = self.create_mock_page(html)
        
        result = extract_level(mock_page)
        
        assert isinstance(result, str) or result is None


class TestHelperFunctionsIntegration:
    """Integration tests combining multiple helper functions"""
    
    def test_extract_addresses_returns_none_on_general_exception(self):
        """Test that any exception returns None values"""
        mock_page = Mock()
        mock_page.wait_for_selector = Mock(side_effect=Exception("Unexpected error"))
        
        result = extract_addresses(mock_page)
        
        assert result == {'address_1': None, 'address_2': None}
    
    def test_multiple_extractions_same_page(self):
        """Test calling multiple extract functions on same mock page"""
        combined_html = """
        <html>
            <span data-test="text-currentLocation1">Kraków</span>
            <span data-test="text-contractName">Contract of employment</span>
            <span data-test="content-positionLevels">mid</span>
        </html>
        """
        
        address_mock = Mock()
        address_mock.wait_for_selector = Mock(return_value=None)
        address_mock.content = Mock(return_value=combined_html)
        
        contract_mock = Mock()
        contract_mock.wait_for_selector = Mock(return_value=None)
        contract_mock.content = Mock(return_value=combined_html)
        
        level_mock = Mock()
        level_mock.wait_for_selector = Mock(return_value=None)
        level_mock.content = Mock(return_value=combined_html)
        
        addresses = extract_addresses(address_mock)
        contract = extract_type(contract_mock)
        level = extract_level(level_mock)
        
        assert addresses['address_1'] == 'Kraków'
        assert contract == 'Contract of employment'
        assert level == 'mid'
    
    def test_all_functions_handle_exceptions_gracefully(self):
        """Test that all extraction functions handle exceptions gracefully"""
        failing_mock = Mock()
        failing_mock.wait_for_selector = Mock(side_effect=Exception("Network error"))
        
        addresses = extract_addresses(failing_mock)
        contract = extract_type(failing_mock)
        level = extract_level(failing_mock)
        
        assert addresses == {'address_1': None, 'address_2': None}
        assert contract is None
        assert level is None


# ================================================================
# Test Execution
# ================================================================
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])