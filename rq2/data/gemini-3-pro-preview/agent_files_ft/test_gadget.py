import stim

def test_gadget():
    # Circuit: H 0, CX 0 1, CX 0 2
    # Gadget: H 0. CX 0 a. CX a 1. CX a 2. CX 0 a. Measure a.
    
    # Baseline
    c = stim.Circuit()
    c.append("H", [0])
    c.append("CX", [0, 1])
    c.append("CX", [0, 2])
    print("Baseline X0 propagation:")
    # Inject X on 0 after H
    sim = stim.TableauSimulator()
    sim.do(stim.Circuit("H 0 X 0 CX 0 1 CX 0 2"))
    # Check outputs. 0, 1, 2 should all have flipped?
    # 0 was |+>, X0 -> |+>. 
    # 1 was |0>, CX 0 1 -> |00>+|11>. 
    # This is getting complicated to trace manually.
    
    # Let's trace Paulis.
    # X0 -> CX 0 1 -> X0 X1
    # -> CX 0 2 -> X0 X1 X2.
    # Weight 3.
    
    # Gadget
    # X0 -> CX 0 a -> X0 Xa
    # -> CX a 1 -> X0 Xa X1
    # -> CX a 2 -> X0 Xa X1 X2
    # -> CX 0 a -> X0 (Xa*Xa=I) X1 X2 = X0 X1 X2.
    # a has NO error. Measure a -> 0.
    # Result: X0 X1 X2. Not flagged.
    
    print("Gadget does not flag X0.")

test_gadget()
