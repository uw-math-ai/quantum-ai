import stim

def count_cx(circuit):
    count = 0
    for op in circuit:
        if op.name == "CX":
            count += len(op.targets_copy()) // 2
        elif op.name == "CZ":
            count += len(op.targets_copy()) // 2  # Assuming CZ counts as CX if tool is lenient, or we decompose
    return count

def main():
    with open("baseline.stim", "r") as f:
        circuit = stim.Circuit(f.read())
    
    print(f"Baseline CX count: {count_cx(circuit)}")
    print(f"Baseline instructions: {len(circuit)}")

if __name__ == "__main__":
    main()
