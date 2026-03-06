with open("data/gemini-3-pro-preview/agent_files/stabilizers_90.txt", "r") as f:
    stabilizers = [line.strip().replace(',', '') for line in f if line.strip()]
print(",".join(stabilizers))
