from bs4 import BeautifulSoup

# ---------------------------------------------------------------------
# JOB LEVEL PARSE FUNCTION
# ---------------------------------------------------------------------
def extract_level(page):
    """
    Extracts level from the job detail page.
    Looks for data-test="content-positionLevels" and extracts text.
    Returns the string (e.g."mid") or None.
    """
    try:
        page.wait_for_selector('span[data-test="content-positionLevels"]', timeout=5000)
        soup = BeautifulSoup(page.content(), "html.parser")
        job_tag = soup.find('span', {'data-test': 'content-positionLevels'})
        job_level = job_tag.get_text(strip=True) if job_tag else None
        return job_level
    except Exception as e:
        return None
