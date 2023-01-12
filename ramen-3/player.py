'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
from prob import*
from montecarlo import *
import eval7
import random

def CheckFold(legal_actions):
    if CheckAction in legal_actions: 
        return CheckAction()
    return FoldAction()

def CheckCall(legal_actions):
    if CheckAction in legal_actions: 
        return CheckAction()
    return CallAction() 



class Player(Bot):
    '''
    A pokerbot.
    '''

    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        Nothing.

        Returns:
        Nothing.
        hola
        '''
        self.PLAYABLE_THRESHOLD=0.4
        self.RAISEABLE_THRESHOLD=0.55
        self.opp_contribution = 0
        self.my_contribution = 0
        with open('prob_table.txt') as f:
            hand_data = f.read()
        self.prob_table = eval(hand_data)
        self.all_hands = get_all_hands(self.prob_table)
                
    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
        round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        my_cards = round_state.hands[active]  # your cards
        big_blind = bool(active)  # True if you are the big blind
        self.opp_contribution=0
        self.my_contribution=0
        self.iwon=False
        rounds_remaining=NUM_ROUNDS-round_num+1
        if((big_blind and round_num%2==0) or (not big_blind and round_num%2==1)): #you are A
            pairs_remaining=(rounds_remaining-rounds_remaining%2)//2
            if(pairs_remaining*3+2*(round_num%2)<my_bankroll):
                self.iwon=True
        else: 
            pairs_remaining=(rounds_remaining-rounds_remaining%2)//2
            if(pairs_remaining*3+(round_num%2)<my_bankroll):
                self.iwon=True

    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        terminal_state: the TerminalState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        previous_state = terminal_state.previous_state  # RoundState before payoffs
        street = previous_state.street  # int of street representing when this round ended
        my_cards = previous_state.hands[active]  # your cards
        opp_cards = previous_state.hands[1-active]  # opponent's cards or [] if not revealed
        pass

    def get_action(self, game_state, round_state, active):
        '''
        Where the magic happens - your code should implement this function.
        Called any time the engine needs an action from your bot.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Your action.
        '''
        legal_actions = round_state.legal_actions()  # the actions you are allowed to take
        street = round_state.street  # int representing pre-flop, flop, turn, or river respectively
        my_cards = round_state.hands[active]  # your cards
        board_cards = round_state.deck[:street]  # the board cards
        my_pip = round_state.pips[active]  # the number of chips you have contributed to the pot this round of betting
        opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
        my_stack = round_state.stacks[active]  # the number of chips you have remaining
        opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        my_contribution = STARTING_STACK - my_stack  # the number of chips you have contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack  # the number of chips your opponent has contributed to the pot
        if RaiseAction in legal_actions:
            min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
            min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
            max_cost = max_raise - my_pip  # the cost of a maximum bet/raise

        #IWON function: 
        if(self.iwon):
            if(CheckAction in legal_actions):
                return CheckAction()
            return FoldAction()
        
        BAD_PREFLOP_CALL_THRESHOLD=0.95
        BAD_PREFLOP_RAISE_THRESHOLD=0.995
        MED_PREFLOP_RAISE_THRESHOLD=0.8
        GOOD_PREFLOP_RAISE_THRESHOLD=0.2
        #preflop_strategy
        if(street==0):
            strength=get_strength(self.prob_table, my_cards)
            if(strength<self.PLAYABLE_THRESHOLD):   #fold bad hands most of the time
                r=random.random()
                if(r<BAD_PREFLOP_CALL_THRESHOLD): 
                    return CheckFold(legal_actions)  
                elif(r>BAD_PREFLOP_RAISE_THRESHOLD):
                    if RaiseAction in legal_actions:
                        return RaiseAction(min(3*min_raise, max_raise))
                    return CheckFold(legal_actions) 
                else: 
                    return CheckCall(legal_actions)  
            elif(strength<self.RAISEABLE_THRESHOLD):  #Call(most of the time) or raise medium hands
                r=random.random()
                if(r<MED_PREFLOP_RAISE_THRESHOLD):
                    return CheckCall(legal_actions)
                else:
                    if RaiseAction in legal_actions:
                        return RaiseAction(min(3*min_raise, max_raise))
                    return CheckCall(legal_actions) 
            else:           #raise (most of the time) or call good hands
                r=random.random()
                if(r<GOOD_PREFLOP_RAISE_THRESHOLD):
                    return CheckCall(legal_actions) 
                else:
                    if RaiseAction in legal_actions:
                        return RaiseAction(min(3*min_raise, max_raise))
                    return CheckCall(legal_actions) 

        #post flop strategy
        else:
            p=monte_carlo_sim(my_cards, board_cards, iters=1000)
            print(p)
            pot_total=my_contribution+opp_contribution
            pot_odds=continue_cost/(pot_total+continue_cost)
            if(p<pot_odds):
                return FoldAction()
            else:
                if(RaiseAction in legal_actions):
                    raise_amount=int((p-pot_odds)*(max_raise-min_raise)+min_raise)
                    raise_amount=min(max_raise, raise_amount)
                    raise_amount=min(my_stack, raise_amount)
                    if(raise_amount<min_raise):
                        return CheckCall(legal_actions)
                    return RaiseAction(raise_amount)
                else: 
                    return CheckCall(legal_actions)

        
if __name__ == '__main__':
    run_bot(Player(), parse_args())
