from app.services.mahajana_scraper import scrape_draw
from app.services.db import insert_draw, get_max_draw_no

LOTTERY_NAME = "mahajana-sampatha"   # change if needed
DRAW_ID = 6098                       # use a real upcoming draw number

print("Max draw in DB BEFORE:", get_max_draw_no())

data = scrape_draw(DRAW_ID, LOTTERY_NAME)

print("SCRAPED DATA:")
print(data)

if data and data.get("draw_no") and data.get("numbers"):
    insert_draw(data)
    print("✅ Inserted into DB")
else:
    print("❌ Scraper returned incomplete data")

print("Max draw in DB AFTER:", get_max_draw_no())
