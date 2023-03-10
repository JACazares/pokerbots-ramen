import eval7

# return a list of playable cards, according to a probability table
def get_playable_hole_cards(prob_table, possible_hands):
    playable = []
    for c1, c2 in possible_hands:
        if prob_table[(c1, c2)] >= 0.4:
            playable.append([c1, c2])

    return playable

def get_all_hands(prob_table):
    deck = eval7.Deck()
    all_hands = []
    for c1 in deck:
        for c2 in deck:
            if c1 != c2:
                all_hands.append([str(c1), str(c2)])

    return all_hands

if __name__ == "__main__":
    with open('prob_table.txt') as f:
        hand_data = f.read()
    prob_table = eval(hand_data)

    prob = pd.DataFrame(prob_table.values())
    print(prob.quantile(0.25))
    # get_playable_hole_cards(prob_table)
