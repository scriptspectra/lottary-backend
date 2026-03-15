import os
import logging
from datetime import datetime, timezone

from dotenv import load_dotenv
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, func
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import select

load_dotenv()
logger = logging.getLogger(__name__)

# Database connection 
connection_uri = os.getenv("CONNECTION_URI")
if not connection_uri:
    raise RuntimeError("CONNECTION_URI environment variable not set")

engine = create_engine(connection_uri)
metadata = MetaData()

# Table definition 
jaya_draws = Table(
    "jaya_draws",
    metadata,
    Column("lottery_name", String, primary_key=False),
    Column("draw_no", Integer, primary_key=True),
    Column("date", String, nullable=False),
    Column("letter", String, nullable=False),
    Column("numbers", PG_ARRAY(Integer), nullable=False),
    Column("created_at", String, default=lambda: str(datetime.now(timezone.utc))),
)


def init_db():
    """Create the tables defined in metadata if they don't exist."""
    metadata.create_all(engine)


def insert_draw(draw_data: dict):
    """Validate and insert a single draw record, skipping duplicates."""
    draw_no = draw_data.get("draw_no")
    if draw_no is None:
        logger.warning("Skipping insert: draw_no is missing")
        return

    try:
        draw_no_int = int(draw_no)
    except (ValueError, TypeError):
        logger.warning("Skipping insert: invalid draw_no=%s", draw_no)
        return

    with engine.begin() as conn:
        # Check for duplicates
        existing = conn.execute(
            select(jaya_draws.c.draw_no).where(jaya_draws.c.draw_no == draw_no_int)
        )
        if existing.first():
            logger.info("Draw %s already exists, skipping", draw_no_int)
            return

        # Parse numbers list
        numbers_list = draw_data.get("numbers") or []
        try:
            numbers = [int(n) for n in numbers_list]
        except (ValueError, TypeError):
            logger.warning("Skipping insert: invalid numbers for draw %s", draw_no_int)
            return

        stmt = jaya_draws.insert().values(
            lottery_name=draw_data.get("lottery_name") or "unknown",
            draw_no=draw_no_int,
            date=draw_data.get("date") or "",
            letter=draw_data.get("letter") or "",
            numbers=numbers,
            created_at=str(datetime.now(timezone.utc)),
        )

        try:
            conn.execute(stmt)
            logger.info("Inserted draw %s", draw_no_int)
        except IntegrityError:
            logger.exception("Failed to insert draw %s", draw_no_int)


def get_max_draw_no(lottery_name: str) -> int | None:
    """Return the maximum draw_no for a specific lottery, or None if empty."""
    with engine.connect() as conn:
        try:
            result = conn.execute(
                select(func.max(jaya_draws.c.draw_no)).where(
                    jaya_draws.c.lottery_name == lottery_name
                )
            )
            max_val = result.scalar()
            return int(max_val) if max_val is not None else None
        except Exception:
            logger.exception("Failed to get max draw_no for %s", lottery_name)
            return None
