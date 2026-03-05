import logging
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler

from app.services.mahajana_scraper import scrape_draw
from app.services.db import insert_draw, get_max_draw_no

logger = logging.getLogger(__name__)

# configure lotteries and fallback as in run_scrape
LOTTERIES = [
    "mahajana-sampatha",
    "zand",
]

# fallback draw id for new lotteries
FALLBACK_LAST_DRAW_ID = 6099

# Sri Lanka timezone (UTC+5:30)
SL_TZ = ZoneInfo("Asia/Colombo")

scheduler = BackgroundScheduler(timezone=SL_TZ)


def scheduled_scrape():
    """Run one scrape for each configured lottery.

    The original version targeted only Mahajana Sampatha; now every lottery in
    `LOTTERIES` will be advanced independently.  The fallback draw ID ensures
    we start from a reasonable number on a fresh database.
    """

    for lottery_name in LOTTERIES:
        try:
            max_db = get_max_draw_no(lottery_name)
            next_id = (max_db + 1) if max_db is not None else (FALLBACK_LAST_DRAW_ID + 1)

            logger.info("[%s] Attempting to scrape draw %s", lottery_name, next_id)

            data = scrape_draw(next_id, lottery_name)

            if data is None:
                logger.info("[%s] Draw %s not available yet", lottery_name, next_id)
                continue

            if not data.get("draw_no") or not data.get("numbers"):
                logger.warning(
                    "[%s] Incomplete data for draw %s, skipping: %s",
                    lottery_name,
                    next_id,
                    data,
                )
                continue

            insert_draw(data)
            logger.info("[%s] Scraped and inserted draw %s", lottery_name, data.get("draw_no"))

        except Exception:
            logger.exception("scheduled_scrape failed for %s", lottery_name)


def start_scheduler():
    """Register the scrape job and start the background scheduler."""
    try:
        if not scheduler.get_job("mahajana_scrape"):
            scheduler.add_job(
                scheduled_scrape,
                "cron",
                hour=22,
                minute=0,
                timezone=SL_TZ,
                id='mahajana_scrape',
            )

        if not scheduler.running:
            scheduler.start()
            logger.info("Scheduler started — mahajana_scrape runs daily at 10:00 PM SL time")

    except Exception:
        logger.exception("Failed to start scheduler")


def shutdown_scheduler():
    """Stop the background scheduler."""
    try:
        if scheduler.running:
            scheduler.shutdown()
            logger.info("Background scheduler stopped")
    except Exception:
        logger.exception("Failed to shutdown scheduler")
