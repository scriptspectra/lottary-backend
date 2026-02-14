from app.services.mahajana_sampatha import scrape_draw
from app.services.db import insert_draw, get_max_draw_no

if __name__ == '__main__':
    draw_id = 365
    print('Scraping draw', draw_id)
    try:
        data = scrape_draw(draw_id)
        print('Scraped data:', data)
    except Exception as e:
        print('Scrape failed:', e)
        raise

    print('Attempting insert...')
    try:
        insert_draw(data)
    except Exception as e:
        print('Insert failed:', e)

    print('Max draw_no in DB now:', get_max_draw_no())
