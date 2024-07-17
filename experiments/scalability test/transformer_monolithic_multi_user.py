from time import sleep, time
from kafka import KafkaProducer, KafkaConsumer
import json
from json import dumps
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import os
from tensorflow.keras.models import load_model
import influxdb_client
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import datetime
from pickle import load
from threading import Thread
import psutil
import time

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

topics = ['rokoko-source-mocap01', 'rokoko-source-mocap02', 'rokoko-source-mocap03']
consumers = {
    topic: KafkaConsumer(topic,                 
                         bootstrap_servers='192.168.50.234:29093',
                         group_id='52',
                         auto_offset_reset='latest',      
                         enable_auto_commit=True,           
                         auto_commit_interval_ms=2000,     
                         value_deserializer=lambda x: x.decode('utf-8'))
    for topic in topics
}

current_work_dir = os.getcwd()
MODEL_FILE = fr"{current_work_dir}/94.11_Transformer.h5"
model = load_model(MODEL_FILE)
scaler = load(open(fr'{current_work_dir}/scaler.pkl', 'rb'))

# Global variables for throughput calculation
message_count = 1

def process_data(message):
    data = json.loads(message.value)
    data_df = pd.DataFrame(data, columns=features)
    scaled_data = scaler.transform(data_df)
    data_array = scaled_data.reshape((1, 60, 7))
    return data_array
    
def predict(test_data):
    results = model.predict(test_data)
    results = np.argmax(results, axis=1)
    return results

def save_to_influx(bucket_name, user_prefix, field1, field2, field3, field4, field5, throughput):
    write_api = write_client.write_api(write_options=SYNCHRONOUS)
    current_time = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    json_body = [
        {
            "measurement": "prediction_latency",
            "tags": {},
            "time": current_time,
            "fields": {
                f"{user_prefix}_prediction_value": field1,
                f"{user_prefix}_latency": field2,
                f"{user_prefix}_inference_latency": field3,
                f"{user_prefix}_cpu_usage": field4,
                f"{user_prefix}_memory_usage": field5,
                f"{user_prefix}_throughput": throughput
            }
        }
    ]
    write_api.write(bucket=bucket_name, org="iff", record=json_body)

def consume_messages(consumer, user_prefix):
    global message_count, start_time
    for message in consumer:
        if message.value:
            start_time = time.time()
            start_process_time = time.time()
            data = process_data(message)
            predict_start = time.time()
            results = predict(data)
            predict_time = time.time() - predict_start
            end_process_time = time.time() - start_process_time
            cpu_usage, memory_usage = get_cpu_memory_usage()
            print(f"{datetime.datetime.now().isoformat(sep=' ', timespec='seconds')}: Predicted Class user {user_prefix}: {results}")
            elapsed_time = time.time() - start_time
            throughput = message_count / elapsed_time
            save_to_influx(f"mono_scalability", user_prefix, np.ndarray.item(results), end_process_time, predict_time, cpu_usage, memory_usage, throughput)

threads = []
for idx, (topic, consumer) in enumerate(consumers.items(), start=1):
    user_prefix = f"u{idx}"
    thread = Thread(target=consume_messages, args=(consumer, user_prefix))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()
