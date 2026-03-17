from app.services.mahajana_scraper import scrape_draw
from app.services.db import insert_draw, get_max_draw_no
from app.services.db import delete_old_draws

# configure one or more lotteries and a draw id that should exist on the
# NLB site.
LOTTERIES = [
    ("mahajana-sampatha", 6099),
    ("dhana-nidhanaya", 2161),  
    ("govisetha", 4373),
    ("mega-power", 2479),
    ("nlb-jaya", 399),
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

def scrape_lottery_range(lottery_name, start_draw_number, end_draw_number):
    print(f"\nScraping {lottery_name} from {start_draw_number} to {end_draw_number}")

    initial_max = get_max_draw_no(lottery_name)
    print("Max draw in DB BEFORE:", initial_max)

    success_count = 0
    fail_count = 0

    for draw_id in range(start_draw_number, end_draw_number + 1):
        print(f"\n→ Processing draw {draw_id}")

        try:
            data = scrape_draw(draw_id, lottery_name)

            if data and data.get("draw_no") and data.get("numbers"):
                insert_draw(data)
                success_count += 1
                print(f"✓ Inserted draw {draw_id}")
            else:
                fail_count += 1
                print(f"✗ Incomplete data for draw {draw_id}")

        except Exception as e:
            fail_count += 1
            print(f"✗ Error for draw {draw_id}: {e}")

    final_max = get_max_draw_no(lottery_name)

    print("\nSummary")
    print("Inserted:", success_count)
    print("Failed:", fail_count)
    print("Max draw in DB AFTER:", final_max)

if __name__ == "__main__":
    scrape_lottery_range("mahajana-sampatha", 6000, 6100)
    scrape_lottery_range("dhana-nidhanaya", 2061, 2161)
    scrape_lottery_range("govisetha", 4273, 4373)
    scrape_lottery_range("mega-power", 2379, 2479)
    scrape_lottery_range("nlb-jaya", 299, 399)
    delete_old_draws()