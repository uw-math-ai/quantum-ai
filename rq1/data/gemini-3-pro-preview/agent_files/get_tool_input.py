import json

def run():
    try:
        with open("data/gemini-3-pro-preview/agent_files/stabilizers.txt", "r") as f:
            lines = [line.strip()[:105] for line in f if line.strip()]
        
        print(json.dumps(lines))
    except Exception as e:
        print(e)

if __name__ == "__main__":
    run()
