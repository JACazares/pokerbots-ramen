'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
from prob import*
import eval7

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
        self.opp_contribution=0
        self.my_contribution=0
        self.prob_table = return_probabilities([], [])
        self.all_hands=get_all_hands()

    def evaluate_p(self, hole, board):
        deck=eval7.Deck()
        hole_card=[eval7.Card(card) for card in hole]
        board_card=[eval7.Card(card) for card in board]
        for card in hole_card:
            deck.cards.remove(card)
        for card in board_card:
            deck.cards.remove(card)
        score=0
        iterations=0
        #can possibly be replaced by opponent's range
        for c1 in deck.cards:
            for c2 in deck.cards:
                if(c1!=c2):
                    iterations+=1
                    my_score=eval7.evaluate(hole_card+board_card)
                    opp_score=eval7.evaluate([c1, c2]+board_card)
                    if(my_score>opp_score):
                        score+=2
                    elif(my_score==opp_score):
                        score+=1
        p=score/iterations
        return p
                
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
        pass

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
        #preflop_strategy   
        if(street==0):
            if CheckAction in legal_actions: #check if possible
                return CheckAction()
            if(my_cards in get_playable_hole_cards(self.prob_table, self.all_hands)):   #call good hands 
                return CallAction()
            return FoldAction()                     #fold bad hands
        else:
            p=self.evaluate_p(my_cards, board_cards)
            pot_total=my_contribution+opp_contribution
            pot_odds=continue_cost/(pot_total+continue_cost)
            if(p<pot_odds):
                return FoldAction()
            else:
                raise_amount=(p-pot_odds)*(max_raise-min_raise)+min_raise
                if(raise_amount<min_raise):
                    if(CheckAction in legal_actions):
                        return CheckAction()
                    return CallAction()
                return RaiseAction(raise_amount)

        
if __name__ == '__main__':
    run_bot(Player(), parse_args())
