"""
Standalone script for Heroku Scheduler to run the daily scrape.

Usage:
    python run_scrape.py

Heroku Scheduler calls this as a one-off process, so it's not
affected by dyno restarts or cold boots.
"""

import logging

logging.basicConfig(level=logging.INFO)

from app.services.db import get_max_draw_no, insert_draw
from app.services.mahajana_scraper import scrape_draw

logger = logging.getLogger(__name__)


def main():
    lottery_name = "mahajana-sampatha"

    max_db = get_max_draw_no(lottery_name)
    next_id = (max_db + 1) if max_db is not None else 6100

    logger.info("Latest draw in DB: %s — scraping draw %s", max_db, next_id)

    data = scrape_draw(next_id, lottery_name)

    if data is None:
        logger.info("Draw %s not available yet", next_id)
        return

    if not data.get("draw_no") or not data.get("numbers"):
        logger.warning("Incomplete data for draw %s: %s", next_id, data)
        return

    insert_draw(data)
    logger.info("Done — inserted draw %s", data.get("draw_no"))


if __name__ == "__main__":
    main()
