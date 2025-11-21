from bs4 import BeautifulSoup

# ---------------------------------------------------------------------
# EXPECTED TECHNOLOGIES PARSE FUNCTION
# ---------------------------------------------------------------------
def extract_expected_technologies(page):
    """
    Extracts expected technologies from the job detail page.
    Returns a list of technology strings (e.g., ['SQL', 'Python']).
    """
    try:
        page.wait_for_selector('[data-test="section-technologies"]', timeout=5000)
        soup = BeautifulSoup(page.content(), "html.parser")
        tech_section = soup.find('div', {'data-test': 'section-technologies'})
        
        if tech_section:
            tech_divs = tech_section.find_all('div', {'data-test': 'chip-technology'})
            technologies = []
            
            for div in tech_divs:
                title = div.get('title')
                if title:
                    technologies.append(title)
                else:
                    tech_text = div.get_text(strip=True)
                    if tech_text:
                        technologies.append(tech_text)
            
            return technologies if technologies else []
        else:
            return []
    except Exception as e:
        return []