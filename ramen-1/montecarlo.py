import eval7

def monte_carlo_sim(hole, board=[], iters=5000):
    '''
    
    '''
    hole_cards = [eval7.Card(s) for s in hole]
    board_cards = [eval7.Card(s) for s in board]
    strength = 0
    for _ in range(iters):
        deck = eval7.Deck()
        for card in hole_cards:
            deck.cards.remove(card)
        for card in board_cards:
            deck.cards.remove(card)
        deck.shuffle()
        opp_cards = deck.deal(2)

        # CHECK THIS
        curr_board_cards = board_cards.copy()
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

if __name__ == "__main__":
    strong_hand = ["As", "Ah"]
    mid_hand = ["Ad", "4d"]
    weak_hand_red = ["2d", "9d"]
    weak_hand_black = ["2s", "9s"]

    print(f'With a strong     hand, strength= {monte_carlo_sim(strong_hand)}')
    print(f'With a mid        hand, strength= {monte_carlo_sim(mid_hand)}')
    print(f'With a weak RED   hand, strength= {monte_carlo_sim(weak_hand_red)}')
    print(f'With a weak BLACK hand, strength= {monte_carlo_sim(weak_hand_black)}')