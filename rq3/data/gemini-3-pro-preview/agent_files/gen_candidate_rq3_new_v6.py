import stim

def generate_optimized():
    try:
        with open("baseline_rq3.stim", "r") as f:
            baseline_text = f.read()
        
        baseline = stim.Circuit(baseline_text)
        
        # Simulate to get the tableau
        sim = stim.TableauSimulator()
        sim.do(baseline)
        tableau = sim.current_inverse_tableau().inverse()
        
        # Synthesize using graph_state
        optimized = tableau.to_circuit(method="graph_state")
        
        print(optimized)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    generate_optimized()