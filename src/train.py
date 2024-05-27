import tensorflow as tf
import os
import datetime
from keras.callbacks import ModelCheckpoint, EarlyStopping
from keras.optimizers import Adam
from data.data_processing import DataPipeline
from visualization.visualization import visualization
from model.model import RNN, Transformer
from keras.layers import LSTM, GRU, Dense

dataset_path = r"//home//RUS_CIP//st179677//project//dataset//5 users//mocap dataset.csv"
labels_path = r"/home/RUS_CIP/st179677/project/dataset/5 users/labels.xlsx"
features = ["Neck_flexion", "Neck_left-ward_tilt", "Neck_right-ward_rotation", "LeftElbow_flexion", "RightElbow_flexion", "LeftKnee_flexion", "RightKnee_flexion", "Thorax_extension", "Thorax_lateral_flexion_rotation"]


# class ModelTrainer:
#     def __init__(self):
        
def main():
    pipeline = DataPipeline(dataset_path, labels_path, features)
    X_train, X_test, y_train, y_test, X_train, X_val, y_train, y_val = pipeline.run_pipeline()

    print("X train :", X_train.shape)
    print("y train:", y_train.shape)
    print("X test :", X_test.shape)
    print("y test :", y_test.shape)
    print("X val :", X_val.shape)
    print("y val :", y_val.shape)

    # Transformer Class Usage:
    input_shape = (60, 9)

    transformer = Transformer(
        input_shape=input_shape,
        head_size=16,
        num_heads=3,
        ff_dim=4,
        num_transformer_blocks=1,
        mlp_units=[10],
        dropout=0.1,
        mlp_dropout=0.1,
    )

    model = transformer.build_model()
    model.summary()

    filepath_1 = '/home/RUS_CIP/st179677/project/model/models/Transformer/transformer_best_model.h5'
    logdir = os.path.join("logs", datetime.datetime.now().strftime("softmax_%Y_%m_%d-%H_%M_%S"))
    tensorboard_callback = tf.keras.callbacks.TensorBoard(logdir, histogram_freq=1)

    checkpoint = ModelCheckpoint(filepath=filepath_1, 
                                monitor='val_accuracy',
                                verbose=1, 
                                save_best_only=True,
                                mode='max')

    early_stopping = EarlyStopping(monitor='val_accuracy', patience=10, verbose=1)

    callbacks_list = [checkpoint, tensorboard_callback, early_stopping] # tf.keras.callbacks.TensorBoard(logdir), hp.KerasCallback(logdir, hparams)]

    adam = Adam(learning_rate=0.0001)
    # chk = ModelCheckpoint('best_model.pkl', monitor='val_acc', save_best_only=True, mode='max', verbose=1)
    model.compile(loss='categorical_crossentropy', optimizer=adam, metrics=['accuracy'])
    history=model.fit(X_train, y_train ,validation_data=([X_val], y_val), epochs=1, callbacks=callbacks_list, batch_size=48)

    visualization(history)


if __name__ == "__main__":
    main()