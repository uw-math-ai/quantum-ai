import stim
import sys

def verify():
    try:
        # Load candidate
        with open('cleaned_candidate.stim', 'r') as f:
            cand_text = f.read()
        candidate = stim.Circuit(cand_text)
        
        # Load stabilizers
        with open('task_v54_stabilizers.txt', 'r') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        
        stabilizers = [stim.PauliString(l) for l in lines]
        
        cx = 0
        for instr in candidate:
            if instr.name in ['CX', 'CNOT']:
                cx += len(instr.targets_copy()) // 2
        print(f"Cleaned CX: {cx}")
        
        # Check preservation
        tableau = stim.TableauSimulator()
        tableau.do_circuit(candidate)
        
        failed = []
        for i, s in enumerate(stabilizers):
            if tableau.peek_observable_expectation(s) != 1:
                failed.append(i)
        
        if failed:
            print(f"FAILED on {len(failed)} stabilizers: {failed}")
        else:
            print("SUCCESS: All stabilizers preserved.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify()
