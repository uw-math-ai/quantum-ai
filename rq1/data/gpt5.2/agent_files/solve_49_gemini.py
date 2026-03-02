import stim
import sys

def main():
    stabilizer_file = r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_49.txt"
    try:
        with open(stabilizer_file, "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        print(f"Loaded {len(lines)} stabilizers.")
        for i, line in enumerate(lines):
            print(f"{i+1}: {line}")
        
        # Convert string stabilizers to stim.PauliString
        stabs = [stim.PauliString(s) for s in lines]
        
        # Check commutativity
        anticommuting_pairs = []
        for i in range(len(stabs)):
            for j in range(i + 1, len(stabs)):
                if not stabs[i].commutes(stabs[j]):
                    anticommuting_pairs.append((i, j))
        
        if anticommuting_pairs:
             print(f"Found {len(anticommuting_pairs)} anticommuting pairs.")
             for i, j in anticommuting_pairs[:5]:
                 print(f"  {i} and {j}")
             if len(anticommuting_pairs) > 5:
                 print("  ...")

        # Generate tableau
        # allow_underconstrained=True because we might have < 49 stabilizers for 49 qubits?
        # The file has 49 lines.
        try:
            tableau = stim.Tableau.from_stabilizers(stabs, allow_underconstrained=True, allow_redundant=True)
        except Exception as e:
            print(f"Stim failed to create tableau: {e}")
            return

        circuit = tableau.to_circuit("elimination")
        print("CIRCUIT_START")
        
        circuit = tableau.to_circuit("elimination")
        circuit_str = str(circuit)
        
        final_lines = []
        for line in circuit_str.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            cmd = parts[0]
            args = parts[1:]
            
            if cmd in ["CX", "CNOT", "ZCX", "XCZ"] and len(args) > 4:
                # Split into pairs
                for i in range(0, len(args), 2):
                    if i+1 < len(args):
                        final_lines.append(f"{cmd} {args[i]} {args[i+1]}")
            else:
                final_lines.append(line)
        
        final_circuit_str = "\n".join(final_lines)
        print("CIRCUIT_START")
        print(final_circuit_str)
        print("CIRCUIT_END")

        with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_49_gemini.stim", "w") as f:
            f.write(final_circuit_str)
        
        print("Circuit written to data/gemini-3-pro-preview/agent_files/circuit_49_gemini.stim")

        # Verification
        print("Verifying circuit against stabilizers...")
        sim = stim.TableauSimulator()
        sim.do_circuit(circuit)
        
        satisfied = True
        for i, stab in enumerate(stabs):
            # measure_kickback returns (result, kickback). 
            # If the state is stabilized by P, measuring P should deterministically return 0 (for +1 eigenstate).
            # measure_expectation_value returns +1, -1, or 0.
            
            # peek_observable_expectation returns 1, -1, or 0.
            ev = sim.peek_observable_expectation(stab)
            if ev != 1:
                print(f"Stabilizer {i} not satisfied! Expectation value: {ev}")
                satisfied = False
        
        if satisfied:
            print("All stabilizers satisfied locally!")
        else:
            print("Some stabilizers failed local verification.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
