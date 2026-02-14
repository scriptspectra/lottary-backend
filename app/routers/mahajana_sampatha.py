from fastapi import APIRouter
from app.services.mahajana_scraper import scrape_draw
from app.services.db import insert_draw
from typing import Optional

router = APIRouter(prefix="/mahajana", tags=["mahajana"])


@router.get("/scrape/{draw_id}")
def scrape_and_insert(draw_id: int, lottery_name: Optional[str] = "mahajana-sampatha"):
    """Scrape a specific draw and insert into DB."""
    
    # ⭐ SAME FUNCTION SIGNATURE
    draw_data = scrape_draw(draw_id, lottery_name)

    if not draw_data:
        return {"error": "Scraping failed"}

    insert_draw(draw_data)

    return {
        "message": f"Draw {draw_id} scraped and inserted successfully",
        "draw": draw_data
    }
