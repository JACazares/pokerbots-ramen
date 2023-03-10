import eval7

def return_probabilities(board, street):
    prob = {}
    for i in range(0, 14):
        for j in range(0, 14):
            prob[(i, j)] = 1

    # remove 2s
    for i in range(1, 10):
        prob[(0, i)] = 0
        prob[(i, 0)] = 0
    
    # remove 3s
    for i in range(5, 10):
        prob[(1, i)] = 0
        prob[(i, 1)] = 0
    
    # remove 4s
    for i in range(7, 10):
        prob[(2, i)] = 0
        prob[(i, 2)] = 0
    
    return prob

# return a list of playable cards, according to a probability table
def get_playable_hole_cards(prob_table, possible_hands):
    deck = eval7.Deck()
    playable = []
    possible_hands=[[eval7.Card(card1), eval7.Card(card2)] for card1, card2 in possible_hands]
    for c in possible_hands:
        if c[0].suit == c[1].suit:
            playable.append([str(c[0]), str(c[1])])
        elif prob_table[(c[0].rank, c[1].rank)] >= 0.5:
            playable.append([str(c[0]), str(c[1])])

    return playable

def get_all_hands(prob_table):
    deck = eval7.Deck()
    all_hands = []
    for c1 in deck:
        for c2 in deck:
            all_hands.append([str(c1), str(c2)])

    return all_hands

#prob_table = return_probabilities([], [])
#print(get_playable_hole_cards(prob_table))
