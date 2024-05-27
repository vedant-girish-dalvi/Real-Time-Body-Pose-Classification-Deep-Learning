import tensorflow as tf
from keras import layers
from keras.models import Sequential
from keras.layers import LSTM, GRU, Dense
from keras import Model, Input
import logging

logger = logging.getLogger(__name__)

# print(tf.__version__)
# tf.random.set_seed(123)

class RNN:
    """LSTM and GRU model builder class."""
    def __init__(self, input_shape, rnn_type, rnn_units, rnn_layers, dense_units, dense_layers):
        self.input_shape = input_shape
        self.rnn_type = rnn_type
        self.rnn_units = rnn_units
        self.rnn_layers = rnn_layers
        self.dense_units = dense_units
        self.dense_layers = dense_layers

    def build_model(self):
        model = Sequential()
        if self.rnn_layers > 1:
            for layer in range(self.rnn_layers-1):
                model.add(self.rnn_type(self.rnn_units, input_shape=self.input_shape, return_sequences=True))
        model.add(self.rnn_type(self.rnn_units, input_shape=self.input_shape, return_sequences=False))
        for layer in range(self.dense_layers):
            model.add(Dense(self.dense_units, activation='relu'))
        model.add(Dense(5, activation='sigmoid'))
        logging.info("Model created")
        return model

class Transformer:
    """Transformer model builder class."""
    def __init__(self, input_shape, head_size, num_heads, ff_dim, num_transformer_blocks, mlp_units, dropout=0, mlp_dropout=0):
        self.input_shape = input_shape
        self.head_size = head_size
        self.num_heads = num_heads
        self.ff_dim = ff_dim
        self.num_transformer_blocks = num_transformer_blocks
        self.mlp_units = mlp_units
        self.dropout = dropout
        self.mlp_dropout = mlp_dropout

    def transformer_encoder(self, inputs):
        # Attention and Normalization
        x = layers.MultiHeadAttention(
            key_dim=self.head_size, num_heads=self.num_heads, dropout=self.dropout
        )(inputs, inputs)
        x = layers.Dropout(self.dropout)(x)
        x = layers.LayerNormalization(epsilon=1e-6)(x)
        res = x + inputs

        # Feed Forward Part
        x = layers.Conv1D(filters=self.ff_dim, kernel_size=1, activation="relu")(res)
        x = layers.Dropout(self.dropout)(x)
        x = layers.Conv1D(filters=inputs.shape[-1], kernel_size=1)(x)
        x = layers.LayerNormalization(epsilon=1e-6)(x)
        return x + res

    def build_model(self):
        inputs = Input(shape=self.input_shape)
        x = inputs
        for _ in range(self.num_transformer_blocks):
            x = self.transformer_encoder(x)

        x = layers.GlobalAveragePooling1D(data_format="channels_last")(x)
        for dim in self.mlp_units:
            x = layers.Dense(dim, activation="relu")(x)
            x = layers.Dropout(self.mlp_dropout)(x)
        outputs = layers.Dense(5, activation="softmax")(x)
        logging.info("Model created")
        return Model(inputs, outputs)

#RNN class usage:


# lstm_model = RNN((60, 9), LSTM, 16, 4, 8, 2)
# model = lstm_model.build_model()
# model.summary()

# # Transformer Class Usage:
# input_shape = (60, 9)

# transformer = Transformer(
#     input_shape=input_shape,
#     head_size=16,
#     num_heads=3,
#     ff_dim=4,
#     num_transformer_blocks=1,
#     mlp_units=[10],
#     dropout=0.1,
#     mlp_dropout=0.1,
# )

# model = transformer.build_model()
# model.summary()

                