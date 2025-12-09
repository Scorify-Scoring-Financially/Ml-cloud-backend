import json
from collections import Counter

with open("lead_score_output.json") as f:
    data = json.load(f)

# Hitung yes / no
counts = Counter(item["predicted_y"] for item in data)

print("Total data:", len(data))
print("YES:", counts.get("yes", 0))
print("NO:", counts.get("no", 0))
