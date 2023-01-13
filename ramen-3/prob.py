import eval7
import pandas as pd
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
import random

def get_strength(prob_table, hole):
    return prob_table[(hole[0], hole[1])]
    
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

def CheckFold(legal_actions):
    if CheckAction in legal_actions: 
        return CheckAction()
    return FoldAction()

def CheckCall(legal_actions):
    if CheckAction in legal_actions: 
        return CheckAction()
    return CallAction() 

def RaiseRandom(legal_actions, raise_amount):
    pass

def RandomAction(round_state, call_threshold, raise_threshold, raise_amount, active):
    legal_actions=round_state.legal_actions()
    my_stack = round_state.stacks[active]  # the number of chips you have remaining
    if RaiseAction in legal_actions:
            min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
    r=random.random()
    if(r<call_threshold): 
        return CheckFold(legal_actions)  
    elif(r>raise_threshold):
        if RaiseAction in legal_actions:
            q=random.random()
            raise_amount=int(raise_amount+(q-0.5)*raise_amount)
            raise_amount=min(max_raise, raise_amount)
            raise_amount=min(my_stack, raise_amount)
            if(raise_amount<min_raise):
                return CheckCall(legal_actions)
            return RaiseAction(raise_amount)
        return CheckCall(legal_actions) 
    else: 
        return CheckCall(legal_actions)