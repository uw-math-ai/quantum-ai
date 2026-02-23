import json

def check():
    with open(r'C:\Users\anpaz\AppData\Local\Temp\1771604775078-copilot-tool-output-k5gyjo.txt', 'r') as f:
        data = json.load(f)
    
    results = data.get('results', {})
    failed = [k for k, v in results.items() if not v]
    
    if failed:
        print(f"Failed stabilizers: {len(failed)}")
        for s in failed:
            print(s)
    else:
        print("All stabilizers passed!")

if __name__ == "__main__":
    check()
