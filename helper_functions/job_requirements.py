from bs4 import BeautifulSoup

# ---------------------------------------------------------------------
# JOB REQUIREMENTS PARSE FUNCTION
# ---------------------------------------------------------------------
def extract_requirements(page):
    """
    Extracts job requirements from the job detail page.
    Returns a list of requirement strings.
    Example: ['Nice to have: knowledge of Drupal, Moodle or Totara', 
              'Working proficiency of the English language...']
    """
    try:
        page.wait_for_selector('[data-test="section-requirements"]', timeout=5000)
        soup = BeautifulSoup(page.content(), "html.parser")
        
        # Find the requirements section
        req_section = soup.find('div', {'data-test': 'section-requirements'})
        
        if req_section:
            # Find the expected requirements ul
            req_ul = req_section.find('ul', {'data-test': 'section-requirements-expected'})
            
            if req_ul:
                # Get all li items
                req_items = req_ul.find_all('li', class_='lxul5ps')
                requirements = []
                
                for item in req_items:
                    req_text = item.get_text(strip=True)
                    # Remove the ":before" text if it exists
                    if req_text:
                        requirements.append(req_text)
                
                return requirements if requirements else []
        
        return []
        
    except Exception as e:
        return []
