import requests
from bs4 import BeautifulSoup

def scrape_draw(draw_id: int):
    url = f"https://www.nlb.lk/results/mahajana-sampatha/{draw_id}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Draw number
    draw_no_tag = soup.find("p", text=lambda t: t and "Draw No." in t)
    if not draw_no_tag:
        # fallback: find the <p> containing <b>Draw No.:</b>
        draw_no_tag = soup.find("p")
    draw_no = draw_no_tag.text.split(":")[1].strip().replace('"', '')

    # Date
    date_tag = soup.find("p", text=lambda t: t and "Date:" in t)
    if not date_tag:
        # fallback: second <p>
        date_tag = soup.find_all("p")[1]
    date = date_tag.text.split(":")[1].strip().replace('"', '')

    # Numbers (first <li> is letter, next six <li> are numbers)
    ol_tag = soup.find("ol", class_="B")
    li_tags = ol_tag.find_all("li")

    letter = li_tags[0].text.strip()
    numbers = [li.text.strip() for li in li_tags[1:7]]  # first 6 numbers

    return {
        "draw_no": draw_no,
        "date": date,
        "letter": letter,
        "numbers": numbers
    }


# Example usage
draw_data = scrape_draw(6097)
print(draw_data)
