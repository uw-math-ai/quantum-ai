import stim
import sys

def main():
    try:
        with open("baseline.stim", "r") as f:
            baseline_text = f.read()
        
        baseline = stim.Circuit(baseline_text)
        
        sim = stim.TableauSimulator()
        sim.do(baseline)
        
        
        # New approach: Get canonical stabilizers, slice them, and reconstruct tableau.
        # This avoids the 60-qubit ghost entanglement issue.
        
        stabs = sim.canonical_stabilizers()
        print(f"Number of stabilizers: {len(stabs)}", file=sys.stderr)
        
        sliced_stabs = []
        MAX_QUBIT = 29
        expected_len = MAX_QUBIT + 1
        
        for s in stabs:
            # Convert to string and slice
            s_str = str(s)
            # s_str might be "+XZ..." or "XZ..."
            # stim 1.12+ usually includes sign.
            sign_char = ""
            if s_str[0] in "+-":
                sign_char = s_str[0]
                content = s_str[1:]
            else:
                content = s_str
            
            # Slice content
            # Warning: simulator might have size > 30.
            if len(content) > expected_len:
                sliced_content = content[:expected_len]
            else:
                sliced_content = content
            
            # Check if it's Identity
            is_identity = all(c == 'I' or c == '_' for c in sliced_content)
            if not is_identity:
                # Reconstruct
                new_s = stim.PauliString(sign_char + sliced_content)
                sliced_stabs.append(new_s)
                
        print(f"Sliced stabilizers: {len(sliced_stabs)}", file=sys.stderr)
        
        # Create tableau from sliced stabilizers
        # allow_redundant=True just in case, though canonical should be independent.
        # But after slicing, maybe some become dependent? (Unlikely if product state)
        t = stim.Tableau.from_stabilizers(sliced_stabs, allow_redundant=True)
        
        # Synthesize graph state circuit
        candidate = t.to_circuit(method="graph_state")
        
        # Post-process: Replace RX with H
        final_circuit = stim.Circuit()
        for instr in candidate:
            if instr.name == "RX":
                final_circuit.append("H", instr.targets_copy())
            elif instr.name == "TICK":
                final_circuit.append("TICK")
            else:
                final_circuit.append(instr)
                
        print(final_circuit)
        if len(final_circuit) == 0:
            print("Warning: Final circuit is empty!", file=sys.stderr)

    except Exception as e:
        if len(final_circuit) == 0:
            print("Warning: Final circuit is empty!", file=sys.stderr)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
