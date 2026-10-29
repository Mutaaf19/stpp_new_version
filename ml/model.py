"""
Stock Price Prediction System — LSTM Model Architecture
Defines and builds the LSTM neural network for stock price prediction.
"""
import numpy as np
import os
import random

# TensorFlow is optional — not available on lightweight deployments (e.g. Vercel)
try:
    import tensorflow as tf
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # Suppress TF warnings

    # === Deterministic Seeds for Reproducible Predictions ===
    SEED = 42
    random.seed(SEED)
    np.random.seed(SEED)
    tf.random.set_seed(SEED)

    from tensorflow.keras.models import Sequential, load_model, Model
    from tensorflow.keras.layers import (
        Input, LSTM, GRU, Conv1D, MaxPooling1D, Flatten, Dense,
        Dropout, BatchNormalization, MultiHeadAttention, Average, Add,
    )
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

    _TF_AVAILABLE = True
except ImportError:
    tf = None
    _TF_AVAILABLE = False



if _TF_AVAILABLE:
    @tf.keras.utils.register_keras_serializable(package="Custom")
    def directional_loss(y_true, y_pred):
        """
        Custom loss function that penalizes directional inaccuracy.
        Uses raw TF ops for maximum compatibility across TF/Keras versions.
        If the predicted sign differs from the true sign, MSE penalty is 5x.
        """
        # Compute MSE manually for compatibility
        mse = tf.reduce_mean(tf.square(y_true - y_pred), axis=-1)
        # Directional penalty: penalize when signs disagree
        sign_match = tf.reduce_mean(tf.cast(y_true * y_pred < 0, tf.float32), axis=-1)
        penalty = 1.0 + 4.0 * sign_match  # ranges from 1.0 (all agree) to 5.0 (all disagree)
        return tf.reduce_mean(mse * penalty)


    def build_ensemble_model(input_shape: tuple, output_steps: int = 1,
                             lstm_units: list = [128, 64], dropout_rate: float = 0.2) -> Model:
        """
        Builds a Hedge-Fund grade Meta-Ensemble using Keras Functional API.
        Branches into 3 models (Attention-LSTM, GRU, Conv1D) and fuses their outputs.
        """
        inputs = Input(shape=input_shape)

        # Branch 1: LSTM with Self-Attention
        lstm_out = LSTM(lstm_units[0], return_sequences=True)(inputs)
        lstm_out = BatchNormalization()(lstm_out)
        attn_out = MultiHeadAttention(num_heads=2, key_dim=32)(lstm_out, lstm_out)
        x1 = Add()([lstm_out, attn_out])
        x1 = LSTM(lstm_units[1], return_sequences=False)(x1)
        x1 = BatchNormalization()(x1)
        x1 = Dropout(dropout_rate)(x1)
        x1 = Dense(64, activation="relu")(x1)
        out1 = Dense(output_steps)(x1)

        # Branch 2: Flow/Momentum (GRU)
        x2 = GRU(lstm_units[0], return_sequences=True)(inputs)
        x2 = BatchNormalization()(x2)
        x2 = GRU(lstm_units[1], return_sequences=False)(x2)
        x2 = BatchNormalization()(x2)
        x2 = Dropout(dropout_rate)(x2)
        x2 = Dense(64, activation="relu")(x2)
        out2 = Dense(output_steps)(x2)

        # Branch 3: Structural Price Geometry (Conv1D)
        x3 = Conv1D(filters=64, kernel_size=3, activation="relu", padding="same")(inputs)
        x3 = MaxPooling1D(pool_size=2)(x3)
        x3 = Conv1D(filters=32, kernel_size=3, activation="relu", padding="same")(x3)
        x3 = Flatten()(x3)
        x3 = BatchNormalization()(x3)
        x3 = Dropout(dropout_rate)(x3)
        x3 = Dense(64, activation="relu")(x3)
        out3 = Dense(output_steps)(x3)

        # Meta Ensemble Fusion
        outputs = Average()([out1, out2, out3])

        model = Model(inputs=inputs, outputs=outputs)
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss=directional_loss,
        )
        return model


    def train_model(model: Model, X_train: np.ndarray, y_train: np.ndarray,
                    epochs: int = 40, batch_size: int = 64,
                    X_val: np.ndarray = None, y_val: np.ndarray = None) -> Model:
        """Train the LSTM model with early stopping and learning rate reduction."""
        callbacks = [
            EarlyStopping(
                monitor="val_loss" if X_val is not None else "loss",
                patience=3,
                restore_best_weights=True,
            ),
            ReduceLROnPlateau(
                monitor="val_loss" if X_val is not None else "loss",
                factor=0.5,
                patience=2,
                min_lr=1e-6,
                verbose=0,
            ),
        ]
        fit_kwargs = dict(epochs=epochs, batch_size=batch_size, callbacks=callbacks, verbose=0)
        if X_val is not None and y_val is not None:
            fit_kwargs["validation_data"] = (X_val, y_val)
        model.fit(X_train, y_train, **fit_kwargs)
        return model


    def tune_and_train_model(X_train, y_train, output_steps, fast_mode=True) -> Model:
        """Build, optionally tune, and train the best LSTM model."""
        input_shape = (X_train.shape[1], X_train.shape[2])
        val_split = int(len(X_train) * 0.85)
        X_t, y_t = X_train[:val_split], y_train[:val_split]
        X_v, y_v = X_train[val_split:], y_train[val_split:]

        if fast_mode:
            model = build_ensemble_model(input_shape, output_steps,
                                         lstm_units=[128, 64], dropout_rate=0.2)
            return train_model(model, X_t, y_t, epochs=40, batch_size=64, X_val=X_v, y_val=y_v)

        best_loss = float("inf")
        best_model = None
        param_grid = [
            {"units": [64, 32, 16], "dropout": 0.2},
            {"units": [128, 64, 32], "dropout": 0.25},
            {"units": [128, 64, 32], "dropout": 0.3},
        ]
        for params in param_grid:
            model = build_ensemble_model(input_shape, output_steps,
                                         lstm_units=params["units"],
                                         dropout_rate=params["dropout"])
            model = train_model(model, X_t, y_t, epochs=30, X_val=X_v, y_val=y_v)
            val_loss = model.evaluate(X_v, y_v, verbose=0)
            if val_loss < best_loss:
                best_loss = val_loss
                best_model = model
        return best_model


    def save_model(model: Model, filepath: str):
        """Save trained model to disk."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        model.save(filepath)


    def load_trained_model(filepath: str) -> Model:
        """Load a previously trained model from disk."""
        if os.path.exists(filepath):
            try:
                return load_model(filepath, custom_objects={"directional_loss": directional_loss})
            except Exception:
                return None
        return None

else:
    # Stubs when TensorFlow is not available (e.g. Vercel)
    def directional_loss(*args, **kwargs):
        raise ImportError("TensorFlow is not installed.")

    def build_ensemble_model(*args, **kwargs):
        raise ImportError("TensorFlow is not installed.")

    def train_model(*args, **kwargs):
        raise ImportError("TensorFlow is not installed.")

    def tune_and_train_model(*args, **kwargs):
        raise ImportError("TensorFlow is not installed.")

    def save_model(*args, **kwargs):
        raise ImportError("TensorFlow is not installed.")

    def load_trained_model(*args, **kwargs):
        return None

