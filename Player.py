from monte_carlo_tree_search import MCTS

with open("data/action_space.pickle", 'rb') as f:
    action_space = pickle.load(f)


class MCTSPlayer:
    """AI player based on MCTS"""

    def __init__(self, policy_value_fn,
                 c_puct=5, n_playout=2000, is_selfplay=0):
        self.mcts = MCTS(policy_value_fn, c_puct, n_playout)
        self.is_selfplay = is_selfplay

    def reset_player(self):
        self.mcts.update_with_move(-1)

    def get_action(self, board, temp=1e-3, return_prob=0):
        sensible_moves = board.possible_moves()
        # the pi vector returned by MCTS as in the alphaGo Zero paper
        move_probs = np.zeros(217)
        if sensible_moves:
            acts, probs = self.mcts.get_move_probs(board, temp)
            move_probs[list(acts)] = probs
            if self.is_selfplay:
                # add Dirichlet Noise for exploration (needed for
                # self-play training)
                move = np.random.choice(
                    acts,
                    p=0.75 * probs + 0.25 *
                      np.random.dirichlet(0.3 * np.ones(len(probs)))
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
            print("WARNING ! Game is over.")


class HumanPlayer:
    def __init__(self):
        pass

    def get_action(self, board):
        while True:
            move = input("Enter your move: ")
            try:
                board.validate(move)
                return move
            except Exception as e:
                print(e)
