from fastapi import APIRouter
from app.services.mahajana_sampatha import scrape_draw

router = APIRouter(prefix="/lottery")

@router.get("/draw/{draw_id}")
def get_draw(draw_id: int):
    return scrape_draw(draw_id)
