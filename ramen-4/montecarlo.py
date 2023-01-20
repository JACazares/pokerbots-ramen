import eval7
import random 

def monte_carlo_sim(num_range, hole, board=[], iters=1000, opp_range=[1, 2, 3, 4, 5, 6, 7, 8]):
    '''
    
    '''
    hole_cards = [eval7.Card(s) for s in hole]
    board_cards = [eval7.Card(s) for s in board]
    strength = 0
    opp_deck=[]
    for i in opp_range:
        for s in num_range[i]:
            if (s[0] not in hole) and (s[0] not in board) and (s[1] not in hole) and (s[1] not in board):
                opp_deck.append([eval7.Card(s[0]), eval7.Card(s[1])])
    

    for _ in range(iters):
        deck = eval7.Deck()
        for card in hole_cards:
            deck.cards.remove(card)
        for card in board_cards:
            deck.cards.remove(card)
        deck.shuffle()
        opp_cards = random.choice(opp_deck)
        for card in opp_cards:
            print(card)
            deck.cards.remove(card)

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
    deck = eval7.Deck()
    n = len(deck.cards)
    strength = {}
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            strength[(str(deck.cards[i]), str(deck.cards[j]))] = \
                monte_carlo_sim([str(deck.cards[i]), str(deck.cards[j])])
    
    print(strength)
    pass