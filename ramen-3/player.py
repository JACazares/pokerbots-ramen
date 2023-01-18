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
import numpy as np

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
        self.opponent_contribution_total=np.array([])
        self.opponent_contribution_we_won =np.array([])
        self.opponent_contribution_they_won =np.array([])
                
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

        # Adjust betting bounds to be more conservative when you're winning
        if big_blind:
            if self.winning_bankroll > 0:
                self.PLAYABLE_THRESHOLD = max([0.4 + 0.3*my_bankroll/self.winning_bankroll, 0.35])
                self.RAISEABLE_THRESHOLD = max([0.55 + 0.3*my_bankroll/self.winning_bankroll, 0.5])
            else:
                self.PLAYABLE_THRESHOLD = 0.4
                self.RAISEABLE_THRESHOLD = 0.55
        else:
            if self.winning_bankroll > 0:
                self.PLAYABLE_THRESHOLD = max([0.45+0.3*my_bankroll/self.winning_bankroll, 0.4])
                self.RAISEABLE_THRESHOLD = max([0.55+0.3*my_bankroll/self.winning_bankroll, 0.5])
            else:
                self.PLAYABLE_THRESHOLD = 0.45
                self.RAISEABLE_THRESHOLD = 0.55
        
        self.opp_std = np.std(self.opponent_contribution_total)
        self.opp_mean = np.mean(self.opponent_contribution_total)

        print(f"Round {round_num}: I have {my_bankroll} and need {self.winning_bankroll} to win")

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

        my_stack = previous_state.stacks[active]
        opp_stack = previous_state.stacks[1-active]
        my_contribution = STARTING_STACK - my_stack
        opp_contribution = STARTING_STACK - opp_stack
        
        '''
        self.opponent_contribution_total = np.append(self.opponent_contribution_total, [opp_contribution])

        if my_delta > 0:
            self.opponent_contribution_we_won = np.append(self.opponent_contribution_total, [opp_contribution])
        elif my_delta < 0:
            self.opponent_contribution_they_won = np.append(self.opponent_contribution_total, [opp_contribution])
        '''
        #test

        # Someone folded
        if opp_cards == []:
            
            pass
        # Got to showdown
        else:
            
            pass
        pass

    # TODO: move all arguments to a class, for easier calling
    def preflop_strategy(self, legal_actions, my_cards, board_cards, my_pip, opp_pip, my_stack,\
                        opp_stack, continue_cost, my_contribution, opp_contribution, min_raise,\
                        max_raise, min_cost, max_cost, big_blind, my_bankroll, round_num):
        '''
        Returns an action for the pre-flop phase
        
        Arguments:
        TODO

        Returns:
        One of FoldAction(), CheckAction(), CallAction() or RaiseAction(amount)
        '''

        # WARNING: MOST NUMBERS ARE ARBITRARY
        # Note: RandomAction(legal_actions, my_stack, min_raise, max_raise,\
        #                    call_threshold, raise_threshold, raise_amount)

        BAD_PREFLOP_CALL_THRESHOLD = 0.95 
        BAD_PREFLOP_RAISE_THRESHOLD = 0.995

        MID_PREFLOP_CALL_THRESHOLD = 0
        MID_PREFLOP_RAISE_THRESHOLD = 0.7

        GOOD_PREFLOP_CALL_THRESHOLD = 0
        GOOD_PREFLOP_RAISE_THRESHOLD = 0.1

        pot_total = my_contribution + opp_contribution
        pot_odds = continue_cost/(pot_total + continue_cost)
        strength = get_strength(self.prob_table, my_cards)
        print(f"     my_strength={strength}")
        print(f"     pot_total={pot_total}")
        print(f"     pot_odds= {pot_odds}")
        print(f"     normalized_pot_odds= {pot_odds+0.1*my_bankroll/self.winning_bankroll}")

        if round_num >= 20:
            std_dev = (continue_cost - self.opp_mean) / self.opp_std
            print(f"std dev is {std_dev}")
            if std_dev > 2.5 and strength <= 0.9:
                print("FOLD because standard deviation was too high")
                return CheckFold(legal_actions)

        # You play first
        if not big_blind:
            if opp_pip == 2:
                print("this")
                # Fold bad hands most of the time
                if strength < self.PLAYABLE_THRESHOLD:
                    return RandomAction(legal_actions, my_stack, min_raise, max_raise,\
                                        0.95,
                                        0.995,
                                        min(2*min_raise, max_raise))

                # Call (most of the time) or raise medium hands
                elif strength < self.RAISEABLE_THRESHOLD:
                    return RandomAction(legal_actions, my_stack, min_raise, max_raise,\
                                        0,
                                        0.7,
                                        min(2*min_raise, max_raise))

                # Raise (most of the time) or call good hands
                else:
                    return RandomAction(legal_actions, my_stack, min_raise, max_raise,\
                                        0,
                                        0.1,
                                        min(2*min_raise, max_raise))
            else:
                # Opponent raised!!
                # TODO: update opponent's range

                if strength < (pot_odds + max(0.1*my_bankroll/self.winning_bankroll, 0)): 
                    return RandomAction(legal_actions, my_stack, min_raise, max_raise,\
                                        0.9, 1, 0)
                elif(strength<0.55):
                    return RandomAction(legal_actions, my_stack, min_raise, max_raise,\
                                        0.7, 1, 0)
                elif(strength<0.75): 
                    return RandomAction(legal_actions, my_stack, min_raise, max_raise,\
                                        0.05, 0.9, min(4*min_raise, max_raise))
                # Strength high enough to raise after a raise
                elif(my_contribution<STARTING_STACK/5):
                    return RandomAction(legal_actions, my_stack, min_raise, max_raise,\
                                        0, 0.5, min(2*min_raise, max_raise))
                else: 
                    return CheckCall(legal_actions)

        # You play second
        else:
            if opp_pip == 2:
                print("that")
                if(strength<self.PLAYABLE_THRESHOLD):
                    return RandomAction(legal_actions, my_stack, min_raise, max_raise,\
                                        0, 0.7, min(4*min_raise, max_raise))
                elif(strength<self.RAISEABLE_THRESHOLD):
                    return RandomAction(legal_actions, my_stack, min_raise, max_raise,\
                                        0, 0.4, min(2*min_raise, max_raise))
                else: 
                    return RandomAction(legal_actions, my_stack, min_raise, max_raise,\
                                        0, 0.6, min(2*min_raise, max_raise))
            else:
                if(strength<pot_odds+max(0.2*my_bankroll/self.winning_bankroll, 0)):
                    return RandomAction(legal_actions, my_stack, min_raise, max_raise,\
                                        0.9, 1, 0)
                elif(strength<0.55):
                    return RandomAction(legal_actions, my_stack, min_raise, max_raise,\
                                        0.7, 1, 0)
                elif(strength<0.75):  
                    return RandomAction(legal_actions, my_stack, min_raise, max_raise,\
                                        0.05, 0.95, min(2*min_raise, max_raise))
                # Strength high enough to raise after a raise
                elif(my_contribution<STARTING_STACK/5):
                    return RandomAction(legal_actions, my_stack, min_raise, max_raise,\
                                        0, 0.5, min(2*min_raise, max_raise))
                else: 
                    return CheckCall(legal_actions)
        
        return CheckFold(legal_actions)
        '''
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
        '''

    def flop_strategy(self, legal_actions, my_cards, board_cards, my_pip, opp_pip, my_stack,\
                        opp_stack, continue_cost, my_contribution, opp_contribution, min_raise,\
                        max_raise, min_cost, max_cost, big_blind, my_bankroll, round_num):
        '''
        Returns an action for the flop phase
        
        Arguments:
        TODO

        Returns:
        One of FoldAction(), CheckAction(), CallAction() or RaiseAction(amount)
        '''
        strength = monte_carlo_sim(my_cards, board_cards, iters=100)
        pot_total = my_contribution+opp_contribution
        pot_odds = continue_cost/(pot_total + continue_cost)
        print(f"     my_strength={strength}")
        print(f"     pot_total={pot_total}")
        print(f"     pot_odds= {pot_odds}")
        print(f"     normalized_pot_odds= {pot_odds+0.1*my_bankroll/self.winning_bankroll}")
        
        if round_num >= 20:
            std_dev = (continue_cost - self.opp_mean) / self.opp_std
            print(f"std dev is {std_dev}")
            if std_dev > 2.5 and strength <= 0.9:
                print("FOLD because standard deviation was too high")
                return CheckFold(legal_actions)

        if big_blind:
            if opp_pip==0:
                if strength<0.5:
                    return RandomAction(legal_actions, my_stack, min_raise, max_raise,\
                                        0, 1-(strength**2)*0.02, min_raise)
                elif strength<0.9:
                    return RandomAction(legal_actions, my_stack, min_raise, max_raise,\
                                        0, 0.8, pot_total)
                else: 
                    return RandomAction(legal_actions, my_stack, min_raise, max_raise,\
                                        0, 0.4, 8*pot_total)
            else:
                if strength<pot_odds+max(0.2*my_bankroll/self.winning_bankroll, 0):
                    return RandomAction(legal_actions, my_stack, min_raise, max_raise,\
                                        0.99, 0.995, min_raise)
                elif strength<0.65:
                    return RandomAction(legal_actions, my_stack, min_raise, max_raise,\
                                        0.7, 1, 0)
                elif strength<0.9:
                    return RandomAction(legal_actions, my_stack, min_raise, max_raise,\
                                        0.05, 0.9, pot_total)
                elif my_pip<STARTING_STACK/4:
                    return RandomAction(legal_actions, my_stack, min_raise, max_raise,\
                                        0, 0.4, 8*pot_total)
                else:
                    return CheckCall(legal_actions)
        else: 
            if opp_pip==0:
                if strength<0.5:
                    return RandomAction(legal_actions, my_stack, min_raise, max_raise,\
                                        0, 1-(strength**2)*0.2, min_raise)
                elif strength<0.75:
                    return RandomAction(legal_actions, my_stack, min_raise, max_raise,\
                                        0, 0.5, pot_total)
                else: 
                    return RandomAction(legal_actions, my_stack, min_raise, max_raise,\
                                        0, 0.3, pot_total)
            else:
                if strength<pot_odds+max(0.2*my_bankroll/self.winning_bankroll, 0):
                    return RandomAction(legal_actions, my_stack, min_raise, max_raise,\
                                        1-(strength**2)*0.01, 1, 2*min_raise)
                elif strength<0.6:
                    return RandomAction(legal_actions, my_stack, min_raise, max_raise,\
                                        0.7, 1, 0)
                elif strength<0.8:
                    return RandomAction(legal_actions, my_stack, min_raise, max_raise,\
                                        0.2, 0.95, pot_total)
                elif my_pip<STARTING_STACK/4:
                    return RandomAction(legal_actions, my_stack, min_raise, max_raise,\
                                        0, 0.5, 8*pot_total)
                else:
                    return CheckCall(legal_actions)

    def turn_strategy(self, legal_actions, my_cards, board_cards, my_pip, opp_pip, my_stack,\
                        opp_stack, continue_cost, my_contribution, opp_contribution, min_raise,\
                        max_raise, min_cost, max_cost, big_blind, my_bankroll, round_num):
        '''
        Returns an action for the turn phase
        
        Arguments:
        TODO

        Returns:
        One of FoldAction(), CheckAction(), CallAction() or RaiseAction(amount)
        '''

        return self.flop_strategy(legal_actions, my_cards, board_cards, my_pip, opp_pip, my_stack,\
                        opp_stack, continue_cost, my_contribution, opp_contribution, min_raise,\
                        max_raise, min_cost, max_cost, big_blind, my_bankroll, round_num)

    def river_strategy(self, legal_actions, my_cards, board_cards, my_pip, opp_pip, my_stack,\
                        opp_stack, continue_cost, my_contribution, opp_contribution, min_raise,\
                        max_raise, min_cost, max_cost, big_blind, my_bankroll, round_num):
        '''
        Returns an action for the river phase
        
        Arguments:
        TODO

        Returns:
        One of FoldAction(), CheckAction(), CallAction() or RaiseAction(amount)
        '''

        return self.flop_strategy(legal_actions, my_cards, board_cards, my_pip, opp_pip, my_stack,\
                        opp_stack, continue_cost, my_contribution, opp_contribution, min_raise,\
                        max_raise, min_cost, max_cost, big_blind, my_bankroll, round_num)

    def run_strategy(self, legal_actions, my_cards, board_cards, my_pip, opp_pip, my_stack,\
                        opp_stack, continue_cost, my_contribution, opp_contribution, min_raise,\
                        max_raise, min_cost, max_cost, big_blind, my_bankroll, round_num):
        '''
        Returns an action for the run phase
        
        Arguments:
        TODO

        Returns:
        One of FoldAction(), CheckAction(), CallAction() or RaiseAction(amount)
        '''

        return self.flop_strategy(legal_actions, my_cards, board_cards, my_pip, opp_pip, my_stack,\
                        opp_stack, continue_cost, my_contribution, opp_contribution, min_raise,\
                        max_raise, min_cost, max_cost, big_blind, my_bankroll, round_num)

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
            return CheckFold(legal_actions)

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
        big_blind = bool(active)
        my_bankroll = game_state.bankroll
        round_num = game_state.round_num
        if RaiseAction in legal_actions:
            min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
            min_cost = min_raise - my_pip  # the cost of a minimum bet/raise
            max_cost = max_raise - my_pip  # the cost of a maximum bet/raise
        
        if continue_cost > 0:
            self.opponent_contribution_total = np.append(self.opponent_contribution_total, [continue_cost])
        
        if self.prev_street != street:
            self.diff_phase = True
        else:
            self.diff_phase = False

        action = CallAction()
        # Pre-flop strategy
        if street == 0:
            print(f"    preflop:")
            action = self.preflop_strategy(legal_actions, my_cards, board_cards, my_pip ,opp_pip, my_stack,
                opp_stack, continue_cost, my_contribution, opp_contribution, min_raise, max_raise, min_cost,
                max_cost, big_blind, my_bankroll, round_num)
        # Flop strategy
        elif street == 3:
            print(f"    flop:")
            action = self.flop_strategy(legal_actions, my_cards, board_cards, my_pip ,opp_pip, my_stack,
                opp_stack, continue_cost, my_contribution, opp_contribution, min_raise, max_raise, min_cost,
                max_cost, big_blind, my_bankroll, round_num)
        # Turn strategy
        elif street == 4:
            print(f"    turn:")
            action = self.turn_strategy(legal_actions, my_cards, board_cards, my_pip ,opp_pip, my_stack,
                opp_stack, continue_cost, my_contribution, opp_contribution, min_raise, max_raise, min_cost,
                max_cost, big_blind, my_bankroll, round_num)
        # River strategy
        elif street == 5:
            print(f"    river:")
            action = self.river_strategy(legal_actions, my_cards, board_cards, my_pip ,opp_pip, my_stack,
                opp_stack, continue_cost, my_contribution, opp_contribution, min_raise, max_raise, min_cost,
                max_cost, big_blind, my_bankroll, round_num)
        # Run strategy
        else:
            print(f"    run:")
            action = self.run_strategy(legal_actions, my_cards, board_cards, my_pip ,opp_pip, my_stack,
                opp_stack, continue_cost, my_contribution, opp_contribution, min_raise, max_raise, min_cost,
                max_cost, big_blind, my_bankroll, round_num)

        self.prev_street = street

        return action

        
if __name__ == '__main__':
    run_bot(Player(), parse_args())
