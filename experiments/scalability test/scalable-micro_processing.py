from time import time, sleep
import json
from kafka import KafkaProducer, KafkaConsumer
import numpy as np
import pandas as pd
import os
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow import keras
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from pickle import load
import threading
import datetime
import logging
import time

# InfluxDB configuration
token = "YmWD6XRRRQjJFpd2Kk1Qe_BbtSrNVNQgjJzmzQAgz0KA_vrTAkwckeED4G-1MpJagvfBobEMlSpzFpfMQrVjnw=="
org = "iff"
url = "http://192.168.50.202:8086"

write_client = InfluxDBClient(url=url, token=token, org=org)

producer = KafkaProducer(
    bootstrap_servers=['192.168.50.234:29093'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

# Kafka consumer setup
topics = ['rokoko-source-mocap01', 'rokoko-source-mocap02', 'rokoko-source-mocap03']

consumers = []
for topic in topics:
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers='192.168.50.234:29093',
        group_id='my_group',
        auto_offset_reset='latest',
        enable_auto_commit=True,
        value_deserializer=lambda x: x.decode('utf-8')
    )
    consumers.append(consumer)


    current_work_dir = os.getcwd()
scaler = load(open(f'{current_work_dir}/scaler.pkl', 'rb'))
features = ["Neck_right-ward_rotation", "LeftElbow_flexion", "RightElbow_flexion", "LeftKnee_flexion", "RightKnee_flexion", "Thorax_extension", "Thorax_lateral_flexion_rotation"]

def save_to_influx(bucket_name, topic_name, latency, data_throughput):
    write_api = write_client.write_api(write_options=SYNCHRONOUS)
    current_time = datetime.datetime.utcnow().isoformat()
    if topic_name == "rokoko-source-mocap01":
        user_prefix = "u1"
    elif topic_name == "rokoko-source-mocap02":
        user_prefix = "u2"
    else:
        user_prefix = "u3"
    json_body = [
        {
            "measurement": "data_processing_latency",
            "time": current_time,
            "fields": {
                f"{user_prefix}_data_processing_latency": latency,
                "data_throughput": data_throughput
            }
        }
    ]
    write_api.write(bucket=bucket_name, org=org, record=json_body)

# Global variables for throughput calculation
message_count = 1

def process_data(consumer, producer, topic_name, bucket_name):
    while True:
        global message_count, start_through_time
        for message in consumer:
            start_time = time.time()
            start_through_time = time.time()
            data = json.loads(message.value)
            data_df = pd.DataFrame(data, columns=features)
            scaled_data = scaler.transform(data_df)
            data_array = scaled_data.reshape((1, 60, 7))
            serialized_data = data_array.tolist()
            producer.send(f"{topic_name}_processed", value=serialized_data)
            elapsed_time = time.time() - start_through_time
            throughput = message_count / elapsed_time
            # print(f"Throughput: {throughput:.2f} messages per second")
            end_time = time.time()
            save_to_influx(bucket_name, topic_name, end_time - start_time, throughput)
            print(f"{datetime.datetime.now().isoformat(sep=' ', timespec='seconds')}: Data Processed for {topic_name}")

threads = []
for i, consumer in enumerate(consumers):
    topic_name = topics[i]
    bucket_name = f"micro_scalability"
    thread = threading.Thread(target=process_data, args=(consumer, producer, topic_name, bucket_name))
    thread.start()
    threads.append(thread)

# Wait for all threads to complete
for thread in threads:
    thread.join()

