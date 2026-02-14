with open("stabilizers_49_final_list.txt", "r") as f:
    stabs = [line.strip() for line in f if line.strip()]

import json
print(json.dumps(stabs))
