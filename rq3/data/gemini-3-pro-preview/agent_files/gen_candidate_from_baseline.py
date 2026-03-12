import stim
import sys

try:
    with open("baseline.stim", "r") as f:
        baseline_text = f.read()

    baseline = stim.Circuit(baseline_text)
    sim = stim.TableauSimulator()
    sim.do(baseline)
    
    inv_tab = sim.current_inverse_tableau()
    tab = inv_tab.inverse()
    
    # Generate circuit using graph state method
    circuit = tab.to_circuit(method="graph_state")
    
    # Post-process to replace RX with H (assuming start from |0>)
    # and ensure no other resets.
    new_circuit = stim.Circuit()
    for instruction in circuit:
        if instruction.name == "RX":
            # RX resets to |+>. From |0>, H does this.
            targets = instruction.targets_copy()
            new_circuit.append("H", targets)
        elif instruction.name == "R" or instruction.name == "RZ":
            # R or RZ resets to |0>. From |0>, Identity does this.
            # So just skip.
            pass
        elif instruction.name == "RY":
             # RY resets to |i+>. From |0>, H then S does this.
             targets = instruction.targets_copy()
             new_circuit.append("H", targets)
             new_circuit.append("S", targets)
        elif instruction.name == "TICK":
            pass
        else:
            new_circuit.append(instruction)
            
    print(new_circuit)

except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)

