from keras import backend as K
from keras import layers, models, optimizers


# 评论者模型
class Critic:
    """Critic (Value) Model."""

    def __init__(self, state_size, action_size, num_units=32):
        """Initialize parameters and build model.
        Params
        ======
            state_size (int): Dimension of each state
            action_size (int): Dimension of each action
            num_units (int): Number of units per layer
        """
        self.state_size = state_size
        self.action_size = action_size

        # Initialize any other variables here
        self.num_units = num_units

        self.build_model()

    def build_model(self):
        """Build a critic (value) network that maps (state, action) pairs -> Q-values."""

        # Define input layers
        states = layers.Input(shape=(self.state_size,), name='states')
        actions = layers.Input(shape=(self.action_size,), name='actions')

        # Try different layer sizes, activations, add batch normalization, regularizers, etc.

        # Add hidden layer(s) for state pathway
        net_states = layers.Dense(units=self.num_units, activation='relu')(states)
        net_states = layers.BatchNormalization()(net_states)
        net_states = layers.Dropout(0.5)(net_states)
        net_states = layers.Dense(units=self.num_units * 2, activation='relu')(net_states)
        net_states = layers.BatchNormalization()(net_states)
        net_states = layers.Dropout(0.5)(net_states)
        net_states = layers.Dense(units=self.num_units, activation='relu')(net_states)
        net_states = layers.BatchNormalization()(net_states)
        net_states = layers.Dropout(0.5)(net_states)

        # Add hidden layer(s) for action pathway
        net_actions = layers.Dense(units=self.num_units, activation='relu')(actions)
        net_actions = layers.BatchNormalization()(net_actions)
        net_actions = layers.Dropout(0.5)(net_actions)
        net_actions = layers.Dense(units=self.num_units * 2, activation='relu')(net_actions)
        net_actions = layers.BatchNormalization()(net_actions)
        net_actions = layers.Dropout(0.5)(net_actions)
        net_actions = layers.Dense(units=self.num_units, activation='relu')(net_actions)
        net_actions = layers.BatchNormalization()(net_actions)
        net_actions = layers.Dropout(0.5)(net_actions)

        # Combine state and action pathways
        net = layers.Add()([net_states, net_actions])
        net = layers.Activation('relu')(net)

        # Add final output layer to prduce action values (Q values)
        Q_values = layers.Dense(units=1, name='q_values')(net)

        # Create Keras model
        self.model = models.Model(inputs=[states, actions], outputs=Q_values)

        # Define optimizer and compile model for training with built-in loss function
        optimizer = optimizers.Adam(lr=0.001)  # learning rate, normal setting is actor lr=0.0001, critic lr=0.001
        self.model.compile(optimizer=optimizer, loss='mse')

        # Compute action gradients (derivative of Q values w.r.t. to actions)
        action_gradients = K.gradients(Q_values, actions)

        # Define an additional function to fetch action gradients (to be used by actor model)
        self.get_action_gradients = K.function(
            inputs=[*self.model.input, K.learning_phase()],
			outputs=action_gradients)