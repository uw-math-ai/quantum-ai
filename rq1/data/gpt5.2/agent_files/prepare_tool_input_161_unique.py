
import json

def prepare():
    with open("C:\\Users\\anpaz\\Repos\\quantum-ai\\rq1\\stabilizers_161_v3.txt") as f:
        stabilizers = [l.strip() for l in f if l.strip()]
        
    print(json.dumps(stabilizers))

if __name__ == "__main__":
    prepare()
