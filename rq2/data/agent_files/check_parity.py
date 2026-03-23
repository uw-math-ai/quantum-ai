import stim

def check_stabilizers(path):
    with open(path, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
        
    stabs = []
    print(f"Loaded {len(lines)} stabilizers.")
    
    for l in lines:
        try:
            # Clean string if commas or extra chars
            l = l.replace(',', '').replace(' ', '')
            p = stim.PauliString(l)
            stabs.append(p)
        except Exception as e:
            print(f"Error parsing stabilizer '{l}': {e}")
            
    weights = [p.weight for p in stabs]
    if weights:
        print(f"Min weight: {min(weights)}")
        print(f"Max weight: {max(weights)}")
        print(f"Weights histogram: {sorted(weights)}")
        
        # Check if they are X or Z type (important for flag choice)
        x_stabs = 0
        z_stabs = 0
        mixed_stabs = 0
        for p in stabs:
            # Check components
            has_x = False
            has_z = False
            for k in range(len(p)):
                if p[k] in [1, 2]: has_x = True
                if p[k] in [2, 3]: has_z = True
            
            if has_x and not has_z: x_stabs += 1
            elif has_z and not has_x: z_stabs += 1
            else: mixed_stabs += 1
            
        print(f"X-only: {x_stabs}, Z-only: {z_stabs}, Mixed: {mixed_stabs}")

if __name__ == "__main__":
    check_stabilizers("data/gemini-3-pro-preview/agent_files_ft/stabilizers_correct.txt")
