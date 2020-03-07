from baghchal.env import Board
import numpy as np
from player import HumanPlayer,MCTSPlayer
from baghchal.lookup_table import action_space
class Game:
    def __init__(self, board=Board()):
        self.board = board

    def start_play(self, GoatPlayer, BaghPlayer, show=True):
        states=[]
        mcts_probs=[]
        value=[]
        """start a game between two players"""
        if show:
            self.board.lightweight_show_board()
        while True:
            player_to_move = GoatPlayer if self.board.next_turn == "G" else BaghPlayer
            states.append(self.board.board_repr())
            player_index = 1 if self.board.next_turn == "G" else -1
            value.append(player_index)
            if player_to_move.__class__==HumanPlayer:
                move = player_to_move.get_action(self.board)
                a=np.zeros(217)
                if len(move)==3:
                    a[action_space[move[1:]]]=1
                else:
                    a[action_space[move[-4:]]]=1
                mcts_probs.append(a)
                self.board.safe_move(move)
            else:
                move, a = player_to_move.get_action(self.board,return_prob=1)
                self.board.pure_move(move)
                mcts_probs.append(a)
            if show:
                self.board.lightweight_show_board()
            end = self.board.is_game_over()
            if end:
                value=np.array(value)
                if self.board.winner() == "B":
                    value *= -1
                elif self.board.winner() == 0:
                    value *= 0
                return zip(states, mcts_probs, value)

    def start_self_play(self, player, show=1, temp=1e-3,greedy_player=None,who_greedy=""):
        """ start a self-play game using a MCTS player, reuse the search tree,
        and store the self-play data: (state, mcts_probs, z) for training
        """
        self.board=Board()
        states, mcts_probs, value = [], [], []
        while True:
            if greedy_player:
                if who_greedy=="B":
                    player_to_move = player if self.board.next_turn == "G" else greedy_player
                elif who_greedy=="G":
                    player_to_move = player if self.board.next_turn == "B" else greedy_player
                else:
                    player_to_move=greedy_player
            else:
                player_to_move = player
            move, move_probs = player_to_move.get_action(self.board,
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
                value=np.array(value)
                # winner from the perspective of the current player of each state
                if self.board.winner() == "B":
                    value *= -1
                elif self.board.winner() == 0:
                    value *= 0
                # reset MCTS root node
                player.reset_player()
                w=self.board.winner()
                return w, zip(states, mcts_probs, value)
