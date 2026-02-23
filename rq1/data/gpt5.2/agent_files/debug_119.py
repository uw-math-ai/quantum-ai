import stim
import sys

def fix_wrapping():
    filename = r'data\gemini-3-pro-preview\agent_files\stabilizers_119.txt'
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    # We need to fix the lines that wrap around.
    # We found that lines 7, 21, 28, 35, 42, 49, 56, 63, 84, 91, 112 failed.
    # Indices: 6, 20, 27, 34, 41, 48, 55, 62, 83, 90, 111.
    
    # Let's see index 6.
    # Current: ...XIIIXIXXIIII
    # Pattern: XIIIXIXX. Length 8.
    # If it wraps, it should be II...II (Start 107).
    # 107 + 8 = 115. Fits in 119.
    # Why did it fail?
    # Maybe it interacts with boundary? No, 115 < 119.
    
    # Wait, 108 preserved.
    # Why did these fail?
    # Maybe because the circuit I generated (using `stim.Tableau.from_stabilizers` with `allow_underconstrained=True`)
    # picked a state that DOES satisfy them, but the CHECKER says no?
    # No, the checker checks the circuit against the provided stabilizers.
    # If `stim` generated the circuit FROM the stabilizers, it should satisfy them.
    # UNLESS `allow_redundant=True` or `allow_underconstrained=True` dropped some constraints that were deemed inconsistent?
    # Or if the stabilizers I passed to `from_stabilizers` were slightly different from what I passed to the tool?
    # I passed the SAME list (fixed index 95).
    
    # Let's check consistency of the set again.
    # I ran `check_comm_119.py` and it said 0 anticommuting pairs.
    # If they all commute, there exists a state that satisfies all.
    # `stim.Tableau.from_stabilizers` should find it.
    
    # Why did it fail for 10 stabilizers?
    # Maybe they are linearly dependent on the others but with a -1 phase product?
    # i.e. S1 * S2 * ... = - Target.
    # If so, the set is inconsistent (contradictory).
    # But `check_comm` only checks commutativity, not phase consistency.
    # Actually, `stim.Tableau.from_stabilizers` would raise an error if they are inconsistent, unless `allow_underconstrained` masks it?
    # No, `allow_underconstrained` handles fewer stabilizers than qubits.
    # `allow_redundant` handles dependent stabilizers.
    # If they are dependent and inconsistent (S1*S2 = -I), it throws error even with `allow_redundant`.
    
    # So the stabilizers are consistent.
    # So why did the circuit fail?
    # Maybe the circuit prepares +1 eigenstate, but for some it prepares -1?
    # Why?
    # Maybe the `stim.Tableau.from_stabilizers` logic guarantees +1 for the INDEPENDENT generators it picks.
    # For the redundant ones, it *should* be +1 if consistent.
    
    # Let's re-verify the "failures".
    # Are they wrapping around?
    # Index 6: Start 107. Ends 114. Fits.
    # Index 20: Start 105. Len 14. Ends 118. Fits.
    # Index 27: Start 104. Len 15. Ends 118. Fits.
    # Index 34: Start 106. Len 13. Ends 118. Fits.
    # Index 41: Start 103. Len 13. Ends 115. Fits.
    # Index 48: Start 110. Len 8. Ends 117. Fits.
    # Index 55: Start 102. Len 15. Ends 116. Fits.
    # Index 62: Start 107? No, previous was ... Wait.
    
    # Let's check Index 111 (Line 112).
    # Pattern ZIZZ... Length 15.
    # Start: 102?
    # Line 112: `IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZIZZIIIIIIIIIIZII`
    # Ends with `ZII`.
    # Length of file is 119.
    # Let's count indices.
    # ...ZIZZ (4) + 10 Is + Z (1) + 2 Is.
    # 4 + 10 + 1 + 2 = 17 chars.
    # Start index?
    # Length 119. Suffix 2. Z is at 116.
    # Pattern ZIZZIIIIIIIIIIZ.
    # Z at 0, I, Z at 2, Z at 3... Z at 14.
    # If Z is at 116, start is 116 - 14 = 102.
    # 102 to 116. Fits.
    
    # So none of them wrap.
    # They are all valid Pauli strings.
    
    # Why did 10 of them fail?
    # Maybe I missed some stabilizers in the `from_stabilizers` call?
    # I passed `fixed_stabilizers`.
    # And I passed the SAME list to the tool.
    
    # Let's assume the circuit is just WRONG for those 10.
    # Why?
    # I will try to debug by checking if `stim` thinks they are satisfied.
    
    paulis = [stim.PauliString(s) for s in lines if len(s) == 119 or len(s) == 121]
    # Fix the 121 one.
    # ...
    # Then tableau = ...
    # Then check `tableau.satisfies(p)`.
    pass

if __name__ == "__main__":
    fix_wrapping()
