import stim
import sys

def analyze():
    try:
        with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\stabilizers_120.txt', 'r') as f:
            lines = [l.strip() for l in f if l.strip()]
        
        stabilizers = [stim.PauliString(line) for line in lines]
        
        # Check for consistency
        # We can try to build a tableau from all of them and see if it fails
        try:
            t = stim.Tableau.from_stabilizers(stabilizers)
            print("All stabilizers are consistent.")
        except Exception as e:
            print(f"Stabilizers are inconsistent: {e}")
            
            # Identify which ones are conflicting
            # We can iteratively add them and see when it breaks
            
            good_stabs = []
            for i, s in enumerate(stabilizers):
                current_set = good_stabs + [s]
                try:
                    stim.Tableau.from_stabilizers(current_set, allow_redundant=True, allow_underconstrained=True)
                    good_stabs.append(s)
                except Exception as e:
                    print(f"Stabilizer {i} conflicts with previous ones.")
                    # We skip it
            
            print(f"Found {len(good_stabs)} consistent stabilizers.")
            
            # Generate circuit from good ones
            t = stim.Tableau.from_stabilizers(good_stabs, allow_redundant=True, allow_underconstrained=True)
            c = t.to_circuit()
            with open(r'C:\Users\anpaz\Repos\quantum-ai\rq1\data\gemini-3-pro-preview\agent_files\circuit_120_improved.stim', 'w') as f:
                f.write(str(c))
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze()
