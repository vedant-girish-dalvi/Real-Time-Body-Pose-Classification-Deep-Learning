import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from keras.utils import to_categorical
from pickle import dump
import logging

logger = logging.getLogger(__name__)

features = ["Neck_flexion", "Neck_left-ward_tilt", "Neck_right-ward_rotation", "LeftElbow_flexion", "RightElbow_flexion", "LeftKnee_flexion", "RightKnee_flexion", "Thorax_extension", "Thorax_lateral_flexion_rotation"]

class DataPipeline:
    """Dataset Loading and Processing Pipeline"""
    def __init__(self, data_path, labels_path, features, timesteps=60, step_size=1):
        logging.basicConfig(filename='DataPipeline.log', level=logging.INFO)
        self.dataset_path = data_path
        self.labels_path = labels_path
        self.features = features
        self.timesteps = timesteps
        self.step_size = step_size
    def load_dataset(self):
        self.dataframe = pd.read_csv(self.dataset_path)
        self.dataframe.drop(self.dataframe.columns[-2:], axis=1, inplace=True)
        self.labels_df = pd.read_excel(self.labels_path)
        self.dataframe = self.dataframe[self.features]
    def scale_dataset(self):
        self.scaler = StandardScaler()
        self.dataframe = pd.DataFrame(self.scaler.fit_transform(self.dataframe), columns = self.dataframe.columns, index=self.dataframe.index)
        dump(self.scaler, open('standard_scaler.pkl', 'wb'))     
    def create_sequences(self):
        self.X = [[] for _ in range(9)]
        self.y = []
        for i in range(0, self.dataframe.shape[0] - self.timesteps, self.step_size):
            for j in range(9): 
                self.X[j].append(self.dataframe.iloc[i:i + self.timesteps, j])
        for i in range(0, self.labels_df.shape[0] - self.timesteps, self.step_size):
            self.y.append(self.labels_df.iloc[i + self.timesteps, 0])
        self.X = [np.array(col) for col in self.X]
        self.y = np.array(self.y)
        self.X = np.stack(self.X, axis=2)
    def encode_labels(self):
        encoder = LabelEncoder()
        encoder.fit(self.y)
        self.encoded_Y = encoder.transform(self.y)
        self.Y = to_categorical(self.encoded_Y)
    def split_data(self):
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.Y, test_size=0.2, random_state=1) 
        X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.1, random_state=2)
        return X_train, X_test, y_train, y_test, X_train, X_val, y_train, y_val
    def run_pipeline(self):
        logging.info("Started")
        self.load_dataset()
        self.scale_dataset
        self.create_sequences()
        self.encode_labels()
        logging.info("Finished!")
        return self.split_data()


# Usage:
# dataset_path = r"//home//RUS_CIP//st179677//project//dataset//5 users//mocap dataset.csv"
# labels_path = r"/home/RUS_CIP/st179677/project/dataset/5 users/labels.xlsx"

# pipeline = DataPipeline(dataset_path, labels_path, features)
# X_train, X_test, y_train, y_test, X_train, X_val, y_train, y_val = pipeline.run_pipeline()

# print("X train :", X_train.shape)
# print("y train:", y_train.shape)
# print("X test :", X_test.shape)
# print("y test :", y_test.shape)
# print("X val :", X_val.shape)
# print("y val :", y_val.shape)