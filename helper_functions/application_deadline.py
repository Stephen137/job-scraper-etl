from bs4 import BeautifulSoup

# HELPER FUNCTIONS
# ---------------------------------------------------------------------
# APPLICATION DEADLINE PARSE FUNCTION
# ---------------------------------------------------------------------
def extract_expiration_date(page):
    """
    Extracts expiration date from the job detail page.
    Looks for data-test="text-expirationDate" and extracts date after colon.
    Returns the date string (e.g., "12 gru 2025") or None.
    """
    try:
        page.wait_for_selector('span[data-test="text-expirationDate"]', timeout=5000)
        soup = BeautifulSoup(page.content(), "html.parser")
        expiration_span = soup.find('span', {'data-test': 'text-expirationDate'})
        
        if expiration_span:
            full_text = expiration_span.get_text(strip=True)
            if ':' in full_text:
                date_value = full_text.split(':', 1)[1].strip()
                return date_value
            else:
                return full_text
    except Exception as e:
        return None
