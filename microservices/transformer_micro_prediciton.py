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
# print(tf.__version__)
import influxdb_client,time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import psutil
import datetime
from threading import Thread

# InfluxDB configuration
token = "YmWD6XRRRQjJFpd2Kk1Qe_BbtSrNVNQgjJzmzQAgz0KA_vrTAkwckeED4G-1MpJagvfBobEMlSpzFpfMQrVjnw=="
org = "iff"
url = "http://192.168.50.202:8086"

current_work_dir = os.getcwd()
# print(current_work_dir)

write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

# Set up Kafka producer
producer = KafkaProducer(bootstrap_servers=['192.168.50.234:29093'],
                         value_serializer=lambda x: json.dumps(x).encode('utf-8'))

# Set up Kafka consumer
consumer = KafkaConsumer(
    'micro_processed_data',                  # Specify the topic name
    bootstrap_servers='192.168.50.234:29093', # Specify the Kafka broker(s)
    group_id='54', # Specify the consumer group ID
    auto_offset_reset='latest',       # Set the offset to the beginning of the topic
    enable_auto_commit=True,            # Enable auto commit offsets
    auto_commit_interval_ms=1000,       # Set auto commit interval (in milliseconds)
    value_deserializer=lambda x: json.loads(x.decode('utf-8')))  # Deserialize the value as UTF-8 string

# Machine learning model configuration
MODEL_FILE = fr"{current_work_dir}/94.11_Transformer.h5"

# Initialize the machine learning model
model = tf.keras.models.load_model(MODEL_FILE)

# Function to measure CPU and Memory usage
def get_cpu_memory_usage():
    cpu_start_time = time.time()
    cpu_usage = psutil.cpu_percent(0)
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent
    memory_usage_mb = memory_usage / (1024 ** 2)  # Convert bytes to MB
    # print(f"cpu_calculation_time={time.time() - cpu_start_time}")
    return cpu_usage, memory_usage_mb

# Function to perform inference using the machine learning model
def predict(test_data):
    # CHECK first convert json back to array
    predict_start = time.time()
    results = model.predict(test_data)
    predict_end = time.time()
    cpu_usage, memory_usage = get_cpu_memory_usage()
    results = np.argmax(results, axis=1)
    print(f"{datetime.datetime.now().isoformat(sep=' ', timespec='seconds')}:Predicted Class: {results}")
    # predict_thread.join()
    end_time = time.time()
    save_to_influx("micro_transformer", np.ndarray.item(results), end_time - start_time, predict_end - predict_start, cpu_usage, memory_usage)

   
# Function to save prediction to InfluxDB
def save_to_influx(bucket_name, field1, field2, field3, field4, field5):
    write_api = write_client.write_api(write_options=SYNCHRONOUS)
    current_time = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    json_body = [
        {
            "measurement": "prediction_latency",
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

def main():
    for message in consumer:
        if message != "":
            global start_time
            start_time = time.time()
            values = message.value
            array = np.array(values, dtype=float)
            predict_thread = Thread(target=predict(array), daemon=True)
            predict_thread.start()
            predict_thread.join()

if __name__ == "__main__":
    main()