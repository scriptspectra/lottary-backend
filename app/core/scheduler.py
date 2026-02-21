import logging
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler

from app.services.mahajana_scraper import scrape_draw
from app.services.db import insert_draw, get_max_draw_no

logger = logging.getLogger(__name__)

# Fallback draw ID if the database is empty
_FALLBACK_LAST_DRAW_ID = 6099

# Sri Lanka timezone (UTC+5:30)
SL_TZ = ZoneInfo("Asia/Colombo")

scheduler = BackgroundScheduler(timezone=SL_TZ)


def scheduled_scrape():
    """
    Scrape the next Mahajana Sampatha draw.

    Queries Supabase for the latest draw_no, increments by 1,
    scrapes that draw, and saves it back to the database.
    """
    lottery_name = "mahajana-sampatha"

    try:
        max_db = get_max_draw_no(lottery_name)
        next_id = (max_db + 1) if max_db is not None else (_FALLBACK_LAST_DRAW_ID + 1)

        logger.info("Attempting to scrape draw %s for %s", next_id, lottery_name)

        data = scrape_draw(next_id, lottery_name)

        if data is None:
            logger.info("Draw %s not available yet", next_id)
            return

        if not data.get("draw_no") or not data.get("numbers"):
            logger.warning("Incomplete data for draw %s, skipping: %s", next_id, data)
            return

        insert_draw(data)
        logger.info("Scraped and inserted draw %s", data.get("draw_no"))

    except Exception:
        logger.exception("scheduled_scrape failed")


def start_scheduler():
    """Register the scrape job and start the background scheduler."""
    try:
        if not scheduler.get_job("mahajana_scrape"):
            scheduler.add_job(
                scheduled_scrape,
                "cron",
                hour=22,
                minute=0,
                id="mahajana_scrape",
            )

        if not scheduler.running:
            scheduler.start()
            logger.info("Scheduler started — mahajana_scrape runs daily at 10:00 PM SL time")

    except Exception:
        logger.exception("Failed to start scheduler")


def shutdown_scheduler():
    """Gracefully stop the background scheduler."""
    try:
        if scheduler.running:
            scheduler.shutdown()
            logger.info("Background scheduler stopped")
    except Exception:
        logger.exception("Failed to shutdown scheduler")
