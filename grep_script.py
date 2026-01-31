import json
import os

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
