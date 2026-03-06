import stim
import sys

def solve():
    print("Loading data...")
    with open("my_stabilizers.txt", "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    stabilizers = [stim.PauliString(l) for l in lines]
    
    baseline = stim.Circuit.from_file("my_baseline.stim")
    
    sim = stim.TableauSimulator()
    sim.do(baseline)
    
    good_indices = []
    failed_indices = []
    
    for i, s in enumerate(stabilizers):
        if sim.peek_observable_expectation(s) == 1:
            good_indices.append(i)
        else:
            failed_indices.append(i)

    print(f"Failed indices: {failed_indices}")
    
    good_stabs = [stabilizers[i] for i in good_indices]
    bad_stabs = [stabilizers[i] for i in failed_indices]
    
    print(f"Checking consistency of good set ({len(good_stabs)})...")
    try:
        t = stim.Tableau.from_stabilizers(good_stabs, allow_underconstrained=True)
        print("Good set is consistent.")
    except Exception as e:
        print(f"Good set is INCONSISTENT: {e}")
        return

    for i, bad in enumerate(bad_stabs):
        try:
            test_set = good_stabs + [bad]
            t = stim.Tableau.from_stabilizers(test_set, allow_underconstrained=True)
            print(f"Bad stabilizer {failed_indices[i]} is CONSISTENT with good set.")
        except Exception as e:
            print(f"Bad stabilizer {failed_indices[i]} is INCONSISTENT with good set: {e}")

if __name__ == "__main__":
    solve()
