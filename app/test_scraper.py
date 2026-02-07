import requests
from bs4 import BeautifulSoup
import re

# -------------------------
# Helper to extract JS cookie
# -------------------------
def extract_cookie_from_script(html_content):
    """
    Extract the cookie name and value from the NLB setCookie JS function.
    """
    pattern = r"setCookie\(['\"]([^'\"]+)['\"],['\"]([^'\"]+)['\"],\d+\)"
    match = re.search(pattern, html_content)
    if match:
        return match.group(1), match.group(2)
    return None, None

# -------------------------
# Create a session with cookie
# -------------------------
def get_nlb_session():
    """
    Returns a requests.Session() with the NLB cookie set.
    """
    url = "https://www.nlb.lk/lotteries"
    session = requests.Session()
    try:
        response = session.get(url, timeout=10)
        cookie_name, cookie_value = extract_cookie_from_script(response.text)
        if cookie_name and cookie_value:
            session.cookies.set(cookie_name, cookie_value, domain="www.nlb.lk", path="/")
        return session
    except Exception as e:
        print("Failed to set up session:", e)
        return session

# -------------------------
# Scraper for a single draw
# -------------------------
def scrape_draw(draw_id: int):
    url = f"https://www.nlb.lk/results/dhana-nidhanaya/{draw_id}"
    session = get_nlb_session()
    headers = {"User-Agent": "Mozilla/5.0"}

    response = session.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    draw_block = soup.find('div', class_='lresult')
    if not draw_block:
        session.close()
        raise Exception("Result block not found")

    # ---------------------
    # Draw number (from <h1>)
    # ---------------------
    draw_no = None
    h1_tag = draw_block.find('h1')
    if h1_tag:
        h1_text = h1_tag.get_text(strip=True)
        draw_no_match = re.search(r'\b(\d{3,5})\b', h1_text)
        if draw_no_match:
            draw_no = draw_no_match.group(1)

    # ---------------------
    # Date (from <p><b>Date:</b>)
    # ---------------------
    date = None
    date_tag = None
    # Find <p> that contains <b>Date:</b>
    for p in draw_block.find_all('p'):
        b_tag = p.find('b')
        if b_tag and 'Date:' in b_tag.get_text():
            date_tag = p
            break
    if date_tag:
        # Get text after <b>Date:</b>
        date_text = date_tag.get_text(strip=True)
        date = date_text.replace('Date:', '').replace('"', '').strip()

    # ---------------------
    # Numbers & letter
    # ---------------------
    numbers = []
    letter = None
    number_tags = draw_block.select('ol.B li')
    for li in number_tags:
        li_classes = li.get('class', [])
        text = li.get_text(strip=True)
        if 'Letter' in li_classes:
            letter = text
        elif text.isdigit():
            numbers.append(text)

    session.close()
    return {
        "draw_no": draw_no,
        "date": date,
        "letter": letter,
        "numbers": numbers
    }

# -------------------------
# Example usage
# -------------------------
if __name__ == "__main__":
    try:
        draw_id = 2127
        draw_data = scrape_draw(draw_id)
        print(f"Mahajana Sampatha Draw {draw_data['draw_no']} ({draw_data['date']}):")
        print(f"Letter: {draw_data['letter']}")
        print(f"Numbers: {', '.join(draw_data['numbers'])}")
    except Exception as e:
        print("Error:", e)
