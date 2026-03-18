import stim
import sys

def clean(input_file, output_file):
    print(f"Reading {input_file}...")
    try:
        with open(input_file, "r") as f:
            c_text = f.read()
        c = stim.Circuit(c_text)
    except Exception as e:
        print(f"Error reading {input_file}: {e}")
        return

    new_c = stim.Circuit()
    
    for inst in c:
        name = inst.name
        targets = inst.targets_copy()
        args = inst.gate_args_copy()
        
        # Filter targets
        new_targets = []
        for t in targets:
            if t.value <= 75:
                new_targets.append(t)
        
        if not new_targets:
            continue
            
        if name == "RX":
            new_c.append("H", new_targets)
        elif name == "R":
            pass
        elif name in ["M", "MX", "MY", "MZ", "MPP"]:
            print(f"Warning: Measurement {name} found!")
            new_c.append(name, new_targets, args)
        else:
            new_c.append(name, new_targets, args)
            
    try:
        with open(output_file, "w") as f:
            f.write(str(new_c))
        print(f"Cleaned circuit saved to {output_file}")
    except Exception as e:
        print(f"Error writing {output_file}: {e}")

if __name__ == "__main__":
    clean("candidate_graph.stim", "candidate_clean.stim")
