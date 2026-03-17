import logging
from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from app.services.db import get_session
from app.services.notification_service import send_win_notification
from app.constants.prizes import LOTTERY_PRIZES 
from app.services.lottery_checker import check_lottery_ticket  
from sqlmodel import text

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/webhook",
    tags=["webhook"],
)

def process_new_draw(payload: dict):
    record = payload.get("record", {})
    if not record:
        logger.warning("Webhook payload missing 'record' field")
        return

    lottery_name = record.get("lottery_name")
    draw_no = record.get("draw_no")
    draw_numbers = record.get("numbers", [])
    draw_letter = record.get("letter")
    draw_special = record.get("special")  # optional, for Mega Power or other lotteries
    
    if not lottery_name or not draw_no:
        logger.error(f"Incomplete draw record: {record}")
        return

    logger.info(f"Processing new draw: {lottery_name} #{draw_no}")

    prize_tiers = LOTTERY_PRIZES.get(lottery_name.upper())
    if not prize_tiers:
        logger.info(f"No prize tiers found for lottery type: {lottery_name}")
        return

    with get_session() as session:
        try:
            query = text("""
                SELECT id, user_id, scanned_numbers, scanned_letter, scanned_special_component
                FROM public.tickets 
                WHERE lottery_type = :lottery 
                  AND draw_number = :draw_no 
                  AND status = 'PENDING'
            """)
            tickets = session.execute(query, {"lottery": lottery_name.upper(), "draw_no": draw_no}).fetchall()
            logger.info(f"Found {len(tickets)} pending tickets for {lottery_name} draw {draw_no}")

            for ticket in tickets:
                ticket_id, user_id, scanned_nums, scanned_letter, scanned_special_component = ticket
                t_nums = scanned_nums if isinstance(scanned_nums, list) else []

                # Check ticket using generic function
                result = check_lottery_ticket(
                    ticket_numbers=t_nums,
                    ticket_letter=scanned_letter,
                    draw_numbers=draw_numbers,
                    draw_letter=draw_letter,
                    prize_tiers=prize_tiers,
                    ticket_special_component=scanned_special_component,
                    special_component=draw_special
                )

                new_status = 'WIN' if result["is_winner"] else 'NO_WIN'
                win_amt = result["win_amount"]

                update_query = text("""
                    UPDATE public.tickets 
                    SET status = :status, win_amount = :win_amt 
                    WHERE id = :id
                """)
                session.execute(update_query, {"status": new_status, "win_amt": win_amt, "id": ticket_id})

                if result["is_winner"]:
                    logger.info(f"Ticket {ticket_id} WON Rs {win_amt}")
                    user_query = text("SELECT fcm_token FROM public.users WHERE id = :user_id")
                    user_record = session.execute(user_query, {"user_id": user_id}).fetchone()
                    if user_record and user_record[0]:
                        send_win_notification(user_record[0], lottery_name, win_amt, draw_no)
                    else:
                        logger.info(f"No FCM token for user {user_id}. Skipping notification.")

            session.commit()
            logger.info(f"Successfully processed draw {draw_no} for {lottery_name}")

        except Exception as e:
            logger.error(f"Error processing tickets for {lottery_name} draw {draw_no}: {e}")
            session.rollback()


@router.post("/supabase-draw-event")
async def supabase_draw_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    table_name = payload.get("table")
    action_type = payload.get("type")

    if table_name != "jaya_draws":
        logger.info(f"Ignoring webhook for table: {table_name}")
        return {"status": "ignored", "reason": f"Table {table_name} not handled"}

    if action_type != "INSERT":
        logger.info(f"Ignoring webhook action type: {action_type}")
        return {"status": "ignored", "reason": f"Action {action_type} not handled"}

    background_tasks.add_task(process_new_draw, payload)

    return {"status": "accepted", "message": "Draw processing started in background"}