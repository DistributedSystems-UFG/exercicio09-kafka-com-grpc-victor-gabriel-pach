import grpc
from const import GRPC_HOST, GRPC_PORT
from datetime import datetime, timedelta

import TemperatureService_pb2
import TemperatureService_pb2_grpc

def run():
    with grpc.insecure_channel(f"{GRPC_HOST}:{GRPC_PORT}") as channel:
        stub = TemperatureService_pb2_grpc.TemperatureServiceStub(channel)

        # Latest average
        response = stub.GetLatestAverage(TemperatureService_pb2.EmptyMessage())
        print(f"Latest average: {response.average}°C at {response.timestamp}")

        # Full history
        response = stub.GetHistory(TemperatureService_pb2.EmptyMessage())
        print(f"History ({len(response.records)} records):")
        for r in response.records:
            print(f"  {r.timestamp} → {r.average}°C")

        # Average in time range (last 1 hour)
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)
        response = stub.GetAverageInRange(TemperatureService_pb2.TimeRange(
            start=one_hour_ago.isoformat(),
            end=now.isoformat()
        ))
        print(f"Average in last hour: {response.average}°C")

if __name__ == "__main__":
    run()