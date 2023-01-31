from collections import namedtuple
from typing import List, Dict, Tuple
import random
import sys
import numpy as np
import eval7
import copy
from abstraction import *

#                          10,  50, 100, 150, 200, 350
Actions = ['F', 'P', 'C', 'a', 'b', 'c', 'd', 'e', 'f']

class InformationSet():
    def __init__(self):
        self.cumulative_regrets = np.zeros(shape=len(Actions))
        self.strategy_sum = np.zeros(shape=len(Actions))
        self.num_actions = len(Actions)
        self.legal = np.ones(shape=len(Actions))
    
    # def __str__(self):
    #     return "cum reg: " + str(self.cumulative_regrets) + "\nstr sum: " + str(self.strategy_sum)

    def normalize(self, strategy: np.array) -> np.array:
        """Normalize a strategy. If there are no positive regrets,
        use a uniform random strategy"""
        tot_sum = 0
        num_actions = 0
        for i in range(self.num_actions):
            if self.legal[i]:
                tot_sum += strategy[i]
                num_actions += 1

        if tot_sum > 0:
            strategy /= tot_sum
        else:
            for i in range(self.num_actions):
                if not self.legal[i]:
                    strategy[i] = 0
                else:
                    strategy[i] = 1.0 / num_actions
        return strategy

    def get_strategy(self, reach_probability: float) -> np.array:
        """Return regret-matching strategy"""
        strategy = np.maximum(0, self.cumulative_regrets)
        strategy = self.normalize(strategy)

        self.strategy_sum += reach_probability * strategy
        return strategy

    def get_average_strategy(self) -> np.array:
        return self.normalize(self.strategy_sum.copy())

class HistoryNode():
    def __init__(self):
        self.history = ['' for _ in range(20)]
        self.bb = 0
        self.round = 0
        self.hole = []
        self.board = []

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, memo))
        return result
    pass

InfoNode = namedtuple('InfoNode', ['history', 'bb', 'round', 'abstractions'])
# class InfoNode():
#     def __init__(self):
#         self.history = ['' for _ in range(20)]
#         self.bb = 0
#         self.round = 0
#         self.abstraction = 0

#     def __deepcopy__(self, memo):
#         cls = self.__class__
#         result = cls.__new__(cls)
#         memo[id(self)] = result
#         for k, v in self.__dict__.items():
#             setattr(result, k, copy.deepcopy(v, memo))
#         return result
    
#     def __str__(self):
#         return str(self.history) + "\n" + str(self.bb) + "\n" + str(self.round) + "\n" + str(self.abstraction)
#     pass

class Poker():
    @staticmethod
    def is_terminal(actions: HistoryNode, run: int) -> bool:
        # Fold
        if actions.history[actions.round][-1:] == "F":
            return True
        # Double Check
        elif (actions.round-1 == run) and (actions.history[actions.round-1][-2:] == "PP"):
            return True
        # Call
        elif (actions.round-1 == run) and (actions.history[actions.round-1][-1:] == "C"):
            return True
        return False

    @staticmethod
    def get_payoff(actions: HistoryNode, cards: List[str], contributions: np.array) -> int:
        if actions.history[actions.round][-1:] == 'F':
            active_player = 0
            if actions.round == 0:
                if actions.bb == 0:
                    active_player = (len(actions.history[actions.round]) + 1) % 2
                else:
                    active_player = (len(actions.history[actions.round])) % 2 
            else:
                if actions.bb == 0:
                    active_player = (len(actions.history[actions.round])) % 2 
                else:
                    active_player = (len(actions.history[actions.round]) + 1) % 2

            if active_player == actions.bb:
                return min(contributions)
            else:
                return -min(contributions)
        else:
            my_cards = []
            opp_cards = []
            if actions.bb == 0:
                my_cards = cards[:2]
                opp_cards = cards[2:4]
            else:
                my_cards = cards[2:4]
                opp_cards = cards[:2]
            board_cards = cards[4:]
            
            my_cards_eval7 = list(map(eval7.Card, my_cards))
            opp_cards_eval7 = list(map(eval7.Card, opp_cards))
            board_cards_eval7 = list(map(eval7.Card, board_cards))

            my_score = eval7.evaluate(my_cards_eval7 + board_cards_eval7)
            opp_score = eval7.evaluate(opp_cards_eval7 + board_cards_eval7)

            if my_score > opp_score:
                return min(contributions)
            else:
                return -min(contributions)

    @staticmethod
    def raise_bounds(contribution, pips, active):
        '''
        Returns a tuple of the minimum and maximum legal raises.
        '''
        # print(contribution, pips, active)
        continue_cost = pips[1-active] - pips[active]
        max_contribution = min(400 - contribution[active], 400 - contribution[1-active] + continue_cost)
        min_contribution = min(max_contribution, continue_cost + max(continue_cost, 2))
        return (min_contribution, max_contribution)
        # return (pips[active] + min_contribution, pips[active] + max_contribution)
    
    # Actions = ['F', 'P', 'C', 'a', 'b', 'c', 'd', 'e', 'f']
    @staticmethod
    def get_legal_actions(contribution, pips, active):
        '''
        Returns a set which corresponds to the active player's legal moves.
        '''
        legal = [0 for _ in range(9)]
        continue_cost = pips[1-active] - pips[active]
        if continue_cost == 0:
            # we can only raise the stakes if both players can afford it
            bets_allowed = (max(contribution) < 400)
            legal[1] = 1
            if bets_allowed:
                minim, maxim = Poker.raise_bounds(contribution, pips, active)
                # print(minim, maxim)
                if minim <= sum(contribution) and sum(contribution) <= maxim:
                    legal[3] = 1
                if minim <= 2*sum(contribution) and 2*sum(contribution) <= maxim:
                    legal[4] = 1
                if minim <= 3*sum(contribution) and 3*sum(contribution) <= maxim:
                    legal[5] = 1
                # if minim <= 150 and 150 <= maxim:
                #     legal[6] = 1
                # if minim <= 200 and 200 <= maxim:
                #     legal[7] = 1
                # if minim <= 350 and 350 <= maxim:
                #     legal[8] = 1
        else:
            # continue_cost > 0
            # similarly, re-raising is only allowed if both players can afford it
            legal[0] = 1
            legal[2] = 1
            raises_forbidden = (continue_cost == 400 - contribution[active] or 400 - contribution[1-active] == 0)
            if not raises_forbidden:
                minim, maxim = Poker.raise_bounds(contribution, pips, active)
                # print(minim, maxim)
                if minim <= sum(contribution) and sum(contribution) <= maxim:
                    legal[3] = 1
                if minim <= 2*sum(contribution) and 2*sum(contribution) <= maxim:
                    legal[4] = 1
                if minim <= 3*sum(contribution) and 3*sum(contribution) <= maxim:
                    legal[5] = 1
                # if minim <= 150 and 150 <= maxim:
                #     legal[6] = 1
                # if minim <= 200 and 200 <= maxim:
                #     legal[7] = 1
                # if minim <= 350 and 350 <= maxim:
                #     legal[8] = 1
        
        return legal

class CFRTrainer:
    def __init__(self):
        self.infoset_map: Dict[InfoNode, InformationSet] = {}

    def get_information_set(self, actions: HistoryNode) -> InformationSet:
        """add if needed and return"""
        aux = InfoNode(tuple(actions.history), actions.bb, actions.round, get_abstraction(actions.hole, actions.board))
        
        if aux not in self.infoset_map:
            self.infoset_map[aux] = InformationSet()
        return self.infoset_map[aux]
    
    def cfr(self, cards: List[str], actions: HistoryNode, run: int, reach_probabilities: np.array, active_player: int, contributions: np.array, pips: np.array):
        if Poker.is_terminal(actions, run):
            return Poker.get_payoff(actions, cards, contributions)
        
        # print(actions.round, actions.history[actions.round][-3:])

        info_set = self.get_information_set(actions)
        legal = np.array(Poker.get_legal_actions(contributions, pips, active_player))
        info_set.legal = legal

        strategy = info_set.get_strategy(reach_probabilities[active_player])
        opponent = (active_player + 1) % 2
        counterfactual_values = np.zeros(len(Actions))

        # print(legal)
        # print(info_set)
        # print(strategy)

        for ix, action in enumerate(Actions):
            if not legal[ix]:
                continue

            action_probability = strategy[ix]

            # compute new reach probabilities after this action
            new_reach_probabilities = reach_probabilities.copy()
            new_reach_probabilities[active_player] *= action_probability

            aux_contributions = copy.deepcopy(contributions)
            aux_pips = copy.deepcopy(pips)
            if action not in ['F', 'P']:
                aux_contributions[active_player] = aux_contributions[opponent]
                aux_pips[active_player] = aux_pips[opponent]
                if action == 'a':
                    aux_pips[active_player] += sum(contributions)
                    aux_contributions[active_player] += sum(contributions)
                if action == 'b':
                    aux_pips[active_player] += 2*sum(contributions)
                    aux_contributions[active_player] += 2*sum(contributions)
                if action == 'c':
                    aux_pips[active_player] += 3*sum(contributions)
                    aux_contributions[active_player] += 3*sum(contributions)
                if action == 'd':
                    aux_pips[active_player] += 150
                    aux_contributions[active_player] += 150
                if action == 'e':
                    aux_pips[active_player] += 200
                    aux_contributions[active_player] += 200
                if action == 'f':
                    aux_pips[active_player] += 350
                    aux_contributions[active_player] += 350
            
            aux_actions = copy.deepcopy(actions)
            aux_actions.history[aux_actions.round] += action
            # print(aux_actions.history[aux_actions.round][-3:])
            if aux_actions.round == 0:
                if (aux_actions.history[aux_actions.round][-1:] == 'C' and len(aux_actions.history[aux_actions.round]) > 1) \
                    or (aux_actions.history[aux_actions.round][-1:] == 'P'):
                    aux_actions.round = 3
                    aux_actions.board = cards[4: 4 + aux_actions.round]
                    aux_pips = np.zeros(2)
            else:
                if (aux_actions.history[aux_actions.round][-1:] == 'C') or (aux_actions.history[aux_actions.round][-2:] == 'PP'):
                    aux_actions.round += 1
                    aux_actions.board = cards[4: 4 + aux_actions.round]
                    aux_pips = np.zeros(2)
            
            aux_actions.bb = 1 - aux_actions.bb
            if aux_actions.bb == 0:
                aux_actions.hole = copy.deepcopy(cards[0:2])
            else:
                aux_actions.hole = copy.deepcopy(cards[2:4])
            
            # print(aux_contributions, aux_pips)

            # recursively call cfr method, next player to act is the opponent
            counterfactual_values[ix] = -self.cfr(cards, aux_actions, run, new_reach_probabilities, opponent, aux_contributions, aux_pips)
        

        # Value of the current game state is just counterfactual values weighted by action probabilities
        node_value = counterfactual_values.dot(strategy)
        for ix, action in enumerate(Actions):
            if not legal[ix]:
                continue

            info_set.cumulative_regrets[ix] += reach_probabilities[opponent] * (counterfactual_values[ix] - node_value)
        
        strategy = info_set.get_strategy(reach_probabilities[active_player])
        # print(strategy)

        return node_value

    def train(self, num_iterations: int) -> int:
        util = 0
        deck = eval7.Deck()

        deck.cards.remove(eval7.Card('Qh'))
        deck.cards.remove(eval7.Card('Qd'))

        for _ in range(num_iterations):
            deck.shuffle()
            cards = ['Qh', 'Qd']
            cards.extend(list(map(str, deck)))
            
            # Increase the run until the last card is black (river of blood)
            run = 9
            while cards[run - 1][1] == 'd' or cards[run - 1][1] == 'h':
                run += 1

            actions = HistoryNode()
            actions.hole = cards[0:2]
            reach_probabilities = np.ones(2)
            contributions = np.array([1, 2])
            pips = np.array([1, 2])
            # aux = self.get_information_set(actions)
            util += self.cfr(cards[:run], actions, run - 4, reach_probabilities, 0, contributions, pips)
            print(_, cards[:2], cards[2:4], cards[4:run], util)
            # print(aux)
            # print(aux.get_strategy(1, legal=np.ones(9)))
            # print(_, cards[:run], util)

        return util

if __name__ == "__main__":
    if len(sys.argv) < 2:
        num_iterations = 100000
    else:
        num_iterations = int(sys.argv[1])
    np.set_printoptions(precision=2, floatmode='fixed', suppress=True)

    cfr_trainer = CFRTrainer()
    util = cfr_trainer.train(num_iterations)

    print(f"\nRunning Poker chance sampling CFR for {num_iterations} iterations")
    print(f"Computed average game value               : {(util / num_iterations):.3f}\n")

    print(f"History  Bet  Pass")
    it = 1
    for name, info_set in cfr_trainer.infoset_map.items():
        print(f"{name}:    {info_set.get_average_strategy()}")
        if it > 10:
            break
        it += 1