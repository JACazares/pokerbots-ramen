'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
from prob import *
from montecarlo import *
from helper_functions import *
import eval7
import random

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
        with open('prob_table.txt') as f:
            hand_data = f.read()
        self.prob_table = eval(hand_data)
        self.iwon = False
        self.actions = []
        self.prev_street = 0
        self.diff_phase = False
                
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
        self.prev_street = -1
        self.diff_phase = True

        print(round_num, active)

        (self.iwon, self.winning_bankroll) =\
            verify_win(big_blind, round_num, NUM_ROUNDS - round_num + 1, my_bankroll)

        if self.winning_bankroll > 0:
            self.PLAYABLE_THRESHOLD = max([0.4 + 0.3*my_bankroll/self.winning_bankroll, 0.35])
            self.RAISEABLE_THRESHOLD = max([0.55 + 0.3*my_bankroll/self.winning_bankroll, 0.5])
        else:
            self.PLAYABLE_THRESHOLD = 0.4
            self.RAISEABLE_THRESHOLD = 0.55

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

    def preflop_strategy(self, legal_actions, my_cards, board_cards, my_pip, opp_pip, my_stack,\
                        opp_stack, continue_cost, my_contribution, opp_contribution, min_raise,\
                        max_raise, min_cost, max_cost):
        '''
        Returns an action for the pre-flop phase
        
        Arguments:
        TODO

        Returns:
        One of FoldAction(), CheckAction(), CallAction() or RaiseAction(amount)
        '''

        BAD_PREFLOP_CALL_THRESHOLD = 0.95 
        BAD_PREFLOP_RAISE_THRESHOLD = 0.995
        MED_PREFLOP_RAISE_THRESHOLD = 0.8
        GOOD_PREFLOP_RAISE_THRESHOLD = 0.2

        pot_total = my_contribution+opp_contribution
        p = get_strength(self.prob_table, my_cards)
        if pot_total == 0:
            if p < self.PLAYABLE_THRESHOLD:   #fold bad hands most of the time
                r = random.random()
                if r < BAD_PREFLOP_CALL_THRESHOLD:
                    return Check_Fold(legal_actions)
                elif r > BAD_PREFLOP_RAISE_THRESHOLD:
                    if RaiseAction in legal_actions and (continue_cost == 0 or self.diff_phase):
                        return RaiseAction(min(2*min_raise, max_raise))
                    return Check_Fold(legal_actions) 
                else: 
                    return Check_Call(legal_actions)  
            elif p < self.RAISEABLE_THRESHOLD:  #Call(most of the time) or raise medium hands
                r = random.random()
                if r < MED_PREFLOP_RAISE_THRESHOLD:
                    return Check_Call(legal_actions)
                else:
                    if RaiseAction in legal_actions and (continue_cost == 0 or self.diff_phase):
                        return RaiseAction(min(2*min_raise, max_raise))
                    return Check_Call(legal_actions) 
            else:           #raise (most of the time) or call good hands
                r = random.random()
                if r < GOOD_PREFLOP_RAISE_THRESHOLD:
                    return Check_Call(legal_actions) 
                else:
                    if RaiseAction in legal_actions and (continue_cost == 0 or self.diff_phase):
                        return RaiseAction(min(3*min_raise, max_raise))
                    return Check_Call(legal_actions) 
        else:
            pot_odds = continue_cost/(pot_total + continue_cost)

            if p < pot_odds:
                return Check_Fold(legal_actions)
            else:
                if RaiseAction in legal_actions and (continue_cost == 0 or self.diff_phase):
                    raise_amount = int(((p - pot_odds)**3)*(max_raise - min_raise) + min_raise)
                    raise_amount = min(max_raise, raise_amount)
                    raise_amount =  min(my_stack, raise_amount)
                    if raise_amount < min_raise:
                        return Check_Call(legal_actions)
                    return RaiseAction(raise_amount)
                else: 
                    return Check_Call(legal_actions)

    def flop_strategy(self, legal_actions, my_cards, board_cards, my_pip, opp_pip, my_stack,\
                        opp_stack, continue_cost, my_contribution, opp_contribution, min_raise,\
                        max_raise, min_cost, max_cost):
        '''
        Returns an action for the flop phase
        
        Arguments:
        TODO

        Returns:
        One of FoldAction(), CheckAction(), CallAction() or RaiseAction(amount)
        '''

        p = monte_carlo_sim(my_cards, board_cards, iters=100)
        pot_total = my_contribution+opp_contribution
        pot_odds = continue_cost/(pot_total + continue_cost)

        if p < pot_odds:
            return Check_Fold(legal_actions)
        else:
            if RaiseAction in legal_actions and (continue_cost == 0 or self.diff_phase):
                raise_amount = int(((p - pot_odds)**3)*(max_raise - min_raise) + min_raise)
                raise_amount = min(max_raise, raise_amount)
                raise_amount =  min(my_stack, raise_amount)
                if raise_amount < min_raise:
                    return Check_Call(legal_actions)
                return RaiseAction(raise_amount)
            else: 
                return Check_Call(legal_actions)

    def turn_strategy(self, legal_actions, my_cards, board_cards, my_pip, opp_pip, my_stack,\
                        opp_stack, continue_cost, my_contribution, opp_contribution, min_raise,\
                        max_raise, min_cost, max_cost):
        '''
        Returns an action for the turn phase
        
        Arguments:
        TODO

        Returns:
        One of FoldAction(), CheckAction(), CallAction() or RaiseAction(amount)
        '''

        return self.flop_strategy(legal_actions, my_cards, board_cards, my_pip, opp_pip, my_stack,\
                        opp_stack, continue_cost, my_contribution, opp_contribution, min_raise,\
                        max_raise, min_cost, max_cost)

    def river_strategy(self, legal_actions, my_cards, board_cards, my_pip, opp_pip, my_stack,\
                        opp_stack, continue_cost, my_contribution, opp_contribution, min_raise,\
                        max_raise, min_cost, max_cost):
        '''
        Returns an action for the river phase
        
        Arguments:
        TODO

        Returns:
        One of FoldAction(), CheckAction(), CallAction() or RaiseAction(amount)
        '''

        return self.flop_strategy(legal_actions, my_cards, board_cards, my_pip, opp_pip, my_stack,\
                        opp_stack, continue_cost, my_contribution, opp_contribution, min_raise,\
                        max_raise, min_cost, max_cost)

    def run_strategy(self, legal_actions, my_cards, board_cards, my_pip, opp_pip, my_stack,\
                        opp_stack, continue_cost, my_contribution, opp_contribution, min_raise,\
                        max_raise, min_cost, max_cost):
        '''
        Returns an action for the run phase
        
        Arguments:
        TODO

        Returns:
        One of FoldAction(), CheckAction(), CallAction() or RaiseAction(amount)
        '''

        return self.flop_strategy(legal_actions, my_cards, board_cards, my_pip, opp_pip, my_stack,\
                        opp_stack, continue_cost, my_contribution, opp_contribution, min_raise,\
                        max_raise, min_cost, max_cost)

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
        # Check if theoretical win
        if self.iwon:
            return Check_Fold(legal_actions)

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
        min_raise = 0
        max_raise = 0
        min_cost = 0
        max_cost = 0
        if RaiseAction in legal_actions:
            min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
            min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
            max_cost = max_raise - my_pip  # the cost of a maximum bet/raise
        
        if self.prev_street != street:
            self.diff_phase = True
        else:
            self.diff_phase = False

        action = CallAction()
        # Pre-flop strategy
        if street == 0:
            action = self.preflop_strategy(legal_actions, my_cards, board_cards, my_pip ,opp_pip, my_stack,
                opp_stack, continue_cost, my_contribution, opp_contribution, min_raise, max_raise, min_cost,
                max_cost)
        # Flop strategy
        elif street == 3:
            action = self.flop_strategy(legal_actions, my_cards, board_cards, my_pip ,opp_pip, my_stack,
                opp_stack, continue_cost, my_contribution, opp_contribution, min_raise, max_raise, min_cost,
                max_cost)
        # Turn strategy
        elif street == 4:
            action = self.turn_strategy(legal_actions, my_cards, board_cards, my_pip ,opp_pip, my_stack,
                opp_stack, continue_cost, my_contribution, opp_contribution, min_raise, max_raise, min_cost,
                max_cost)
        # River strategy
        elif street == 5:
            action = self.river_strategy(legal_actions, my_cards, board_cards, my_pip ,opp_pip, my_stack,
                opp_stack, continue_cost, my_contribution, opp_contribution, min_raise, max_raise, min_cost,
                max_cost)
        # Run strategy
        else:
            action = self.run_strategy(legal_actions, my_cards, board_cards, my_pip ,opp_pip, my_stack,
                opp_stack, continue_cost, my_contribution, opp_contribution, min_raise, max_raise, min_cost,
                max_cost)

        self.prev_street = street

        return action

        
if __name__ == '__main__':
    run_bot(Player(), parse_args())
