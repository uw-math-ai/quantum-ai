import json

def run():
    with open("data/gemini-3-pro-preview/agent_files/stabilizers.txt", "r") as f:
        # Read lines and strip whitespace
        lines = [line.strip()[:105] for line in f if line.strip()]
    
    with open("data/gemini-3-pro-preview/agent_files/tool_input.json", "w") as f:
        json.dump(lines, f)
    print("Saved to tool_input.json")

if __name__ == "__main__":
    run()
