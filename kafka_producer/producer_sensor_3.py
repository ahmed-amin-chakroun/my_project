# Directory: kafka_producer/producer_sensor_1.py
import time
from kafka import KafkaProducer
import json
import random

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_sensor_data(sensor_id):
    return {
        'sensor_id': sensor_id,
        'features': [random.random(), random.random(), random.random()]
    }

while True:
    data = generate_sensor_data('sensor_3')
    producer.send('rf-topic', value=data)
    print(f"Sensor 3 sent: {data}")
    time.sleep(1)

