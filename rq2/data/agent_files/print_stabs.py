import json
import sys

chunk_id = int(sys.argv[1])

with open("stabilizers.txt", "r") as f:
    stabs = [line.strip() for line in f if line.strip()]

if chunk_id == 1:
    chunk = stabs[:90]
    print(json.dumps(chunk))
elif chunk_id == 2:
    chunk = stabs[90:]
    print(json.dumps(chunk))
