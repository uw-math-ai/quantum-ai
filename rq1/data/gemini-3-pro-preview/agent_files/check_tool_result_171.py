import json

try:
    with open(r"C:\Users\anpaz\AppData\Local\Temp\1771699021483-copilot-tool-output-ggm0d1.txt", "r") as f:
        data = json.load(f)
    
    print(f"Preserved: {data.get('preserved')}")
    print(f"Total: {data.get('total')}")
    
    if data.get('error'):
        print(f"Error: {data.get('error')}")
        
except Exception as e:
    print(f"Error reading/parsing file: {e}")
