import re
import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 30  # seconds

NLB_BASE_URL = "https://www.nlb.lk"


def _extract_cookie_from_script(html_content: str) -> tuple[str | None, str | None]:
    """Extract cookie name/value from the NLB anti-bot setCookie JS snippet."""
    pattern = r"setCookie\(['\"]([^'\"]+)['\"],['\"]([^'\"]+)['\"],\d+\)"
    match = re.search(pattern, html_content)
    if match:
        return match.group(1), match.group(2)
    return None, None


def _get_nlb_session() -> requests.Session:
    """Return a requests.Session with the NLB cookie pre-set and retry logic."""
    session = requests.Session()

    # Retry up to 3 times with exponential backoff on connection/timeout errors
    retry_strategy = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=[500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    try:
        response = session.get(f"{NLB_BASE_URL}/lotteries", timeout=REQUEST_TIMEOUT)
        cookie_name, cookie_value = _extract_cookie_from_script(response.text)
        if cookie_name and cookie_value:
            session.cookies.set(cookie_name, cookie_value, domain="www.nlb.lk", path="/")
    except Exception:
        logger.warning("Failed to set up NLB session", exc_info=True)
    return session


def _parse_draw_number(draw_block) -> str | None:
    """Extract the draw number from the <h1> tag."""
    h1_tag = draw_block.find("h1")
    if h1_tag:
        match = re.search(r"\b(\d{3,5})\b", h1_tag.get_text(strip=True))
        if match:
            return match.group(1)
    return None


def _parse_date(draw_block) -> str | None:
    """Extract the draw date from the <p><b>Date:</b>...</p> pattern."""
    for p in draw_block.find_all("p"):
        b_tag = p.find("b")
        if b_tag and "Date:" in b_tag.get_text():
            return p.get_text(strip=True).replace("Date:", "").replace('"', "").strip()
    return None


def _parse_numbers_and_letter(draw_block) -> tuple[list[str], str | None]:
    """Extract winning numbers and the bonus letter."""
    numbers = []
    letter = None
    for li in draw_block.select("ol.B li"):
        li_classes = li.get("class", [])
        text = li.get_text(strip=True)
        if "Letter" in li_classes:
            letter = text
        elif text.isdigit():
            numbers.append(text)
    return numbers, letter





def scrape_draw(draw_id: int, lottery_name: str) -> dict:
    """
    Scrape a single lottery draw from the NLB website.

    Args:
        draw_id: The numeric draw ID used in the NLB URL.
        lottery_name: URL slug for the lottery (e.g. "mahajana-sampatha").

    Returns:
        Dict with keys: lottery_name, draw_no, date, letter, numbers, prize_structure.

    Raises:
        Exception: If the result block is not found on the page.
    """
    url = f"{NLB_BASE_URL}/results/{lottery_name}/{draw_id}"
    session = _get_nlb_session()

    try:
        response = session.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=REQUEST_TIMEOUT)
        soup = BeautifulSoup(response.text, "html.parser")

        draw_block = soup.find("div", class_="lresult")
        if not draw_block:
            logger.info("No results found for draw %s — likely not released yet", draw_id)
            return None

        return {
            "lottery_name": lottery_name,
            "draw_no": _parse_draw_number(draw_block),
            "date": _parse_date(draw_block),
            "letter": _parse_numbers_and_letter(draw_block)[1],
            "numbers": _parse_numbers_and_letter(draw_block)[0],
        }
    finally:
        session.close()
