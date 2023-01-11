import eval7

def monte_carlo_sim(hole, board=[], iters=100):
    '''
    
    '''
    hole_cards = [eval7.Card(s) for s in hole]
    board_cards = [eval7.Card(s) for s in board]
    strength = 0
    for _ in iters:
        deck = eval7.Deck()
        deck.cards.remove(hole_cards)
        deck.cards.remove(board_cards)
        deck.shuffle()

        opp_cards = deck.deal(2)

        # CHECK THIS
        curr_board_cards = board_cards
        while len(curr_board_cards) < 5:
            curr_board_cards.extend(deck.deal(1))

        while str(curr_board_cards[-1])[1] == 'h' or str(curr_board_cards[-1])[1] == 'd':
            curr_board_cards.extend(deck.deal(1))
        
        my = eval7.evaluate(hole_cards + curr_board_cards)
        opp = eval7.evaluate(opp_cards + curr_board_cards)

        if my > opp:
            strength += 1
        elif my == opp:
            strength += 0.5

    return strength / iters
