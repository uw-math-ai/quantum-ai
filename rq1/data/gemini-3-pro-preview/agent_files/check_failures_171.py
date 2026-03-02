import json

try:
    with open(r"C:\Users\anpaz\AppData\Local\Temp\1771699021483-copilot-tool-output-ggm0d1.txt", "r") as f:
        data = json.load(f)
    
    results = data.get('results', {})
    failed = [s for s, res in results.items() if not res]
    
    print(f"Failed count: {len(failed)}")
    for s in failed:
        print(f"FAILED: {s}")
        
except Exception as e:
    print(f"Error reading/parsing file: {e}")
