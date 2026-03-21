import stim
def main():
    # Test Tableau.prepend
    t = stim.Tableau(2)
    # t is Identity
    # Prepend X on 0
    t.prepend(stim.Tableau.from_named_gate("X"), [0])
    # t should represent X on 0.
    # Propagate Z0 -> X Z0 X = -Z0? No.
    # X Z X = -Z.
    # Tableau maps P -> U P U^-1.
    # If U = X, Z -> -Z.
    p = stim.PauliString("Z_")
    out = t(p)
    print(f"Propagating Z_ through X0: {out}")
    
    # Test suffix logic
    # Circuit: H 0, CX 0 1.
    # Ops: [H 0], [CX 0 1]
    # S_2 = I
    # S_1 = I * CX 0 1 (prepend CX 0 1 to I) = CX 0 1.
    # S_0 = S_1 * H 0 (prepend H 0 to S_1) = CX 0 1 * H 0.
    # S_0 represents U = CX 0 1 H 0.
    # Apply H 0 then CX 0 1.
    # If state |00>, H0 -> |+0>, CX -> |Bell>.
    # Propagate Z0 through S_0.
    # Z0 -> (CX H) Z0 (H CX) = CX (H Z0 H) CX = CX (X0) CX = X0 X1.
    
    s2 = stim.Tableau(2)
    
    s1 = s2.copy()
    s1.prepend(stim.Tableau.from_named_gate("CX"), [0, 1])
    
    s0 = s1.copy()
    s0.prepend(stim.Tableau.from_named_gate("H"), [0])
    
    p = stim.PauliString("Z_")
    out = s0(p)
    print(f"Propagating Z_ through H0 CX01: {out}")
    # Expected: +XX
    
    # Check if my script logic does this.
    # My script loop:
    # k=1 (CX): current_suffix (I). prepend CX. s1 = CX.
    # k=0 (H): current_suffix (CX). prepend H. s0 = CX H.
    # Seems correct.
    
    # Maybe `targets` handling for `prepend` is tricky.
    
if __name__ == "__main__":
    main()
