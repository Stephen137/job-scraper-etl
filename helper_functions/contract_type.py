from bs4 import BeautifulSoup

# ---------------------------------------------------------------------
# CONTRACT TYPE PARSE FUNCTION
# ---------------------------------------------------------------------
def extract_type(page):
    """
    Extracts contract type from the job detail page.
    Looks for data-test="text-contractName" and extracts text.
    Returns the string (e.g."contract of employment") or None.
    """
    try:
        page.wait_for_selector('span[data-test="text-contractName"]', timeout=5000)
        soup = BeautifulSoup(page.content(), "html.parser")
        contract_tag = soup.find('span', {'data-test': 'text-contractName'})
        contract_type = contract_tag.get_text(strip=True) if contract_tag else None
        return contract_type
    except Exception as e:
        return None