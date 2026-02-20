import json

path = r'C:\Users\anpaz\AppData\Local\Temp\1771598198269-copilot-tool-output-dcb4wo.txt'
try:
    with open(path, 'r') as f:
        data = json.load(f)
    
    print(f"Preserved: {data.get('preserved')}")
    print(f"Total: {data.get('total')}")
    
    results = data.get('results', {})
    false_count = 0
    for k, v in results.items():
        if not v:
            false_count += 1
            # print(f"Failed: {k[:20]}...")
            
    print(f"False count: {false_count}")

except Exception as e:
    print(f"Error: {e}")
