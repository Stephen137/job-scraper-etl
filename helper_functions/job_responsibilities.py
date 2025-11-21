from bs4 import BeautifulSoup

# ---------------------------------------------------------------------
# JOB RESPONSIBILITIES PARSE FUNCTION
# ---------------------------------------------------------------------
def extract_responsibilities(page):
    """
    Extracts job responsibilities from the job detail page.
    Returns a list of responsibility strings.
    Example: ['Understand business requirements and develop test cases.', 
              'Implement automated tests in Playwright and TypeScript.']
    """
    try:
        page.wait_for_selector('[data-test="section-responsibilities"]', timeout=5000)
        soup = BeautifulSoup(page.content(), "html.parser")
        
        # Find the responsibilities section
        resp_section = soup.find('div', {'data-test': 'section-responsibilities'})
        
        if resp_section:
            # Find all li items with class lxul5ps
            resp_items = resp_section.find_all('li', class_='lxul5ps')
            responsibilities = []
            
            for item in resp_items:
                resp_text = item.get_text(strip=True)
                if resp_text:
                    responsibilities.append(resp_text)
            
            return responsibilities if responsibilities else []
        
        return []
        
    except Exception as e:
        return []