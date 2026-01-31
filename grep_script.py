import json
import os
from dateTime import datetime
import time
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.write.point import Point, WritePrecision


INFLUX_URL    = "http://localhost:8086"   
INFLUX_TOKEN  = "gzpYuBDNdp4cyMOUOfsYaB96Q6Wn-kjShJ6ojc_k-t8jdcxa5z6RPCgZVKHjJ9UnIBwrF2Alt9-yNa9I1jSOpQ=="         # your InfluxDB auth token
INFLUX_ORG    = "SSiHackathon"           # your InfluxDB org name
INFLUX_BUCKET = "HackBucket"        # target bucket to write into

time_to_temp_graph_data = {"time": [], "temp": [], "soil_val": [], "hum": []}

folder_path = "dataset/Makerfabs Soil Moisture Sensor/48e663fffe3000dd"

for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        file_path = os.path.join(folder_path, filename)

        with open(file_path, "r") as file:
            data = json.load(file)

        #For Debugging: show which file you're processing
        print(f"Processing {filename}")

        # Check top-level keys
        if "time" not in data:
            print(f"  Skipping {filename}: no 'time'")
            continue

        if "object" not in data:
            print(f"  Skipping {filename}: no 'object'")
            continue

        obj = data["object"]

        # Check sensor fields inside object
        required_fields = ["temp", "soil_val", "hum"]
        if not all(field in obj for field in required_fields):
            print(f"  Skipping {filename}: missing one of {required_fields}")
            continue

        # Safe to append now
        time_to_temp_graph_data["time"].append(data["time"])
        time_to_temp_graph_data["temp"].append(obj["temp"])
        time_to_temp_graph_data["soil_val"].append(obj["soil_val"])
        time_to_temp_graph_data["hum"].append(obj["hum"])

print("Done loading.")
print(time_to_temp_graph_data)



record = list(zip(time_to_temp_graph_data["time"],
                  time_to_temp_graph_data["temp"],time_to_temp_graph_data["soil_val"],
                  time_to_temp_graph_data["hum"]))

record.sort(key=lambda x: datetime.fromisoformat(x[0].replace("Z", "+00:00")))

# ─── Replay + Write to InfluxDB ───────────────────────────────────────────────
for entry in records:
    timestamp, temp, soil_val, hum = entry

    # Parse the ISO timestamp for InfluxDB
    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

    point = (
        Point("soil_sensor")
        .tag("sensor_id", "48e663fffe3000dd")
        .field("temp", float(temp))
        .field("soil_val", float(soil_val))
        .field("hum", float(hum))
        .time(dt, WritePrecision.NS)
    )

    # Write the single point
    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)

    print(f"[REPLAY + WRITE] {timestamp} | Temp: {temp}°C | Soil: {soil_val} | Humidity: {hum}%")

# ─── Cleanup ──────────────────────────────────────────────────────────────────
client.close()
print("All records written to InfluxDB and connection closed.")