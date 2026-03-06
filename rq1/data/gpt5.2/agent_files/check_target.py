target = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXIIIXXIIIIIIIIIIIIIIIIIIIIIIIIIII"
with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_150_v2.txt", "r") as f:
    for i, line in enumerate(f):
        line = line.strip()
        if line == target:
            print(f"Found target at line {i}")
            exit()
        if target in line:
            print(f"Found partial match at line {i}")
        if line in target:
            print(f"Found reverse partial match at line {i}")
            
print("Target NOT found")
