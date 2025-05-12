from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import KafkaSource
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common import WatermarkStrategy
import json
import requests

TRITON_URL = "http://localhost:8000/v2/models/dummy_model/infer"

def infer_from_triton(features):
    inputs = {
        "inputs": [{
            "name": "input",
            "shape": [1, 3],
            "datatype": "FP32",
            "data": features
        }]
    }
    response = requests.post(TRITON_URL, json=inputs)
    return response.json()

def flink_job():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.add_jars("file:///home/ahmed/my_project/lib/flink-connector-kafka-3.0.1-1.17.jar")
    env.add_jars("file:///home/ahmed/my_project/lib/kafka-clients-2.8.0.jar")
    source = KafkaSource.builder() \
        .set_bootstrap_servers("localhost:9092") \
        .set_topics("rf-topic") \
        .set_group_id("flink-group") \
        .set_value_only_deserializer(SimpleStringSchema()) \
        .build()

    ds = env.from_source(
    source,
    WatermarkStrategy.no_watermarks(),
    source_name="KafkaSource"
    )

    def process_data(value):
        data = json.loads(value)
        result = infer_from_triton(data["features"])
        print(f"Sensor {data['sensor_id']} -> Prediction: {result}")

    ds.map(process_data)
    env.execute("RF Sensor Inference Job")

if __name__ == "__main__":
    flink_job()

