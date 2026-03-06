import os
base_dir = r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files'
circuit_path = os.path.join(base_dir, 'circuit_105.stim')
with open(circuit_path, 'r') as f:
    print(repr(f.read()))
