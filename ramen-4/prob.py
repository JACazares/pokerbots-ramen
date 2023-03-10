import eval7
import pandas as pd

#def get_strength(prob_table, hole):
#    return prob_table[(hole[0], hole[1])]
    
def get_opp_range(hole, board, opp_contribution, ):
    '''
        if opponent calls our bet, we assume they think their p-winning is greater than their pot odds.
        In that case, we update their range accordingly. 

        if opponent raises, we assume they think our pot odds now is greater than their p winning
    '''
    pass

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
