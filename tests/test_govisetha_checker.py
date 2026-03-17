from app.services.govisetha_checker import check_govisetha_ticket

def test_govisetha_super_prize():
    # 4 numbers + letter
    ticket_numbers = ["35", "43", "46", "76"]
    ticket_word = "Y"
    draw_numbers = [35, 43, 46, 76]
    draw_word = "y"
    
    res = check_govisetha_ticket(ticket_numbers, ticket_word, draw_numbers, draw_word)
    assert res["is_winner"] is True
    assert res["win_amount"] == 75031364.0

def test_govisetha_first_prize():
    # 4 numbers + NO letter
    ticket_numbers = ["35", "43", "46", "76"]
    ticket_word = "A"
    draw_numbers = [35, 43, 46, 76]
    draw_word = "y"
    
    res = check_govisetha_ticket(ticket_numbers, ticket_word, draw_numbers, draw_word)
    assert res["is_winner"] is True
    assert res["win_amount"] == 2000000.0

def test_govisetha_eighth_prize():
    # 0 numbers + letter
    ticket_numbers = ["01", "02", "03", "04"]
    ticket_word = "Y"
    draw_numbers = [35, 43, 46, 76]
    draw_word = "y"
    
    res = check_govisetha_ticket(ticket_numbers, ticket_word, draw_numbers, draw_word)
    assert res["is_winner"] is True
    assert res["win_amount"] == 40.0

def test_govisetha_no_prize():
    # 0 numbers + NO letter
    ticket_numbers = ["01", "02", "03", "04"]
    ticket_word = "A"
    draw_numbers = [35, 43, 46, 76]
    draw_word = "y"
    
    res = check_govisetha_ticket(ticket_numbers, ticket_word, draw_numbers, draw_word)
    assert res["is_winner"] is False
    assert res["win_amount"] == 0.0

def test_govisetha_out_of_order_match():
    # Order doesn't matter, non-positional
    ticket_numbers = ["76", "43", "35", "46"]
    ticket_word = "A" # No letter match => 1st prize
    draw_numbers = [35, 43, 46, 76]
    draw_word = "Y"
    
    res = check_govisetha_ticket(ticket_numbers, ticket_word, draw_numbers, draw_word)
    assert res["is_winner"] is True
    assert res["win_amount"] == 2000000.0
