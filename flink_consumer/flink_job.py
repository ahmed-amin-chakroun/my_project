
"""
# Directory: flink_consumer/flink_job.py
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common import WatermarkStrategy, Duration
import json
import requests
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger("flink-rf-job")

# Triton server URL - using the Docker container's service name if running in the same network
TRITON_URL = "http://localhost:8000/v2/models/dummy_model/infer"

def infer_from_triton(features):

    try:
        # Package the data for Triton
        inputs = {
            "inputs": [{
                "name": "input",
                "shape": [1, len(features)],
                "datatype": "FP32",
                "data": features
            }]
        }
        
        # Log the request
        logger.info(f"Sending request to Triton: {inputs}")
        
        # Send request with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(TRITON_URL, json=inputs, timeout=5)
                response.raise_for_status()  # Raise exception for non-200 status codes
                result = response.json()
                logger.info(f"Received response from Triton: {result}")
                return result
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Triton request failed (attempt {attempt+1}/{max_retries}): {e}")
                    time.sleep(1)  # Wait before retrying
                else:
                    logger.error(f"Triton request failed after {max_retries} attempts: {e}")
                    return {"error": str(e)}
    except Exception as e:
        logger.error(f"Error in inference: {e}")
        return {"error": str(e)}

def flink_job():

    try:
        # Create execution environment
        env = StreamExecutionEnvironment.get_execution_environment()
        env.set_parallelism(1)  # Set to 1 for easier debugging
        
        # Add required Kafka connector JAR files
        # Make sure these JAR files exist at the specified locations
        env.add_jars("file:///home/ahmed/my_project/lib/flink-connector-kafka-3.0.1-1.17.jar")
        env.add_jars("file:///home/ahmed/my_project/lib/kafka-clients-3.0.1.jar")
        
        # Configure checkpoint interval (optional, for fault tolerance)
        env.enable_checkpointing(60000)  # 60 seconds
        
        # Create Kafka source - use kafka:9092 if running in Docker network, or localhost:29092 if from host
        # Important: With your Docker setup, you need the right bootstrap server here
        source = KafkaSource.builder() \
            .set_bootstrap_servers("kafka:9092") \
            .set_topics("rf-topic") \
            .set_group_id("flink-group") \
            .set_starting_offsets(KafkaOffsetsInitializer.earliest()) \
            .set_value_only_deserializer(SimpleStringSchema()) \
            .build()
        
        # Create data stream from Kafka source
        ds = env.from_source(
            source,
            WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_seconds(5)),
            source_name="KafkaSource"
        )
        
        # Process incoming data
        def process_data(value):
            try:
                # Parse the JSON message
                data = json.loads(value)
                logger.info(f"Processing message: {data}")
                
                # Extract features and send to Triton
                features = data.get("features", [])
                result = infer_from_triton(features)
                
                # Log results
                logger.info(f"Sensor {data.get('sensor_id')} -> Features: {features} -> Prediction: {result}")
                return True
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                return False
        ds = ds.map(lambda v: logger.info(f"RAW MESSAGE: {v}") or v).name("Log-Raw-Messages")
        # Apply processing function to the stream
        ds.map(process_data).name("RF-Processing")
        
        # Execute the Flink job
        logger.info("Starting Flink job...")
        env.execute("RF Sensor Inference Job")
        
    except Exception as e:
        logger.error(f"Error in Flink job: {e}")
        raise
if __name__ == "__main__":
    try:
        logger.info("Initializing RF sensor processing job...")
        flink_job()
    except KeyboardInterrupt:
        logger.info("Job interrupted by user")
    except Exception as e:
        logger.error(f"Job failed: {e}")
        """
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common import Duration, WatermarkStrategy
import json
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("kafka-flink-consumer")

def main():
    # Create execution environment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    
    # Add required JAR files - use relative paths or environment variables
    # These paths should be available in your Flink container
    current_dir = os.path.dirname(os.path.realpath(__file__))
    
    # Option 1: If running from within Docker container with mounted volumes
    kafka_connector_jar = "file:///opt/flink/lib/flink-connector-kafka-3.0.1-1.17.jar"
    kafka_clients_jar = "file:///opt/flink/lib/kafka-clients-3.0.1.jar"
    
    # Option 2: If using relative paths
    # kafka_connector_jar = f"file://{current_dir}/lib/flink-connector-kafka-3.0.1-1.17.jar"
    # kafka_clients_jar = f"file://{current_dir}/lib/kafka-clients-3.0.1.jar"
    
    env.add_jars(kafka_connector_jar)
    env.add_jars(kafka_clients_jar)
    
    # Create Kafka source - use the service name from docker-compose
    source = KafkaSource.builder() \
        .set_bootstrap_servers("kafka:9092") \  # Use internal Docker network name
        .set_topics("rf-topic") \
        .set_group_id("flink-test-group") \
        .set_starting_offsets(KafkaOffsetsInitializer.earliest()) \
        .set_value_only_deserializer(SimpleStringSchema()) \
        .build()
    
    # Create data stream from Kafka source
    ds = env.from_source(
        source, 
        WatermarkStrategy.for_monotonous_timestamps(), 
        "KafkaSource"
    )
    
    # Process and display the messages
    def process_message(message):
        try:
            # Parse the JSON message
            data = json.loads(message)
            logger.info(f"RECEIVED: {data}")
            return data
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {"error": str(e), "raw_message": message}
    
    # Apply the processing function and execute
    ds.map(process_message).name("Process-Message")
    
    # Execute the Flink job
    env.execute("Kafka RF Data Consumer")

if __name__ == "__main__":
    main()


