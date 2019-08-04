import numpy as np
import copy


class Node:
    def __init__(self, parent, prior_prob):
        self.parent = parent
        self.children = {}
        self.prior_prob = prior_prob
        self.W = 0
        self.n_visits = 0

    @property
    def Q(self):
        return self.W / self.n_visits if self.n_visits != 0 else 0

    def get_value(self, cpuct):
        self.U = cpuct * self.prior_prob * \
                 (self.n_visits ** 0.5 / (1 + self.parent.n_visits))
        return self.Q + self.U

    def expand(self, action_prob):
        for action, prob in action_prob:
            if action not in self.children:
                self.children[action] = prob

    def update(self, value):
        self.n_visits += 1
        self.W += value

    def update_ancestors(self, value):
        if self.parent:
            self.parent.update(-value)
        self.update(value)

    def select(self, cpuct):
        return max(self.children.items(),
                   key=lambda act_node: act_node[1].get_value(cpuct))

    def is_leaf(self):
        return self.children == {}

    def is_root(self):
        return self.parent is None


class MCTS:
    def __init__(self, policy_value_fn, cpuct, n_playout):
        self.root = Node(None, 1)
        self.policy = policy_value_fn
        self.cpuct = cpuct
        self.n_playout = n_playout

    def playout(self, board):
        node = self.root
        while True:
            if node.is_leaf():
                break
            action, node = node.select(self.cpuct)
            board.pure_move(action)
        end = board.is_game_over()
        if not end:
            action_probs, leaf_value = self.policy(board)
            node.expand(action_probs)
        else:
            winner = board.winner()
            if winner == 0:  # tie
                leaf_value = 0.0
            else:
                leaf_value = (
                    1 if winner == board.next_turn else -1
                )

        '''-ve because from the parent node's perspective the ,
     leaf node is -leaf_value as we use max while selecting the node.'''
        node.update_recursive(-leaf_value)

        def get_move_probs(self, board, temp=1e-3):

            for _ in range(self.n_playout):
                board_copy = copy.deepcopy(board)
                self.playout(board_copy)

        act_visits = [(act, node.n_visits)
                      for act, node in self.root.children.items()]
        acts, visits = zip(*act_visits)
        act_probs = np.array(visits) ** (1 / temp)
        act_probs = act_probs / sum(act_probs)

        [print(act, f"{node.Q:.3f} {node.n_visits}") for act, node in self.root.children.items()]
        return acts, act_probs

        def update_with_move(self, move):

            if move in self.root.children:
                self.root = self.root.children[move]
                self.root.parent = None
            else:
                self.root = Node(None, 1)
