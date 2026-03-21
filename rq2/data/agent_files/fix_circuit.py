import stim

def main():
    with open("circuit_input.stim", "r") as f:
        circuit_str = f.read()
    circuit = stim.Circuit(circuit_str)
    
    with open("stabilizers.txt", "r") as f:
        stabilizers = [line.strip() for line in f if line.strip()]
        
    for i in range(len(stabilizers)):
        s = stabilizers[i]
        if len(s) < 175:
            stabilizers[i] = s + "I" * (175 - len(s))
        elif len(s) > 175:
            stabilizers[i] = s[:175]
            
    weights = []
    for s_str in stabilizers:
        w = 0
        for char in s_str:
            if char in "XYZ":
                w += 1
        weights.append(w)
        
    print(f"Stabilizer weights: min={min(weights)}, max={max(weights)}, avg={sum(weights)/len(weights)}")

if __name__ == "__main__":
    main()
