import eval7
import pandas as pd


# return a list of playable cards, according to a probability table
def get_playable_hole_cards(prob_table, possible_hands):
    PLAYABLE_THRESHOLD=0.4

    playable = []
    for c1, c2 in possible_hands:
        if prob_table[(c1, c2)] >= PLAYABLE_THRESHOLD:
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
    print(prob.quantile(0.15))
    # get_playable_hole_cards(prob_table)
