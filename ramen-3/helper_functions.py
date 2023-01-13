from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
import eval7

def verify_win(big_blind, round_num, rounds_remaining, my_bankroll):
    '''
    Function to help verify if you have already theoretically won

    Arguemnts:
    big_blind: A boolean value, representing if you are currently the big blind
    round_num: An integer, the current round
    rounds_remaining: An integer, the number of rounds remaining
    my_bankroll: An integer, representing your current winnings

    Returns:
    A tuple, first element True if you have won, False otherwise, second element
    the bankroll required to win
    '''
    if (big_blind and round_num%2 == 0) or (not big_blind and round_num%2 == 1): #you are A
        pairs_remaining = (rounds_remaining - rounds_remaining%2)//2
        winning_bankroll = 3*pairs_remaining + 2*(round_num%2) + 1
    else: 
        pairs_remaining = (rounds_remaining - rounds_remaining%2)//2
        winning_bankroll = 3*pairs_remaining + (round_num%2) + 1

    if winning_bankroll <= my_bankroll:
        return (True, winning_bankroll)
    return (False, winning_bankroll)

def Check_Fold(legal_actions):
    if CheckAction in legal_actions: 
        return CheckAction()
    return FoldAction()

def Check_Call(legal_actions):
    if CheckAction in legal_actions: 
        return CheckAction()
    return CallAction() 

# def Raise(amount, legal_actions, min_raise, max_raise, my_stack):
