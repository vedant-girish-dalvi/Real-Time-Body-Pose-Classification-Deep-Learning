import pandas as pd
import numpy as np
import time
import paho.mqtt.client as mqtt
import json
import datetime
import random
from paho.mqtt import client as mqtt_client
from pickle import load

broker = 'broker.hivemq.com'
port = 1883
topic = "mqtt-rokoko03-source"
# Generate a Client ID with the publish prefix.
client_id = f'publish-{random.randint(0, 1000)}'

def generate_new_user_data(dataframe, noise_std, scaling_factor):
    """
    Generate new user data by adding Gaussian noise and scaling the data.

    Parameters:
        dataframe : Dataframe containing the original data.
        noise_std (float): Standard deviation of the Gaussian noise to add.
        scaling_factor (float): Scaling factor to apply to the data.

    Returns:
        pandas.DataFrame: DataFrame containing the new user data.
    """
    original_data = dataframe
    noise = np.random.normal(scale=noise_std, size=original_data.shape)
    noisy_data = original_data + noise
    scaled_data = noisy_data * scaling_factor
    
    return scaled_data

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {rc}\n")

    client = mqtt_client.Client(mqtt.CallbackAPIVersion.VERSION1, client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    try:
        client.connect(broker, port)
    except Exception as e:
        print(f"Error connecting to MQTT broker: {e}")
        raise
    return client

def run():
    global client
    client = connect_mqtt()
    client.loop_start()
    try:
        broadcast_data()
    finally:
        client.loop_stop()

CSV_FILE_PATH = r"C:\Users\vedan\Desktop\data\60 FPS - clipped\user-wise\train\user-5_train.csv" 

features = ["Neck_right-ward_rotation", "LeftElbow_flexion", "RightElbow_flexion", "LeftKnee_flexion", "RightKnee_flexion", "Thorax_extension", "Thorax_lateral_flexion_rotation"]


df = pd.read_csv(CSV_FILE_PATH)
labels_value = df["label"]
df = df[features]

new_user_data = generate_new_user_data(df, noise_std=0.1, scaling_factor=1.01)

# Divide data into blocks of 60 rows
block_size = 60
blocks = []
labels = []
for i in range(0, len(new_user_data), block_size):
    block = new_user_data[i:i+block_size]
    label = labels_value[i:i+block_size]
    if len(block) == block_size:
        blocks.append(block)
    if len(label) == block_size:
        labels.append(label)

# Function to broadcast data
def broadcast_data():
    for block in blocks:
        data = np.array(block)
        payload = json.dumps(data.tolist())
        client.publish(topic, payload)
        print(f"{datetime.datetime.now().isoformat(sep=' ', timespec='seconds')}: Published data to {topic}\n")
        time.sleep(1)

if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        print("Broadcasting stopped")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        client.disconnect()
        print("Disconnected from MQTT broker.")