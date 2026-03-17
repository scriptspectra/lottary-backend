from app.services.lottery_checker import check_lottery_ticket
from app.constants.prizes import GOVISETHA_PRIZES

def test_govisetha_super_prize():
    # 4 numbers + letter
    ticket_numbers = ["35", "43", "46", "76"]
    ticket_letter = "Y"
    draw_numbers = [35, 43, 46, 76]
    draw_letter = "y"

    res = check_lottery_ticket(
        ticket_numbers=ticket_numbers,
        ticket_letter=ticket_letter,
        draw_numbers=draw_numbers,
        draw_letter=draw_letter,
        prize_tiers=GOVISETHA_PRIZES
    )
    
    assert res["is_winner"] is True
    assert res["win_amount"] == 75031364.0


def test_govisetha_first_prize():
    # 4 numbers + NO letter
    ticket_numbers = ["35", "43", "46", "76"]
    ticket_letter = "A"
    draw_numbers = [35, 43, 46, 76]
    draw_letter = "y"

    res = check_lottery_ticket(
        ticket_numbers=ticket_numbers,
        ticket_letter=ticket_letter,
        draw_numbers=draw_numbers,
        draw_letter=draw_letter,
        prize_tiers=GOVISETHA_PRIZES
    )
    
    assert res["is_winner"] is True
    assert res["win_amount"] == 2000000.0


def test_govisetha_eighth_prize():
    # 0 numbers + letter
    ticket_numbers = ["01", "02", "03", "04"]
    ticket_letter = "Y"
    draw_numbers = [35, 43, 46, 76]
    draw_letter = "y"

    res = check_lottery_ticket(
        ticket_numbers=ticket_numbers,
        ticket_letter=ticket_letter,
        draw_numbers=draw_numbers,
        draw_letter=draw_letter,
        prize_tiers=GOVISETHA_PRIZES
    )
    
    assert res["is_winner"] is True
    assert res["win_amount"] == 40.0


def test_govisetha_no_prize():
    # 0 numbers + NO letter
    ticket_numbers = ["01", "02", "03", "04"]
    ticket_letter = "A"
    draw_numbers = [35, 43, 46, 76]
    draw_letter = "y"

    res = check_lottery_ticket(
        ticket_numbers=ticket_numbers,
        ticket_letter=ticket_letter,
        draw_numbers=draw_numbers,
        draw_letter=draw_letter,
        prize_tiers=GOVISETHA_PRIZES
    )
    
    assert res["is_winner"] is False
    assert res["win_amount"] == 0.0


def test_govisetha_out_of_order_match():
    # Order doesn't matter, non-positional
    ticket_numbers = ["76", "43", "35", "46"]
    ticket_letter = "A"  # No letter match => 1st prize
    draw_numbers = [35, 43, 46, 76]
    draw_letter = "Y"

    res = check_lottery_ticket(
        ticket_numbers=ticket_numbers,
        ticket_letter=ticket_letter,
        draw_numbers=draw_numbers,
        draw_letter=draw_letter,
        prize_tiers=GOVISETHA_PRIZES
    )
    
    assert res["is_winner"] is True
    assert res["win_amount"] == 2000000.0