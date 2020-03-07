from game import Game
from player import MCTSPlayer,HumanPlayer
from policy_value_net import PolicyValueNet
from utils import symmetry_board_moves
import os
game=Game()
goat=HumanPlayer()
pvnet=PolicyValueNet("../model.h5")
pvnet_fn=pvnet.policy_value_fn
bagh=MCTSPlayer(pvnet_fn,n_playout=800)
game.start_play(goat,bagh)
