import stim
import sys

def check_comm():
    try:
        with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_120.txt', 'r') as f:
            lines = [l.strip() for l in f if l.strip()]
        
        stabilizers = [stim.PauliString(line) for line in lines]
        
        for i in range(len(stabilizers)):
            for j in range(i + 1, len(stabilizers)):
                if not stabilizers[i].commutes(stabilizers[j]):
                    print(f"Stabilizer {i} anticommutes with {j}")
                    return

        print("All pairs commute.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_comm()
