# Directory: kafka_producer/updated_producer.py
import time
import sys
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import random

# Use the host-accessible port from our updated docker-compose config
BOOTSTRAP_SERVERS = 'localhost:29092'  # This is the important change
TOPIC_NAME = 'rf-topic'

def generate_sensor_data(sensor_id):
    """Generate random sensor data"""
    return {
        'sensor_id': sensor_id,
        'timestamp': time.time(),
        'features': [random.random(), random.random(), random.random()]
    }

def main():
    print(f"Connecting to Kafka at {BOOTSTRAP_SERVERS}...")
    
    try:
        producer = KafkaProducer(
            bootstrap_servers=BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',
            retries=5,
            retry_backoff_ms=1000,
            request_timeout_ms=30000,
            max_block_ms=30000
        )
        print(f"Successfully connected to Kafka")
    except KafkaError as e:
        print(f"Failed to connect to Kafka: {e}")
        sys.exit(1)
        
    # Start sending data
    count = 0
    while True:
        try:
            data = generate_sensor_data('sensor_2')
            count += 1
            data['message_number'] = count
            
            print(f"Sending message {count}: {data}")
            
            future = producer.send(TOPIC_NAME, value=data)
            record_metadata = future.get(timeout=10)
            
            print(f"Successfully sent: Topic={record_metadata.topic}, "
                  f"Partition={record_metadata.partition}, "
                  f"Offset={record_metadata.offset}")
            
            producer.flush()
            time.sleep(1)
            
        except KafkaError as e:
            print(f"ERROR sending message: {e}")
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("Shutting down producer...")
            producer.close()
            sys.exit(0)

if __name__ == "__main__":
    main()
