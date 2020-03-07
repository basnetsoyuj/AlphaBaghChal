import numpy as np
import copy
from utils import softmax


class Node:
    def __init__(self, parent, prior_prob):
        self.parent = parent
        self.children = {}  # { action -> child node }
        self.n_visits = 0
        self.Q = 0
        self.U = 0
        self.P = prior_prob

    def get_value(self, c_puct):
        """Calculate and return the value for this node.
        It is a combination of leaf evaluations Q, and this node's prior
        adjusted for its visit count, U.
        c_puct: a number in (0, inf) controlling the relative impact of
            value Q, and prior probability P, on this node's score.
        """
        self.U = (c_puct * self.P *
                  np.sqrt(self.parent.n_visits) / (1 + self.n_visits))
        return self.Q + self.U

    def select(self, c_puct):
        """
        Returns the child node with highest Q+U value
        """
        return max(self.children.items(),
                   key=lambda act_node: act_node[1].get_value(c_puct))

    def update(self, leaf_value):
        """
        Update given node value from leaf evaluation.
        leaf_value: the value of subtree evaluation from the current player's
            perspective.
        """
        # Count visit.
        self.n_visits += 1
        # Update Q, a running average of values for all visits.
        self.Q += (leaf_value - self.Q) / self.n_visits

    def update_recursive(self, leaf_value):
        # update() but applied recursively for all ancestors.

        # If it is not root, this node's parent should be updated first.
        if self.parent:
            # negative -> from other's perspective
            self.parent.update_recursive(-leaf_value)
        self.update(leaf_value)

    def expand(self, action_prob):
        """
        Discover new nodes from the current node, based on moves possible and respective action_prob
        action_prob-> a list of tuples of actions and their prior probability according to the policy function.
        """
        for action, prob in action_prob:
            if action not in self.children:
                self.children[action] = Node(self, prob)

    def is_leaf(self):
        """Check if leaf node (i.e. no nodes below this have been expanded)."""
        return self.children == {}

    def is_root(self):
        # Check if node has parent node
        return self.parent is None


class MCTS:
    """An implementation of Monte Carlo Tree Search."""

    def __init__(self, policy_value_fn, c_puct=5, n_playout=10000):
        """
        policy_value_fn: a function that takes in a board state and outputs
            Policy -> a list of (action, probability) tuples
            Value -> a score in [-1, 1](i.e. the expected value of the end game score from the current
            player's perspective) for the current player.
        c_puct: a number in (0, inf) that controls how quickly exploration
            converges to the maximum-value policy. A higher value means
            relying on the prior more.
        """
        self.root = Node(None, 1.0)
        self.policy = policy_value_fn
        self.c_puct = c_puct
        self.n_playout = n_playout

    def playout(self, board):
        """Run a single playout from the root to the leaf, getting a value at
        the leaf and propagating it back through its parents.
        board is modified in-place, so a copy must be provided.
        """
        node = self.root
        while True:
            if node.is_leaf():
                break
            # Greedily select next move.
            action, node = node.select(self.c_puct)
            # pure_move() -> move on the basis of pure movement notation eg:1122
            board.pure_move(action)

        # Check for end of game.
        end = board.is_game_over()
        if not end:
            # Evaluate the leaf using a network which outputs a list of
            # (action, probability) tuples p and also a score v in [-1, 1]
            # for the current player.
            action_probs, leaf_value = self.policy(board)
            node.expand(action_probs)
        else:
            # for end state，return the "true" leaf_value
            winner = board.winner()
            if winner == 0:  # tie
                leaf_value = 0.0
            else:
                leaf_value = (
                    1.0 if winner == board.next_turn else -1.0
                )

        # Update value and visit count of nodes in this traversal.
        node.update_recursive(-leaf_value)

    def get_move_probs(self, board, temp=1e-3):
        """Run all playouts sequentially and return the available actions and
        their corresponding probabilities.
        board: the current game state
        temp: temperature parameter in (0, 1] controls the level of exploration
        """
        for n in range(self.n_playout):
            board_copy = copy.deepcopy(board)
            self.playout(board_copy)

        # calc the move probabilities based on visit counts at the root node
        act_visits = [(act, node.n_visits)
                      for act, node in self.root.children.items()]
        acts, visits = zip(*act_visits)
        act_probs = softmax(np.log(np.array(visits) + 1e-10)*(1/temp))

        return acts, act_probs

    def update_with_move(self, last_move):
        """Step forward in the tree, keeping everything we already know
        about the subtree.
        """
        if last_move in self.root.children:
            self.root = self.root.children[last_move]
            self.root.parent = None
        else:
            self.root = Node(None, 1.0)
