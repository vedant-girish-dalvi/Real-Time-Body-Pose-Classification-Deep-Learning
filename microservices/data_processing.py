from time import sleep
from kafka import KafkaProducer, KafkaConsumer
import json
from json import dumps
import numpy as np
import pandas as pd
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow import keras
import influxdb_client, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import datetime
from pickle import load
import logging

# InfluxDB configuration
token = "YmWD6XRRRQjJFpd2Kk1Qe_BbtSrNVNQgjJzmzQAgz0KA_vrTAkwckeED4G-1MpJagvfBobEMlSpzFpfMQrVjnw=="
org = "iff"
url = "http://192.168.50.202:8086"

features = ["Neck_right-ward_rotation", "LeftElbow_flexion", "RightElbow_flexion", "LeftKnee_flexion", "RightKnee_flexion", "Thorax_extension", "Thorax_lateral_flexion_rotation"]
current_work_dir = os.getcwd()

write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

# Set up Kafka producer
producer = KafkaProducer(bootstrap_servers=['192.168.50.234:29093'],
                         value_serializer=lambda x: json.dumps(x).encode('utf-8'))

# Set up Kafka consumer
consumer = KafkaConsumer(
    'rokoko-source-mocap01',                  # Specify the topic name
    bootstrap_servers='192.168.50.234:29093', # Specify the Kafka broker(s)
    group_id='49', # Specify the consumer group ID
    auto_offset_reset='latest',       # Set the offset to the beginning of the topic
    enable_auto_commit=True,            # Enable auto commit offsets
    auto_commit_interval_ms=1000,       # Set auto commit interval (in milliseconds)
    value_deserializer=lambda x: x.decode('utf-8'))  # Deserialize the value as UTF-8 string

# Create 9 empty lists with names X1 to X9
x0, x1, x2, x3, x4, x5, x6 = ([] for _ in range(7))

scaler = load(open(fr'{current_work_dir}/scaler.pkl', 'rb'))
# print(scaler)

# Function to save prediction to InfluxDB
def save_to_influx(bucket_name, latency):
    write_api = write_client.write_api(write_options=SYNCHRONOUS)

    # Get current time
    current_time = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    
    # Define data point
    json_body = [
        {
            "measurement": "data_processing_latency",
            "tags": {},
            "time": current_time,
            "fields": {
                "data_processing_latency": latency
            }
        }
    ]

    write_api.write(bucket=bucket_name, org="iff", record=json_body)
    # time.sleep(1) # separate points by 1 second          

# Function to process the incoming data
def process_data():
    # Parse and preprocess the data as needed
    # Start consuming messages
    df = pd.DataFrame()
    while True:
        for message in consumer:
            if message != "":
                global start_time
                start_time = time.time()
                data = json.loads(message.value)
                # print(data)
                data_df = pd.DataFrame(data, columns = features)
                scaled_data = scaler.transform(data_df)
                data_array = scaled_data.reshape((1,60,7))
                # df = pd.concat([df, data_df])
                # df.to_csv(r"C:\Users\vedan\Desktop\DATA.csv")
                # Serialize the array to JSON
                serialized_data = data_array.tolist()
                end_time = time.time()                
                # Send the serialized data to Kafka topic
                producer.send("micro_processed_data", value=serialized_data)
                save_to_influx("micro_data_processing", end_time - start_time)
                print(f"{datetime.datetime.now().isoformat(sep=' ', timespec='seconds')}:Data Processed")
                # print(serialized_data)

if __name__ == "__main__":
    process_data()