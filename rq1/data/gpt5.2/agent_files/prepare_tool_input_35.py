import json

def prepare_args():
    with open("stabilizers_35_task_v2.txt", "r") as f:
        stabilizers = [l.strip() for l in f if l.strip()]
    
    with open("circuit_35_task.stim", "r") as f:
        circuit = f.read()
        
    print(json.dumps({"circuit": circuit, "stabilizers": stabilizers}))

if __name__ == "__main__":
    prepare_args()
