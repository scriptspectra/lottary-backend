from app.services.mahajana_scraper import scrape_draw
from app.services.db import insert_draw, get_max_draw_no

# configure one or more lotteries and a draw id that should exist on the
# NLB site.
LOTTERIES = [
    ("mahajana-sampatha", 6099),
    ("zand", 1000),  # example fallback / existing draw id
]

for lottery_name, draw_id in LOTTERIES:
    print("\n--- testing", lottery_name, "draw", draw_id, "---")
    print("Max draw in DB BEFORE:", get_max_draw_no(lottery_name))

    data = scrape_draw(draw_id, lottery_name)
    print("SCRAPED DATA:")
    print(data)

    if data and data.get("draw_no") and data.get("numbers"):
        insert_draw(data)
        print("Inserted into DB")
    else:
        print("Scraper returned incomplete data")

    print("Max draw in DB AFTER:", get_max_draw_no(lottery_name))
