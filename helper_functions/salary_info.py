from bs4 import BeautifulSoup

# ---------------------------------------------------------------------
# SALARY INFO PARSE FUNCTION
# ---------------------------------------------------------------------
def extract_salary_details(page):
    """
    Extracts detailed salary information from the job detail page.
    Returns a dict with remuneration, frequency, and gross or net.
    Example: {'remuneration': '20000 - 23500', 'frequency': 'mth', 'gross or net': 'net'}
    """
    try:
        page.wait_for_selector('span[data-test="text-contractSalary"]', timeout=5000)
        soup = BeautifulSoup(page.content(), "html.parser")
        
        salary_tag = soup.find('span', {'data-test': 'text-contractSalary'})
        remuneration = salary_tag.get_text(strip=True) if salary_tag else None
        
        gross_or_net_tag = soup.find('span', {'data-test': 'text-contractUnits'})
        gross_or_net = gross_or_net_tag.get_text(strip=True) if gross_or_net_tag else None
        
        frequency_tag = soup.find('span', {'data-test': 'text-contractTimeUnits'})
        frequency = frequency_tag.get_text(strip=True) if frequency_tag else None
        
        return {
            'remuneration': remuneration,
            'frequency': frequency,
            'gross_or_net': gross_or_net
        }
    except Exception as e:
        return {
            'remuneration': None,
            'frequency': None,
            'gross_or_net': None
        }
