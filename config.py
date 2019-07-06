class ModelConfig:
    def __init__(self):
        self.cnn_filter_num = 256
        self.cnn_first_filter_size = 3
        self.cnn_filter_size = 3
        self.resnet_N = 7
        self.l2_reg = 1e-4
        self.value_dense_size = 256

class TrainConfig:
    def __init__(self):
        self.learn_rate = 2e-3
        self.lr_multiplier = 1.0  # adaptively adjust the learning rate based on KL
        self.temp = 1.0  # the temperature param
        self.n_playout = 500  # num of simulations for each move
        self.c_puct = 5
        self.buffer_size = 10000
        self.batch_size = 1  # mini-batch size for training

        self.play_batch_size = 1 # how many games to play
        self.epochs = 3  # num of train_steps for each update
        self.kl_targ = 0.02
        self.check_freq = 50
        self.game_batch_num = 1500

