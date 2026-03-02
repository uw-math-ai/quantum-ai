import stim

def main():
    circuit_path = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_49_gemini.stim"
    with open(circuit_path, "r") as f:
        c = stim.Circuit(f.read())
    
    # Iterate over instructions and print them one per line
    for instruction in c:
        print(instruction)

if __name__ == "__main__":
    main()
