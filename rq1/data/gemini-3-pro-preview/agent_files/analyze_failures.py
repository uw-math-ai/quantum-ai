import json

path = r'C:\Users\anpaz\AppData\Local\Temp\1771598198269-copilot-tool-output-dcb4wo.txt'
try:
    with open(path, 'r') as f:
        data = json.load(f)
    
    results = data.get('results', {})
    failed_indices = []
    
    # Read original stabilizers to map index
    with open(r'data/gemini-3-pro-preview/agent_files/stabs.txt', 'r') as f:
        stabs = [line.strip() for line in f if line.strip()]
    
    # Check which failed
    for i, s in enumerate(stabs):
        # The result keys are the stabilizers themselves
        # But we need to handle padding/formatting if the key differs.
        # The output key looks like the string.
        # Let's check if the key exists.
        
        # The key in results might be the full string or partial.
        # Let's try to match.
        
        # Actually, let's just print the failed keys from results.
        pass

    failed_keys = [k for k, v in results.items() if not v]
    print(f"Failed count: {len(failed_keys)}")
    
    # Map back to index
    failed_indices = []
    for k in failed_keys:
        # find index in stabs
        # careful with padding
        found = False
        for i, s in enumerate(stabs):
            if s in k or k in s: # simple containment
                failed_indices.append(i)
                found = True
                break
        if not found:
            print(f"Could not find index for {k[:20]}...")
            
    print(f"Failed indices: {sorted(failed_indices)}")

except Exception as e:
    print(f"Error: {e}")
