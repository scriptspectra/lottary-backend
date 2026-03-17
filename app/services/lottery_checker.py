import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)

def check_lottery_ticket(
    ticket_numbers: List[str],
    ticket_letter: Optional[str],
    draw_numbers: List[int],
    draw_letter: Optional[str],
    prize_tiers: List[Dict[str, Any]],
    special_component: Optional[int] = None,
    ticket_special_component: Optional[int] = None
) -> dict:
    """
    Generic lottery ticket checker.
    
    prize_tiers: list of dicts with keys:
        - matchedNumbers: int
        - letterMatched: bool
        - specialComponentMatched: bool (optional)
        - prizeAmount: float
    special_component: the drawn special number (if any)
    ticket_special_component: ticket's special number (if any)
    """
    # Convert ticket numbers to int safely
    try:
        t_nums = [int(n) for n in ticket_numbers if str(n).isdigit()]
    except ValueError as e:
        logger.error(f"Error converting ticket numbers to int: {e}")
        return {"is_winner": False, "win_amount": 0.0}

    # Count matching numbers
    matched_numbers_count = len(set(t_nums).intersection(set(draw_numbers)))
    
    # Check letter match
    letter_matched = False
    if ticket_letter and draw_letter:
        letter_matched = str(ticket_letter).strip().upper() == str(draw_letter).strip().upper()
    
    # Check special component match
    special_matched = False
    if special_component is not None and ticket_special_component is not None:
        special_matched = ticket_special_component == special_component

    # Determine win amount based on prize tiers
    win_amount = 0.0
    for tier in prize_tiers:
        tier_special = tier.get("specialComponentMatched", False)
        if (
            tier["matchedNumbers"] == matched_numbers_count
            and tier["letterMatched"] == letter_matched
            and tier_special == special_matched
        ):
            win_amount = float(tier["prizeAmount"])
            break

    return {
        "is_winner": win_amount > 0,
        "win_amount": win_amount
    }