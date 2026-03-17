import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

PRIZE_TIERS = [
    {"matchedNumbers": 4, "letterMatched": True, "prizeAmount": 75031364}, 
    {"matchedNumbers": 4, "letterMatched": False, "prizeAmount": 2000000},  
    {"matchedNumbers": 3, "letterMatched": True, "prizeAmount": 250000},    
    {"matchedNumbers": 3, "letterMatched": False, "prizeAmount": 5000},     
    {"matchedNumbers": 2, "letterMatched": True, "prizeAmount": 2000},      
    {"matchedNumbers": 2, "letterMatched": False, "prizeAmount": 200},      
    {"matchedNumbers": 1, "letterMatched": True, "prizeAmount": 200},      
    {"matchedNumbers": 1, "letterMatched": False, "prizeAmount": 40},       
    {"matchedNumbers": 0, "letterMatched": True, "prizeAmount": 40},       
]

def check_govisetha_ticket(
    ticket_numbers: List[str], 
    ticket_letter: Optional[str], 
    draw_numbers: List[int], 
    draw_letter: Optional[str]
) -> dict:
    try:
        t_nums = [int(n) for n in ticket_numbers if str(n).isdigit()]
    except ValueError as e:
        logger.error(f"Error converting ticket numbers to int: {e}")
        return {"is_winner": False, "win_amount": 0.0}

    matched_numbers_count = len(set(t_nums).intersection(set(draw_numbers)))
    
    letter_matched = False
    if ticket_letter and draw_letter:
        letter_matched = (str(ticket_letter).strip().upper() == str(draw_letter).strip().upper())
        
    win_amount = 0.0
    for tier in PRIZE_TIERS:
        if tier["matchedNumbers"] == matched_numbers_count and tier["letterMatched"] == letter_matched:
            win_amount = float(tier["prizeAmount"])
            break
            
    return {
        "is_winner": win_amount > 0,
        "win_amount": win_amount
    }
