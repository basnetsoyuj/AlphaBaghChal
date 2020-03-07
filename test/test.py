import numpy as np
import copy

def softmax(x):
    probs = np.exp(x - np.max(x))
    probs /= np.sum(probs)
    return probs


class Node:
    def __init__(self, parent, prior_prob):
        self.parent = parent
        self.children = {}  # { action -> child node }
        self.n_visit = 0
        self.Q = 0
        self.U = 0
        self.P = prior_prob

    def get_value(self, c_puct):
        """Calculate and return the value for this node.
        It is a combination of leaf evaluations Q, and this node's prior
        adjusted for its visit count, u.
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
        self.Q += 1.0*(leaf_value - self.Q) / self.n_visits

    def update_recursive(self, leaf_value):
        #update() but applied recursively for all ancestors.
        
        # If it is not root, this node's parent should be updated first.
        if self.parent:
            self.parent.update_recursive(-leaf_value)# negative -> from other's perspective
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
        #Check if node has parent node
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
            board.pure_move(action)#pure_move() -> move on the basis of pure movement notation eg:1122

        # Evaluate the leaf using a network which outputs a list of
        # (action, probability) tuples p and also a score v in [-1, 1]
        # for the current player.
        action_probs, leaf_value = self.policy(board)
        # Check for end of game.
        end = board.is_game_over()
        if not end:
            node.expand(action_probs)
        else:
            # for end state，return the "true" leaf_value
            winner=board.winner()
            if winner == 0:  # tie
                leaf_value = 0.0
            else:
                leaf_value = (
                    1.0 if winner == board.get_current_player() else -1.0
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
        act_probs = softmax(1.0/temp * np.log(np.array(visits) + 1e-10))

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


class MCTSPlayer:
    """AI player based on MCTS"""

    def __init__(self, policy_value_function,
                 c_puct=5, n_playout=2000, is_selfplay=0):
        self.mcts = MCTS(policy_value_function, c_puct, n_playout)
        self.is_selfplay = is_selfplay

    def set_player_ind(self, p):
        self.player = p

    def reset_player(self):
        self.mcts.update_with_move(-1)

    def get_action(self, board, temp=1e-3, return_prob=0):
        sensible_moves = board.availables
        # the pi vector returned by MCTS as in the alphaGo Zero paper
        move_probs = np.zeros(board.width*board.height)
        if len(sensible_moves) > 0:
            acts, probs = self.mcts.get_move_probs(board, temp)
            move_probs[list(acts)] = probs
            if self.is_selfplay:
                # add Dirichlet Noise for exploration (needed for
                # self-play training)
                move = np.random.choice(
                    acts,
                    p=0.75*probs + 0.25*np.random.dirichlet(0.3*np.ones(len(probs)))
                )
                # update the root node and reuse the search tree
                self.mcts.update_with_move(move)
            else:
                # with the default temp=1e-3, it is almost equivalent
                # to choosing the move with the highest prob
                move = np.random.choice(acts, p=probs)
                # reset the root node
                self.mcts.update_with_move(-1)
#                location = board.move_to_location(move)
#                print("AI move: %d,%d\n" % (location[0], location[1]))

            if return_prob:
                return move, move_probs
            else:
                return move
        else:
            print("WARNING: the board is full")

    def __str__(self):
        return "MCTS {}".format(self.player)
