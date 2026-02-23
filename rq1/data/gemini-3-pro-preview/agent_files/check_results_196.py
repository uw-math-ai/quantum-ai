import json

file_path = r"C:\Users\anpaz\AppData\Local\Temp\1771626676651-copilot-tool-output-zsjhx0.txt"

try:
    with open(file_path, "r") as f:
        data = json.load(f)
    
    print(f"Preserved: {data.get('preserved')}")
    print(f"Total: {data.get('total')}")
    
    if data.get('preserved') == data.get('total'):
        print("SUCCESS: All stabilizers preserved.")
    else:
        print("FAILURE: Some stabilizers not preserved.")
        for k, v in data.get('results', {}).items():
            if not v:
                print(f"Failed: {k}")

except Exception as e:
    print(f"Error reading results: {e}")
