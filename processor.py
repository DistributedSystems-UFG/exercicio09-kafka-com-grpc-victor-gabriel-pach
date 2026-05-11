import json
from kafka import KafkaConsumer, KafkaProducer
from datetime import datetime
from collections import deque
from const import KAFKA_HOST

consumer = KafkaConsumer(
    "temperature-raw",
    bootstrap_servers=f"{KAFKA_HOST}:9092",
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset="earliest",
    group_id="processor-group"
)

producer = KafkaProducer(
    bootstrap_servers=f"{KAFKA_HOST}:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

window = deque(maxlen=10)  # keeps last 10 readings

print("Processor started. Consuming 'temperature-raw'...")

for msg in consumer:
    data = msg.value
    window.append(data["temperature"])
    avg = round(sum(window) / len(window), 2)

    event = {
        "average": avg,
        "timestamp": datetime.utcnow().isoformat()
    }
    producer.send("temperature-avg", event)
    print(f"Processed: raw={data['temperature']} → avg={avg}")