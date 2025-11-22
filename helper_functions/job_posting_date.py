from bs4 import BeautifulSoup

# HELPER FUNCTIONS
# ---------------------------------------------------------------------
# JOB POSTING DATE PARSE FUNCTION
# ---------------------------------------------------------------------
def extract_job_posting_date(page):
    """
    Extracts job posting date from the job detail page.
    Looks for data-test="text-fromDate" and extracts date after colon.
    Returns the date string (e.g., "12 gru 2025") or None.
    """
    try:
        page.wait_for_selector('span[data-test="text-fromDate"]', timeout=5000)
        soup = BeautifulSoup(page.content(), "html.parser")
        job_posting_span = soup.find('span', {'data-test': 'text-fromDate'})
        
        if job_posting_span:
            full_text = job_posting_span.get_text(strip=True)
            if ':' in full_text:
                date_value = full_text.split(':', 1)[1].strip()
                return date_value
            else:
                return full_text
    except Exception as e:
        return None
