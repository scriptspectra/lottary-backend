import logging
logger = logging.getLogger(__name__)

def send_win_notification(fcm_token: str, lottery_name: str, win_amount: float, draw_no: int):
    """Send a win notification to the user.
    This is a no-op placeholder if no FCM integration is configured.
    """
    if not fcm_token:
        logger.warning("No FCM token provided; skipping notification.")
        return
    logger.info("[Notification] Would send win notification to token=%s lottery=%s draw=%s amount=%.2f", fcm_token, lottery_name, draw_no, win_amount)
