from time import sleep
from kafka import KafkaProducer, KafkaConsumer
import json
from json import dumps
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = "0"
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import load_model
# from keras.saving import load_model
import influxdb_client, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import datetime
from pickle import load
from threading import Thread
import psutil

# Function to measure CPU and Memory usage
def get_cpu_memory_usage():
    cpu_usage = psutil.cpu_percent(0)
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent
    memory_usage_mb = memory_usage / (1024 ** 2)  # Convert bytes to MB
    return cpu_usage, memory_usage_mb

features = [
            "Neck_right-ward_rotation", 
            "LeftElbow_flexion", "RightElbow_flexion",
            "LeftKnee_flexion", "RightKnee_flexion", 
            "Thorax_extension", "Thorax_lateral_flexion_rotation"
            ]

# InfluxDB configuration
token = "YmWD6XRRRQjJFpd2Kk1Qe_BbtSrNVNQgjJzmzQAgz0KA_vrTAkwckeED4G-1MpJagvfBobEMlSpzFpfMQrVjnw=="
org = "iff"
url = "http://192.168.50.202:8086"

write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

producer = KafkaProducer(bootstrap_servers=['192.168.50.234:29093'],
                         value_serializer=lambda x: 
                         dumps(x).encode('utf-8'))

consumer = KafkaConsumer(
    'rokoko-source-mocap01',                 
    bootstrap_servers='192.168.50.234:29093',
    group_id='50',
    auto_offset_reset='latest',      
    enable_auto_commit=True,           
    auto_commit_interval_ms=2000,     
    value_deserializer=lambda x: x.decode('utf-8')) 

current_work_dir = os.getcwd()

MODEL_FILE = fr"{current_work_dir}/95.73_gru.h5"

model = load_model(MODEL_FILE)

scaler = load(open(fr'{current_work_dir}/scaler.pkl', 'rb'))

def process_data():
    data = json.loads(message.value)
    data_df = pd.DataFrame(data, columns = features)
    save_features_to_influx("mocap_features", data_df)
    scaled_data = scaler.transform(data_df)
    data_array = scaled_data.reshape((1,60,7))
    return data_array
    
def predict(test_data):
    results = model.predict(test_data)
    results = np.argmax(results, axis=1)
    return results
    # producer.send("monolstm", value=np.ndarray.item(results))

def save_to_influx(bucket_name, field1, field2, field3, field4, field5):
    write_api = write_client.write_api(write_options=SYNCHRONOUS)
    current_time = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    json_body = [
        {
            "measurement": "classification_result",
            "tags": {},
            "time": current_time,
            "fields": {
                "prediction_value": field1,
                "latency": field2,
                "inference_latency":field3,
                "cpu_usage":field4,
                "memory_usage":field5
            }
        }
    ]
    write_api.write(bucket=bucket_name, org="iff", record=json_body)
    # time.sleep(1) # separate points by 1 second

def save_features_to_influx(bucket_name, df):
    json_body = []
    write_api = write_client.write_api(write_options=SYNCHRONOUS)

    for index, row in df.iterrows():
        json_body.append({
            "measurement": "Features",
            "tags": {
                "topic":"rokoko-source-mocap01"  # Optional, add tags if needed
            },
            "time": pd.Timestamp.utcnow().isoformat(),
            "fields": row.to_dict()
        })

    try:
        write_api.write(bucket=bucket_name, org="iff", record=json_body)
        print("Data saved to InfluxDB successfully")
    except Exception as e:
        print(f"InfluxDB Write Error: {e}")

if __name__ == "__main__":
        while True:
            for message in consumer:
                if message != "":
                    start_time = time.time()
                    data = process_data()
                    predict_start = time.time()
                    results = predict(data)
                    predict_time = time.time() - predict_start
                    end_time = time.time() - start_time
                    cpu_usage, memory_usage = get_cpu_memory_usage()
                    print(f"{datetime.datetime.now().isoformat(sep=' ', timespec='seconds')}:Predicted Class: {results}")
                    save_to_influx("mono_gru", np.ndarray.item(results), end_time, predict_time, cpu_usage, memory_usage)


