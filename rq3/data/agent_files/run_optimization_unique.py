import stim
import sys

BASELINE_STIM = """
H 0
CX 0 12 0 18 0 49 0 52
H 6 48
CX 6 0 48 0 12 1 1 12 12 1 6 1 48 1 18 2 2 18 18 2 6 2 48 2 30 3 3 30 30 3 3 24 3 49 52 3 24 4 4 24 24 4 52 4 52 5 5 52 52 5 5 49 6 36 6 42 36 7 7 36 36 7 42 8 8 42 42 8 36 9 9 36 36 9
H 9
CX 9 13 9 19 9 49
H 12
CX 12 9 48 9 13 10 10 13 13 10 12 10 48 10 19 11 11 19 19 11 12 11 48 11 12 25 12 31 25 13 13 25 25 13 31 14 14 31 31 14 49 15 15 49 49 15 15 37 15 43 44 15 45 15 46 15 47 15 50 15 51 15 53 15 37 16 16 37 37 16 44 16 45 16 46 16 47 16 50 16 51 16 53 16 43 17 17 43 43 17 44 17 45 17 46 17 47 17 50 17 51 17 53 17 42 18 18 42 42 18
H 18
CX 18 20 18 31 18 51
H 42
CX 42 18 48 18 31 19 19 31 31 19 42 19 48 19 42 20 48 20 42 21 21 42 42 21 21 26 21 32 26 22 22 26 26 22 32 23 23 32 32 23 44 24 24 44 44 24 24 38 51 24 38 25 25 38 38 25 51 25 51 26 26 51 51 26 36 27 27 36 36 27
H 27
CX 27 42 27 49 27 50
H 30
CX 30 27 48 27 49 28 28 49 49 28 30 28 48 28 42 29 29 42 42 29 30 29 48 29 30 33 30 36 36 31 31 36 36 31 33 32 32 33 33 32 45 33 33 45 45 33 33 39 50 33 39 34 34 39 39 34 50 34 50 35 35 50 50 35 48 36 36 48 48 36
H 48
CX 36 37 36 48 36 51 36 53
H 38 44
CX 38 36 44 36 38 37 44 37 51 38 38 51 51 38 44 38 51 38 44 39 39 44 44 39 39 44 39 49 49 40 40 49 49 40 44 41 41 44 44 41 46 42 42 46 46 42 42 49 51 42 49 43 43 49 49 43 51 43 51 44 44 51 51 44 48 45 45 48 48 45 45 48 45 49 45 53
H 52
CX 52 45 49 46 46 49 49 46 52 46 48 47 47 48 48 47 52 47 52 48 48 52 52 48 48 49 48 50 52 51 51 52 52 51 51 52 53 51 53 52
"""

def solve():
    try:
        baseline = stim.Circuit(BASELINE_STIM)
    except Exception as e:
        print(f"Error parsing baseline: {e}")
        return

    # Synthesize using graph state
    sim = stim.TableauSimulator()
    sim.do(baseline)
    # Get the tableau of the operation implemented by the circuit
    # The circuit prepares a state from |0>. The tableau represents U such that U|0> = |psi>.
    # Wait, current_inverse_tableau().inverse() gives the tableau of the operation performed so far.
    tableau = sim.current_inverse_tableau().inverse()
    
    # Check if graph state synthesis works
    try:
        candidate = tableau.to_circuit(method="graph_state")
    except Exception as e:
        print(f"Error synthesizing graph state: {e}")
        return

    # Post-process to remove resets and use H for RX
    clean_circuit = stim.Circuit()
    for instr in candidate:
        if instr.name == "RX":
            # RX reset puts qubit in |+>. 
            # Since we start in |0>, apply H to get |+>.
            clean_circuit.append("H", instr.targets_copy())
        elif instr.name == "R" or instr.name == "RZ":
             # R/RZ reset puts qubit in |0>.
             # Since we start in |0>, do nothing.
             pass
        elif instr.name == "MY" or instr.name == "MZ" or instr.name == "MX":
             # Should not happen for unitary synthesis but just in case
             print(f"Warning: Measurement {instr.name} found")
             clean_circuit.append(instr)
        else:
            clean_circuit.append(instr)
            
    # Write to file
    with open("candidate_run.stim", "w") as f:
        f.write(str(clean_circuit))
    
    print("Candidate written to candidate_run.stim")

if __name__ == "__main__":
    solve()
