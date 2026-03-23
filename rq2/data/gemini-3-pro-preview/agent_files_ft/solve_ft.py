import stim
import sys

class FTSolver:
    def __init__(self, circuit_str):
        self.circuit = stim.Circuit(circuit_str)
        self.num_qubits = 105
        self.next_ancilla = 105
        self.ancillas = []
        
        # Flatten circuit to list of ops
        self.ops = []
        for instruction in self.circuit:
            if instruction.name in ["H", "S", "X", "Y", "Z", "I"]:
                for t in instruction.targets_copy():
                    self.ops.append((instruction.name, [t.value]))
            elif instruction.name == "CX":
                targets = instruction.targets_copy()
                for i in range(0, len(targets), 2):
                    self.ops.append(("CX", [targets[i].value, targets[i+1].value]))
            elif instruction.name in ["R", "RX", "RY", "RZ", "M", "MX", "MY", "MZ", "MPP"]:
                 # Keep as is? Or decomposition?
                 # The input seems to only have H, CX.
                 # But let's handle generic just in case.
                 pass
            else:
                 pass
                 
    def analyze_faults(self):
        # Determine current max qubit index to include ancillas
        max_q = self.num_qubits - 1
        if self.ancillas:
            max_q = max(max_q, max(self.ancillas))
        
        bad_faults = []
        max_weight_found = 0
        
        # We only care about errors on DATA qubits (0-104).
        # Ancilla errors are fine if they don't spread to >4 data qubits.
        
        # Create a mapping of gate usage to speed up
        # Actually just linear scan is fine for ~2000 gates.
        
        # Precompute gates
        ops = self.ops
        
        for i in range(len(ops) + 1):
            # Optim: Skip checking faults on ancillas?
            # Fault on ancilla can spread to data. Must check.
            
            if i < len(ops):
                name, targets = ops[i]
                fault_targets = targets
            else:
                continue

            for target in fault_targets:
                for error_type in ["X", "Z"]:
                    # Propagation simulation
                    # We can use sets for error state
                    x_err = set()
                    z_err = set()
                    if error_type == "X": x_err.add(target)
                    else: z_err.add(target)
                    
                    # Track if flag triggered
                    # Flag triggers if any ANCILLA has X error at the end.
                    # We assume ancillas are measured in Z basis (standard for flags).
                    # Wait, prompt: "Flagging means X error on flag qubit."
                    # Yes, X error -> flip |0> to |1> -> measurement -1.
                    
                    flag_triggered = False
                    
                    for j in range(i + 1, len(ops)):
                        op_name, op_targets = ops[j]
                        if op_name == "H":
                            for t in op_targets:
                                hx = t in x_err
                                hz = t in z_err
                                if hx and not hz: x_err.remove(t); z_err.add(t)
                                elif not hx and hz: z_err.remove(t); x_err.add(t)
                        elif op_name == "CX":
                            for k in range(0, len(op_targets), 2):
                                c = op_targets[k]
                                t = op_targets[k+1]
                                if c in x_err:
                                    if t in x_err: x_err.remove(t)
                                    else: x_err.add(t)
                                if t in z_err:
                                    if c in z_err: z_err.remove(c)
                                    else: z_err.add(c)
                        elif op_name == "CZ":
                            for k in range(0, len(op_targets), 2):
                                c = op_targets[k]
                                t = op_targets[k+1]
                                if c in x_err:
                                    if t in z_err: z_err.remove(t)
                                    else: z_err.add(t)
                                if t in x_err:
                                    if c in z_err: z_err.remove(c)
                                    else: z_err.add(c)
                                
                    # Check flags
                    for anc in self.ancillas:
                        if anc in x_err:
                            flag_triggered = True
                            break
                            
                    if flag_triggered:
                        continue # Fault tolerant!
                        
                    # Calculate weight on data qubits
                    weight = 0
                    for q in range(105):
                        if q in x_err or q in z_err:
                            weight += 1
                            
                    if weight > max_weight_found:
                        max_weight_found = weight
                        
                    if weight >= 4:
                        bad_faults.append((i, target, error_type, weight))
                        
        return max_weight_found, bad_faults

    def apply_fixes(self, bad_faults):
        # Map: (qubit, type) -> list of op_indices
        fault_map = {}
        for idx, q, type, w in bad_faults:
            key = (q, type)
            if key not in fault_map:
                fault_map[key] = []
            fault_map[key].append(idx)
            
        intervals = [] # (start, end, q, type, ancilla)
        
        # 1. Determine all intervals
        for (q, type), indices in fault_map.items():
            indices.sort()
            
            # Helper to check safety
            def is_safe(op_idx, q, type):
                if op_idx >= len(self.ops): return True
                name, targets = self.ops[op_idx]
                if name == "CX":
                    c, t = targets
                    if type == "X":
                        if t == q: return False # Cannot be target
                    elif type == "Z":
                        if c == q: return False # Cannot be control
                elif name == "H":
                     if q in targets: return False
                return True

            # Group indices into covering intervals
            # Greedily take first fault, expand, remove covered faults
            
            uncovered = set(indices)
            while uncovered:
                idx = min(uncovered)
                start = idx
                end = idx
                
                # Expand
                while start > 0 and is_safe(start - 1, q, type):
                    start -= 1
                while end < len(self.ops) - 1 and is_safe(end + 1, q, type):
                    end += 1
                
                # Assign ancilla
                ancilla = self.next_ancilla
                self.next_ancilla += 1
                self.ancillas.append(ancilla)
                
                intervals.append((start, end, q, type, ancilla))
                
                # Remove covered
                to_remove = set()
                for u in uncovered:
                    if start <= u <= end:
                        to_remove.add(u)
                uncovered -= to_remove

        # 2. Reconstruct circuit with intervals
        new_ops = []
        
        # Lookups for efficient processing
        starts = {}
        ends = {}
        
        for interv in intervals:
            s, e, q, t, a = interv
            if s not in starts: starts[s] = []
            starts[s].append(interv)
            if e not in ends: ends[e] = []
            ends[e].append(interv)
            
        active_z = {} # q -> list of ancillas checking q (Z-type)
        
        for i in range(len(self.ops) + 1): # +1 to handle ends at last op
            
            current_batch = []
            
            # Process starts
            if i in starts:
                cx_group = []
                h_group = []
                # Collect ops first
                for interv in starts[i]:
                    s, e, q, t, a = interv
                    if t == "X":
                        cx_group.extend([q, a])
                    elif t == "Z":
                        h_group.append(a)
                        cx_group.extend([a, q])
                        if q not in active_z: active_z[q] = []
                        active_z[q].append(a)
                
                if h_group:
                    new_ops.append(("H", h_group))
                if cx_group:
                    new_ops.append(("CX", cx_group))

            if i < len(self.ops):
                op_name, op_targets = self.ops[i]
                new_ops.append((op_name, op_targets))
                
                # Corrections for active Z checks
                if op_name == "CX":
                    c, tgt = op_targets
                    if tgt in active_z:
                        cz_group = []
                        for a in active_z[tgt]:
                            # Correction: CZ c a
                            cz_group.extend([c, a])
                        if cz_group:
                            new_ops.append(("CZ", cz_group))
            
            # Process ends
            if i in ends:
                cx_group = []
                h_group = []
                for interv in ends[i]:
                    s, e, q, t, a = interv
                    if t == "X":
                        cx_group.extend([q, a])
                    elif t == "Z":
                        cx_group.extend([a, q])
                        h_group.append(a)
                        if q in active_z:
                            active_z[q].remove(a)
                            if not active_z[q]: del active_z[q]
                            
                if cx_group:
                    new_ops.append(("CX", cx_group))
                if h_group:
                    new_ops.append(("H", h_group))

        self.ops = new_ops

    def generate(self):
        # 1. First analysis
        w, bad = self.analyze_faults()
        # print(f"Initial max weight: {w}, bad faults: {len(bad)}")
        
        # Loop
        for _ in range(3): # Try 3 iterations
            if w < 4:
                break
            self.apply_fixes(bad)
            w, bad = self.analyze_faults()
            # print(f"Iteration {_}: max weight: {w}, bad faults: {len(bad)}")
            
        # Build string
        lines = []
        for name, targets in self.ops:
            t_str = " ".join(map(str, targets))
            lines.append(f"{name} {t_str}")
            
        if self.ancillas:
            lines.append(f"M {' '.join(map(str, self.ancillas))}")
            
        return "\n".join(lines)

# Read from file? No, put circuit in variable
circuit_str = """H 0 14
CX 0 14 0 28 0 101 0 102
H 98 99
CX 98 0 99 0 101 1 1 101 101 1 1 28 1 35 1 56 1 102
H 7
CX 7 1 31 1 34 1 45 1 48 1 52 1 55 1 57 1 59 1 62 1 78 1 80 1 83 1 85 1 87 1 90 1 92 1 94 1 97 1 98 1 99 1 103 1 104 1 14 2 2 14 14 2 2 28 2 35 2 42 2 63 2 70 7 2 98 2 99 2 28 3 3 28 28 3 3 42 3 70 31 3 34 3 45 3 48 3 52 3 55 3 57 3 59 3 62 3 78 3 80 3 83 3 85 3 87 3 90 3 92 3 94 3 97 3 98 3 99 3 103 3 104 3 49 4 4 49 49 4 4 35 4 56 4 77
H 21
CX 7 4 21 4 42 4 56 4 77 4 84 4 91 4 42 5 5 42 42 5 5 56 5 63 5 84 7 5 21 5 31 5 34 5 35 5 45 5 48 5 52 5 55 5 56 5 57 5 59 5 62 5 77 5 78 5 80 5 83 5 84 5 85 5 87 5 90 5 91 5 92 5 94 5 97 5 103 5 104 5 35 6 6 35 35 6 6 63 6 77 6 91 21 6 56 6 77 6 84 6 91 6 56 7 7 56 56 7 7 63 21 7 31 7 34 7 45 7 48 7 52 7 55 7 57 7 59 7 62 7 77 7 78 7 80 7 83 7 84 7 85 7 87 7 90 7 91 7 92 7 94 7 97 7 103 7 104 7 56 8 8 56 56 8 8 63 8 70 8 84 98 8 99 8 63 9 9 63 63 9 9 70 31 9 34 9 45 9 48 9 52 9 55 9 57 9 59 9 62 9 77 9 78 9 80 9 83 9 85 9 87 9 90 9 92 9 94 9 97 9 98 9 99 9 103 9 104 9 70 10 10 70 70 10 77 10 98 10 99 10 84 11 11 84 84 11 11 77 21 11 91 11 77 12 12 77 77 12 21 12 31 12 34 12 45 12 48 12 52 12 55 12 57 12 59 12 62 12 78 12 80 12 83 12 85 12 87 12 90 12 91 12 92 12 94 12 97 12 103 12 104 12 91 13 13 91 91 13 21 13 31 13 34 13 45 13 48 13 52 13 55 13 57 13 59 13 62 13 78 13 80 13 83 13 85 13 87 13 90 13 92 13 94 13 97 13 103 13 104 13 21 14 14 21 21 14 98 15 15 98 98 15
H 21 23 26 27 35 42 56
CX 15 21 15 23 15 26 15 27 15 29 15 35 15 42 15 56 15 99 15 102 15 104
H 101
CX 101 15 56 16 16 56 56 16
H 98
CX 16 29 16 36 16 57 16 98 16 102 101 16 98 17 17 98 98 17 17 29 17 36 17 43 17 64 17 71 101 17 29 18 18 29 29 18 18 43 18 71 101 18 50 19 19 50 50 19 19 36 19 57 19 78
H 22
CX 22 19 43 19 101 19 43 20 20 43 43 20 20 57 20 64 20 85 22 20 36 20 101 20 36 21 21 36 36 21 21 64 21 78 21 92 22 21 101 21 101 22 22 101 101 22 101 22 57 23 23 57 57 23 23 102 78 23 85 23 92 23 64 24 24 64 64 24 24 71 85 24 92 24 71 25 25 71 71 25 85 25 92 25 85 26 26 85 85 26 26 78 92 26 101 26 78 27 27 78 78 27 27 102 92 27 101 27 92 28 28 92 92 28 28 102 101 28 101 29 29 101 101 29 36 30 30 36 36 30
H 63
CX 30 36 30 63 30 102 99 30 63 31 31 63 63 31
H 56
CX 31 36 31 37 31 56 31 57 31 58 31 102 99 31 56 32 32 56 56 32 32 36 32 37 32 44 32 65 32 72 99 32 36 33 33 36 36 33 33 44 33 72 99 33 57 34 34 57 57 34 34 37 34 51 34 58 34 79 37 35 35 37 37 35 35 44 35 51 35 65 35 79 35 86 44 36 36 44 44 36 36 51 36 86 36 93 51 37 37 51 51 37 37 93 102 38 38 102 102 38 38 58 39 38 45 38 52 38 59 38 60 38 63 38 80 38 81 38 87 38 94 38 99 38 103 38 65 39 39 65 65 39 39 72 45 39 52 39 58 39 59 39 60 39 63 39 65 39 79 39 80 39 81 39 87 39 94 39 99 39 103 39 72 40 40 72 72 40 45 40 52 40 58 40 59 40 60 40 63 40 65 40 79 40 80 40 81 40 87 40 94 40 99 40 103 40 79 41 41 79 79 41 41 86 45 41 52 41 58 41 59 41 60 41 63 41 65 41 80 41 81 41 87 41 94 41 103 41 58 42 42 58 58 42 42 86 45 42 52 42 59 42 60 42 63 42 65 42 80 42 81 42 87 42 94 42 103 42 86 43 43 86 86 43 43 93 45 43 52 43 59 43 60 43 63 43 65 43 80 43 81 43 87 43 94 43 103 43 93 44 44 93 93 44 45 44 52 44 59 44 60 44 63 44 65 44 80 44 81 44 87 44 94 44 103 44 92 45 45 92 92 45
H 45 70
CX 45 63 45 70 45 103
H 100
CX 100 45 100 46 46 100 100 46
H 98
CX 46 58 46 59 46 85 46 98 46 99 46 102 70 46 98 47 47 98 98 47 47 63 47 66 47 73 47 92 47 102 70 47 63 48 48 63 63 48 48 73 48 92 70 49 49 70 70 49 49 52 49 66 49 73 49 80 49 92 49 102 49 103
H 64
CX 64 49 102 50 50 102 102 50 50 52 50 66 50 80 50 87 50 92 64 50 92 51 51 92 92 51 51 52 51 87 51 94 64 51 52 94 64 52 59 53 53 59 59 53 53 103 80 53 87 53 94 53 66 54 54 66 66 54 54 73 87 54 94 54 73 55 55 73 73 55 87 55 94 55 87 56 56 87 87 56 56 80 64 56 94 56 80 57 57 80 80 57 57 103 64 57 94 57 94 58 58 94 94 58 58 103 64 58 64 59 59 64 64 59 99 60 60 99 99 60
H 71 84
CX 60 71 60 78 60 84 60 87 60 92 60 103 60 104
H 70
CX 70 60 70 61 61 70 70 61
H 101
CX 61 65 61 71 61 99 61 101 84 61 84 62 62 84 84 62 62 67 62 71 62 74 62 99 62 100 62 103 101 62 87 63 63 87 87 63 63 74 63 100 101 63 71 64 64 71 71 64 64 67 64 71 64 81 64 99 64 101 65 67 65 71 65 81 65 88 65 100 101 65 100 66 66 100 100 66 66 71 66 88 66 95 101 66 71 67 67 71 71 67 67 95 99 68 68 99 99 68 68 103 81 68 71 69 69 71 71 69 69 74 101 69 74 70 70 74 74 70 101 70 101 71 71 101 101 71 71 88 71 95 81 72 72 81 81 72 72 103 88 73 73 88 88 73 73 95 95 74 74 95 95 74 94 75 75 94 94 75
H 77
CX 75 77 75 93 75 103 77 76 76 77 77 76
H 102
CX 76 81 76 85 76 93 76 95 76 102 76 103 102 77 77 102 102 77 77 81 77 93 77 94 77 98 77 99 93 78 78 93 93 78 78 94 78 98 85 79 79 85 85 79 79 81 79 82 79 95 79 100 81 80 80 81 81 80 80 82 80 89 80 98 80 99 80 100 98 81 81 98 98 81 81 89 81 96 81 100 100 82 82 100 100 82 82 96 103 83 83 103 103 83 83 95 84 83 87 83 88 83 90 83 97 83 98 83 103 83 104 83 99 84 84 99 99 84 84 94 87 84 88 84 90 84 95 84 97 84 98 84 99 84 100 84 103 84 104 84 94 85 85 94 94 85 87 85 88 85 90 85 95 85 97 85 98 85 99 85 100 85 103 85 104 85 100 86 86 100 100 86 86 89 87 86 88 86 90 86 95 86 97 86 98 86 99 86 103 86 104 86 95 87 87 95 95 87 87 89 88 87 90 87 95 87 97 87 98 87 99 87 103 87 104 87 89 88 88 89 89 88 88 96 89 88 90 88 95 88 97 88 98 88 99 88 103 88 104 88 96 89 89 96 96 89 90 89 95 89 96 89 97 89 98 89 99 89 103 89 104 89 92 90 90 92 92 90
H 91
CX 90 91 90 98
H 100
CX 91 93 91 94 91 98 91 99 91 100 91 104 100 92 92 100 100 92 92 94 92 95 92 98 92 101 92 102 98 93 93 98 98 93 93 95 93 102 98 94 94 98 98 94 94 96 94 98 94 99 94 103 94 104 98 95 95 98 98 95 95 96 95 98 95 100 95 101 95 103 98 96 96 98 98 96 96 97 96 98 96 100 98 97 97 98 98 97 97 98 99 98 98 99 99 98 99 98 100 98 103 98 104 98 101 99 99 101 101 99 99 102 100 99 101 99 104 99 102 100 100 102 102 100 101 100 102 100 104 100 102 101 101 102 102 101 101 103 102 101 104 101 103 102 102 103 103 102 103 102 104 102 104 103"""

solver = FTSolver(circuit_str)
result = solver.generate()
print(result)
