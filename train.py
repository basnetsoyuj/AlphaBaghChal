from Game import Game
from Player import MCTSPlayer,MCTSPlayerGreedy
from policy_value_net import PolicyValueNet
from utils import symmetry_board_moves
from config import TrainConfig,TrainGreedyConfig
from queue import deque
import numpy as np
class TrainPipeline():
    def __init__(self, init_model=None):

        # params of the board and the game
        self.game = Game()
        # training params
        self.config=TrainConfig()
        self.greedy_config=TrainGreedyConfig()
        self.data_buffer = deque(maxlen=self.config.buffer_size)
        if init_model:
            # start training from an initial policy-value net
            self.policy_value_net = PolicyValueNet(init_model)
        else:
            # start training from a new policy-value net
            self.policy_value_net = PolicyValueNet()

        self.mcts_player = MCTSPlayer(self.policy_value_net.policy_value_fn,
                                      c_puct=self.config.c_puct,
                                      n_playout=self.config.n_playout,
                                      is_selfplay=1)
        self.mcts_player_greedy = MCTSPlayerGreedy(self.policy_value_net.policy_value_fn,
                                      c_puct=self.greedy_config.c_puct,
                                      n_playout=self.greedy_config.n_playout,
                                      is_selfplay=1)

    def collect_selfplay_data(self, n_games=1):
        """collect self-play data for training"""
        for i in range(n_games):
            winner, play_data = self.game.start_self_play(self.mcts_player,
                                                          temp=self.config.temp
                                                          ,greedy_player=self.mcts_player_greedy,who_greedy="B")
            play_data = list(play_data)
            # augment the data
            play_data = symmetry_board_moves(play_data)
            self.data_buffer.extend(play_data)


    def policy_update(self):
        """update the policy-value net"""
        state_batch = [data[0] for data in self.data_buffer]
        mcts_probs_batch = [data[1] for data in self.data_buffer]
        winner_batch = [data[2] for data in self.data_buffer]
        self.policy_value_net.train(state_batch,mcts_probs_batch,winner_batch,self.config.epochs)
        self.policy_value_net.save_model("model.h5")

    def run(self):
        """run the training pipeline"""
        try:
            self.collect_selfplay_data(self.config.play_batch_size)
            self.policy_update()
        except KeyboardInterrupt:
            print('\n\rquit')
    def summary(self):
        self.policy_value_net.model.summary()


if __name__ == '__main__':
    TrainPipeline().run()
