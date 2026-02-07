from apscheduler.schedulers.background import BackgroundScheduler
from app.services.mahajana_sampatha import scrape_draw

last_draw_id = 6097  # load from DB in real project

def scheduled_scrape():
    global last_draw_id
    last_draw_id += 1
    data = scrape_draw(last_draw_id)
    print("Scraped:", data)
    # Save to database here

scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_scrape, 'interval', hours=24)
scheduler.start()
