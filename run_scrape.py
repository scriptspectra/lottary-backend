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


# define the lotteries we care about and a default starting draw number
# the fallback value will be used for any lottery that has no records yet
LOTTERIES = [
    "mahajana-sampatha",
    "zand",              # add new lottery slugs here
    # "another-lottery",
]
FALLBACK_DRAW_NO = 6100


def main():
    """Loop through all configured lotteries and attempt one scrape each.

    The script figures out the next draw ID by querying the database for the
    highest draw number we already have.  If the table is empty for a
    lottery, `FALLBACK_DRAW_NO` is used so we don't start at zero.
    """

    for lottery_name in LOTTERIES:
        max_db = get_max_draw_no(lottery_name)
        next_id = (max_db + 1) if max_db is not None else FALLBACK_DRAW_NO

        logger.info(
            "[%s] Latest draw in DB: %s — scraping draw %s",
            lottery_name,
            max_db,
            next_id,
        )

        data = scrape_draw(next_id, lottery_name)

        if data is None:
            logger.info("[%s] Draw %s not available yet", lottery_name, next_id)
            # try the next lottery rather than exiting completely
            continue

        if not data.get("draw_no") or not data.get("numbers"):
            logger.warning(
                "[%s] Incomplete data for draw %s: %s",
                lottery_name,
                next_id,
                data,
            )
            continue

        insert_draw(data)
        logger.info("[%s] Done — inserted draw %s", lottery_name, data.get("draw_no"))


if __name__ == "__main__":
    main()
