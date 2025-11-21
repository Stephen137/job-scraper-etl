from bs4 import BeautifulSoup

# ---------------------------------------------------------------------
# ADDRESS PARSE FUNCTION
# ---------------------------------------------------------------------
def extract_addresses(page):
    """
    Extracts address information from the job detail page.
    Returns a dict with address_1 and address_2.
    Example: {'address_1': 'Kraków, Prądnik Biały', 'address_2': 'Lekarska 1'}
    """
    try:
        page.wait_for_selector('[data-test="section-workplace"]', timeout=5000)
        soup = BeautifulSoup(page.content(), "html.parser")
        
        # Extract address_1 (e.g., "Kraków, Prądnik Biały")
        address_1_tag = soup.find('span', {'data-test': 'text-currentLocation1'})
        address_1 = address_1_tag.get_text(strip=True) if address_1_tag else None
        
        # Extract address_2 (e.g., "Lekarska 1")
        address_2_tag = soup.find('span', {'data-test': 'text-currentLocation2'})
        address_2 = address_2_tag.get_text(strip=True) if address_2_tag else None
        
        return {
            'address_1': address_1,
            'address_2': address_2
        }
    except Exception as e:
        return {
            'address_1': None,
            'address_2': None
        }