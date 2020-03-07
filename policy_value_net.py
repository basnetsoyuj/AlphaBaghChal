from keras import Input, Model
from keras.layers import Dense, Flatten, Conv2D, BatchNormalization, Add, Activation
from keras.regularizers import l2
from keras.optimizers import Adam
from keras.models import load_model
from config import ModelConfig
from utils import mask_illegal
import numpy as np
from baghchal.lookup_table import action_list
action_list=np.array(action_list)

class PolicyValueNet:
    def __init__(self, model_file=None):
        self.config = ModelConfig()

        if model_file:
            self.model = load_model(model_file, compile=True)
        else:
            self.create()
            self.loss_train_op()

    def create(self):

        in_x = x = Input((5, 5, 5))

        # (batch, channels, height, width)
        x = Conv2D(filters=self.config.cnn_first_filter_num, kernel_size=self.config.cnn_first_filter_size, padding="same",
                   data_format="channels_first", use_bias=False, kernel_regularizer=l2(self.config.l2_reg),
                   name=f"input1_conv-{self.config.cnn_filter_num}-{self.config.cnn_first_filter_size}x{self.config.cnn_first_filter_size}")(
            x)
        x = Conv2D(filters=self.config.cnn_filter_num, kernel_size=self.config.cnn_first_filter_size, padding="same",
                   data_format="channels_first", use_bias=False, kernel_regularizer=l2(self.config.l2_reg),
                   name=f"input_conv-{self.config.cnn_filter_num}-{self.config.cnn_first_filter_size}x{self.config.cnn_first_filter_size}")(
            x)
        x = BatchNormalization(axis=1, name="input_batchnorm")(x)
        x = Activation("relu", name="input_relu")(x)

        for i in range(self.config.resnet_N):
            x = self.build_residual_block(x, i + 1)

        res_out = x

        # for policy output
        x = Conv2D(filters=4, kernel_size=1, data_format="channels_first", use_bias=False,
                   kernel_regularizer=l2(self.config.l2_reg), name="policy_conv-4-1x1")(res_out)
        x = BatchNormalization(axis=1, name="policy_batchnorm")(x)
        x = Activation("relu", name="policy_relu")(x)
        x = Flatten(name="policy_flatten")(x)
        ''' For action policy network output, BaghChal has 217 moves possible at any time period
         (For more: lookup_table.py ->action_space)'''
        policy_out = Dense(217, kernel_regularizer=l2(
            self.config.l2_reg), activation="softmax", name="policy_out")(x)

        # for value output
        x = Conv2D(filters=2, kernel_size=1, data_format="channels_first", use_bias=False,
                   kernel_regularizer=l2(self.config.l2_reg), name="value_conv-2-1x1")(res_out)
        x = BatchNormalization(axis=1, name="value_batchnorm")(x)
        x = Activation("relu", name="value_relu")(x)
        x = Flatten(name="value_flatten")(x)
        x = Dense(self.config.value_dense_size, kernel_regularizer=l2(
            self.config.l2_reg), activation="relu", name="value_dense")(x)
        value_out = Dense(1, kernel_regularizer=l2(
            self.config.l2_reg), activation="tanh", name="value_out")(x)

        self.model = Model(
            in_x, [policy_out, value_out], name="BaghChal_model")

    def build_residual_block(self, x, index):
        in_x = x
        res_name = "resnet" + str(index)
        x = Conv2D(filters=self.config.cnn_filter_num, kernel_size=self.config.cnn_filter_size, padding="same",
                   data_format="channels_first", use_bias=False, kernel_regularizer=l2(self.config.l2_reg),
                   name=f"{res_name}_conv1-{self.config.cnn_filter_num}-{self.config.cnn_filter_size}x{self.config.cnn_filter_size}")(
            x)
        x = BatchNormalization(axis=1, name=f"{res_name}_batchnorm1")(x)
        x = Activation("relu", name=f"{res_name}_relu1")(x)
        x = Conv2D(filters=self.config.cnn_filter_num, kernel_size=self.config.cnn_filter_size, padding="same",
                   data_format="channels_first", use_bias=False, kernel_regularizer=l2(self.config.l2_reg),
                   name=f"{res_name}_conv2-{self.config.cnn_filter_num}-{self.config.cnn_filter_size}x{self.config.cnn_filter_size}")(
            x)
        x = BatchNormalization(axis=1, name=f"{res_name}_batchnorm2")(x)
        x = Add(name=f"{res_name}_add")([in_x, x])
        x = Activation("relu", name=f"{res_name}_relu2")(x)
        return x

    def policy_value(self, state_input):
        state_input = np.array(state_input)  # _on_batch(state_input_union)
        results = self.model.predict(state_input)
        return results

    def policy_value_fn(self, board):
        """
        input: board
        output: a list of (action, probability) tuples for each available action and the score of the board state
        """
        legal_positions = board.possible_moves_vector()
        act_probs_raw, value = self.policy_value(np.expand_dims(board.board_repr(),0))
        act_probs_raw = mask_illegal(act_probs_raw[0], legal_positions)
        index_list=np.where(legal_positions == 1)[0]
        actions=action_list[index_list]
        act_probs=act_probs_raw[index_list]
        return zip(actions,act_probs), value[0][0]

    def loss_train_op(self):
        """
        Three loss terms：
        loss = (z - v)^2 + pi^T * log(p) + c||theta||^2
        """
        # get the train op
        opt = Adam()
        losses = ['categorical_crossentropy', 'mean_squared_error']
        self.model.compile(optimizer=opt, loss=losses)

    def save_model(self, model_filename):
        """ save model to file """
        self.model.save(f"models/{model_filename}")

    def train(self,board_repr,mtcs_prob,winner,epochs):
        board_repr = np.array(board_repr)
        mtcs_prob = np.array(mtcs_prob)
        winner = np.array(winner)
        self.model.fit(board_repr, [mtcs_prob, winner],epochs=epochs)

