from apscheduler.schedulers.background import BackgroundScheduler
import logging
from datetime import datetime as dt
from zoneinfo import ZoneInfo

from app.services.mahajana_scraper import scrape_draw
from app.services import db as db_service
from app.services.db import insert_draw

logger = logging.getLogger(__name__)

# Sri Lanka timezone (UTC+5:30)
SL_TZ = ZoneInfo("Asia/Colombo")

last_draw_id = 6097


def scheduled_scrape():
    """Scrape the next draw for Mahajana Sampatha and insert into DB."""
    global last_draw_id

    lottery_name = "mahajana-sampatha"   # ⭐ explicitly defined

    try:
        max_db = db_service.get_max_draw_no()

        if max_db is not None:
            next_id = max_db + 1
        else:
            next_id = last_draw_id + 1

        # call the scrape draw function with the lottery name
        data = scrape_draw(next_id, lottery_name)

        if not data:
            logger.warning("No data returned for draw %s", next_id)
            return

        if not data.get('draw_no') or not data.get('numbers'):
            logger.warning("Incomplete data for draw %s: %s", next_id, data)
            return

        insert_draw(data)
        last_draw_id = next_id

        logger.info(
            "Scraped and inserted draw %s for %s",
            data.get('draw_no'),
            lottery_name
        )

    except Exception:
        logger.exception("scheduled_scrape failed")


scheduler = BackgroundScheduler()


def start_scheduler():
    try:
        if not scheduler.get_job('mahajana_scrape'):
            scheduler.add_job(
                scheduled_scrape,
                'cron',
                hour=22,
                minute=0,
                timezone=SL_TZ,
                id='mahajana_scrape',
            )

        if not scheduler.running:
            scheduler.start()
            logger.info("Background scheduler started")

    except Exception:
        logger.exception("Failed to start scheduler")


def shutdown_scheduler():
    try:
        if scheduler.running:
            scheduler.shutdown()
            logger.info("Background scheduler stopped")
    except Exception:
        logger.exception("Failed to shutdown scheduler")
