import os
from sqlalchemy import create_engine, Table, Column, Integer, String, JSON, MetaData, func
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import select
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Your Supabase/Postgres URI
connection_uri = os.getenv("CONNECTION_URI")

engine = create_engine(connection_uri)
metadata = MetaData()

# Table definition
jaya_draws = Table(
    'jaya_draws',
    metadata,
    Column('lottery_name', String, primary_key=False),
    Column('draw_no', Integer, primary_key=True),
    Column('date', String, nullable=False),
    Column('letter', String, nullable=False),
    Column('numbers', PG_ARRAY(Integer), nullable=False),
    Column('prize_structure', JSON, nullable=False),
    Column('created_at', String, default=lambda: str(datetime.utcnow()))
)

metadata.create_all(engine)

def insert_draw(draw_data):
    # Use a transaction so inserts are committed
    with engine.begin() as conn:
        # Validate incoming data
        draw_no = draw_data.get('draw_no')
        if draw_no is None:
            logger.warning("Skipping insert: draw_no is missing")
            return

        try:
            draw_no_int = int(draw_no)
        except Exception:
            logger.warning("Skipping insert: invalid draw_no=%s", draw_no)
            return

        # Avoid duplicates
        result = conn.execute(select(jaya_draws.c.draw_no).where(jaya_draws.c.draw_no == draw_no_int))
        if result.first():
            logger.info("Draw %s already exists", draw_no_int)
            return

        numbers_list = draw_data.get('numbers') or []
        try:
            numbers = [int(n) for n in numbers_list]
        except Exception:
            logger.warning("Skipping insert: invalid numbers for draw %s", draw_no_int)
            return

        stmt = jaya_draws.insert().values(
            lottery_name=draw_data.get('lottery_name') or 'unknown',
            draw_no=draw_no_int,
            date=draw_data.get('date') or '',
            letter=draw_data.get('letter') or '',
            numbers=numbers,
            prize_structure=draw_data.get('prize_structure') or {},
            created_at=str(datetime.utcnow())
        )

        try:
            conn.execute(stmt)
            logger.info("Inserted draw %s", draw_no_int)
        except IntegrityError as e:
            logger.exception("Failed to insert draw: %s", e)


def get_max_draw_no():
    """Return the maximum draw_no from the `jaya_draws` table or None if table is empty / on error."""
    with engine.connect() as conn:
        try:
            result = conn.execute(select(func.max(jaya_draws.c.draw_no)))
            max_val = result.scalar()
            return int(max_val) if max_val is not None else None
        except Exception as e:
            logger.exception("Failed to get max draw_no: %s", e)
            return None
