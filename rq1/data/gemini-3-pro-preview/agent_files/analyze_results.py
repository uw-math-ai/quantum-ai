import json

def analyze():
    path = r'C:\Users\anpaz\AppData\Local\Temp\1771678556435-copilot-tool-output-c2tfd5.txt'
    try:
        with open(path, 'r') as f:
            res = json.load(f)
    except Exception as e:
        print(f"Error reading results: {e}")
        return

    preserved = res.get('preserved')
    total = res.get('total')
    print(f"Preserved: {preserved}/{total}")
    
    results = res.get('results', {})
    failed = [k for k, v in results.items() if not v]
    print(f"Failed count: {len(failed)}")
    print("Failed items:")
    for f in failed:
        print(f"'{f}'")
    
    # We expect 3 failures if my logic was correct (dropping 7, 97, 105)
    # But wait, I generated the circuit from the 179 GOOD stabilizers.
    # The tool checked against ALL 182.
    # So the 3 bad ones should fail.
    # AND, any others that I didn't include but are consistent? No, I included all consistent ones.
    
    print("Failed stabilizers indices (approximate):")
    # I need to match strings back to indices.
    # I'll read the original file again to map.
    with open(r'data/gemini-3-pro-preview/agent_files/stabilizers_186.txt') as f:
        lines = [line.strip() for line in f if line.strip()]
        
    failed_indices = []
    for i, line in enumerate(lines):
        if line in failed: # Note: this assumes exact string match, which should hold
            failed_indices.append(i)
            
    print(f"Failed indices: {failed_indices}")

if __name__ == "__main__":
    analyze()
