import stim
import sys

def get_data_qubits():
    # Parse stabilizers to find max qubit index
    try:
        with open("stabilizers.txt", "r") as f:
            stabs = f.read().splitlines()
        
        # Stabs are strings like "XX..."
        # Length of string is number of qubits
        # Prompt says circuit uses qubits up to 53.
        # Stabilizer string length:
        if not stabs: return []
        n = len(stabs[0].strip())
        return list(range(n))
    except Exception as e:
        # Fallback to circuit parsing
        return list(range(54))

if __name__ == "__main__":
    print(get_data_qubits())
