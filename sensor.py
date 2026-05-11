import time, random, json
from kafka import KafkaProducer
from datetime import datetime
from const import KAFKA_HOST

producer = KafkaProducer(
    bootstrap_servers=f"{KAFKA_HOST}:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

print("Sensor started. Publishing to 'temperature-raw'...")

last_temp = 25.0
while True:
    variation = random.uniform(-2.0, 2.0)
    new_temp = round(last_temp + variation, 2)

    if abs(variation) >= 0.5:
        event = {
            "temperature": new_temp,
            "timestamp": datetime.utcnow().isoformat()
        }
        producer.send("temperature-raw", event)
        print(f"Published: {event}")
        last_temp = new_temp

    time.sleep(2)