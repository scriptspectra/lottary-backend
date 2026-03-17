from app.services.lottery_checker import check_lottery_ticket
from app.constants.prizes import DHANA_NIDHANAYA_PRIZES

def test_dhana_super_prize():
    # 4 numbers + letter
    ticket_numbers = ["12", "34", "56", "78"]
    ticket_letter = "Z"
    draw_numbers = [12, 34, 56, 78]
    draw_letter = "z"

    res = check_lottery_ticket(
        ticket_numbers=ticket_numbers,
        ticket_letter=ticket_letter,
        draw_numbers=draw_numbers,
        draw_letter=draw_letter,
        prize_tiers=DHANA_NIDHANAYA_PRIZES
    )

    assert res["is_winner"] is True
    assert res["win_amount"] == 104556873.0


def test_dhana_first_prize_no_letter():
    # 4 numbers, wrong letter
    ticket_numbers = ["12", "34", "56", "78"]
    ticket_letter = "A"
    draw_numbers = [12, 34, 56, 78]
    draw_letter = "Z"

    res = check_lottery_ticket(
        ticket_numbers=ticket_numbers,
        ticket_letter=ticket_letter,
        draw_numbers=draw_numbers,
        draw_letter=draw_letter,
        prize_tiers=DHANA_NIDHANAYA_PRIZES
    )

    assert res["is_winner"] is True
    assert res["win_amount"] == 2000000.0


def test_dhana_lower_prize():
    # 3 numbers + letter
    ticket_numbers = ["12", "34", "56", "99"]
    ticket_letter = "Z"
    draw_numbers = [12, 34, 56, 78]
    draw_letter = "Z"

    res = check_lottery_ticket(
        ticket_numbers=ticket_numbers,
        ticket_letter=ticket_letter,
        draw_numbers=draw_numbers,
        draw_letter=draw_letter,
        prize_tiers=DHANA_NIDHANAYA_PRIZES
    )

    assert res["is_winner"] is True
    assert res["win_amount"] == 250000.0


def test_dhana_no_prize():
    # 0 numbers, wrong letter
    ticket_numbers = ["01", "02", "03", "04"]
    ticket_letter = "A"
    draw_numbers = [12, 34, 56, 78]
    draw_letter = "Z"

    res = check_lottery_ticket(
        ticket_numbers=ticket_numbers,
        ticket_letter=ticket_letter,
        draw_numbers=draw_numbers,
        draw_letter=draw_letter,
        prize_tiers=DHANA_NIDHANAYA_PRIZES
    )

    assert res["is_winner"] is False
    assert res["win_amount"] == 0.0