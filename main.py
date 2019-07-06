from Game import Game
from Player import MCTSPlayer,HumanPlayer
from policy_value_net import PolicyValueNet
game=Game()
bagh=HumanPlayer()
pvnet=PolicyValueNet("models/model.h5")
pvnet_fn=pvnet.policy_value_fn
goat=MCTSPlayer(pvnet_fn,n_playout=800)
game.start_play(goat,bagh)
