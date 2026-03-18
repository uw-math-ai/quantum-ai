import stim

def solve():
    # Load baseline
    with open("baseline_prompt.stim", "r") as f:
        baseline_text = f.read()
    
    baseline = stim.Circuit(baseline_text)
    
    # Simulate to get tableau
    sim = stim.TableauSimulator()
    sim.do(baseline)
    t = sim.current_inverse_tableau().inverse()
    
    # Synthesize
    # method="graph_state" is optimal for CX count (uses CZ)
    candidate = t.to_circuit(method="graph_state")
    
    cand_str = str(candidate)
    
    new_lines = []
    for line in cand_str.splitlines():
        if line.strip().startswith("RX"):
            # Replace RX with H
            new_lines.append(line.replace("RX", "H"))
        elif line.strip().startswith("R "):
             pass
        elif line.strip().startswith("TICK"):
            continue 
        else:
            new_lines.append(line)
            
    # Re-assemble
    final_text = "\n".join(new_lines)
    
    # Double check it parses
    try:
        c = stim.Circuit(final_text)
        with open("candidate.stim", "w") as f:
            f.write(final_text)
        print("Generated candidate.stim")
        print(f"Stats: {c.num_gates} gates")
    except Exception as e:
        print(f"Error parsing generated circuit: {e}")

if __name__ == "__main__":
    solve()
