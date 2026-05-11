import json, grpc, threading
from concurrent import futures
from kafka import KafkaConsumer
from datetime import datetime
from collections import deque
from const import KAFKA_HOST, GRPC_PORT

import TemperatureService_pb2
import TemperatureService_pb2_grpc

# In-memory database
history = deque(maxlen=100)
latest = None
lock = threading.Lock()

# Background thread: consumes temperature-avg from Kafka
def kafka_consumer_thread():
    global latest
    consumer = KafkaConsumer(
        "temperature-avg",
        bootstrap_servers=f"{KAFKA_HOST}:9092",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
        group_id="service-group"
    )
    print("Service consuming 'temperature-avg'...")
    for msg in consumer:
        data = msg.value
        with lock:
            history.append(data)
            latest = data
        print(f"Stored: {data}")

class TemperatureServicer(TemperatureService_pb2_grpc.TemperatureServiceServicer):

    def GetLatestAverage(self, request, context):
        with lock:
            if latest is None:
                return TemperatureService_pb2.TemperatureReply(
                    average=0.0, timestamp="no data yet")
            return TemperatureService_pb2.TemperatureReply(
                average=latest["average"],
                timestamp=latest["timestamp"])

    def GetHistory(self, request, context):
        with lock:
            records = [
                TemperatureService_pb2.TemperatureReply(
                    average=r["average"], timestamp=r["timestamp"])
                for r in history
            ]
        return TemperatureService_pb2.TemperatureHistoryReply(records=records)

    def GetAverageInRange(self, request, context):
        with lock:
            filtered = [
                r for r in history
                if request.start <= r["timestamp"] <= request.end
            ]
        if not filtered:
            return TemperatureService_pb2.TemperatureReply(
                average=0.0, timestamp="no data in range")
        avg = round(sum(r["average"] for r in filtered) / len(filtered), 2)
        return TemperatureService_pb2.TemperatureReply(
            average=avg,
            timestamp=datetime.utcnow().isoformat())

def serve():
    t = threading.Thread(target=kafka_consumer_thread, daemon=True)
    t.start()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    TemperatureService_pb2_grpc.add_TemperatureServiceServicer_to_server(
        TemperatureServicer(), server)
    server.add_insecure_port(f"0.0.0.0:{GRPC_PORT}")
    server.start()
    print(f"gRPC Service running on port {GRPC_PORT}...")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()