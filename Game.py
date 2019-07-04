class Game:
    def __init__(self, board):
        self.board = board

    def start_play(self, GoatPlayer, BaghPlayer, show=True):
        """start a game between two players"""
        if show:
            self.board.lightweight_show_board()
        while True:
            player_to_move = GoatPlayer if self.board.next_turn == "G" else BaghPlayer
            move = player_to_move.get_action(self.board)
            self.safe_move(move)
            if show:
                self.board.lightweight_show_board()
            end = self.board.is_game_over()
            if end:
                return self.board.winner()

    def start_self_play(self, player, show=0, temp=1e-3):
        """ start a self-play game using a MCTS player, reuse the search tree,
        and store the self-play data: (state, mcts_probs, z) for training
        """
        states, mcts_probs, value = [], [], []
        while True:
            move, move_probs = player.get_action(self.board,
                                                 temp=temp,
                                                 return_prob=1)
            # store the data
            states.append(self.board.board_repr())
            mcts_probs.append(move_probs)

            # temporarily store 1 for goat move and -1 for bagh
            # later can multiply,ie if goat is winner <value>*1
            # if bagh wins <value>*-1 , if draw *0
            player_index = 1 if self.board.next_turn == "G" else -1
            value.append(player_index)

            # perform a move
            self.board.pure_move(move)
            if show:
                self.board.lightweight_show_board()
            end = self.board.is_game_over()
            if end:
                # winner from the perspective of the current player of each state
                if self.board.winner() == "B":
                    value *= -1
                elif self.board.winner() == 0:
                    value *= 0
                # reset MCTS root node
                player.reset_player()
                return self.board.winner(), zip(states, mcts_probs, value)
