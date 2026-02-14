def check():
    s5 = "IIIIIIIIIIIIIIIIXXIXXIIXXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII"
    s37 = "IIIIIIIIIIIIIIIIIZIIZIIIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII"
    
    # S5 is line 5 in my file (index 5)
    # S37 is line 37 in my file (index 37)
    
    # Let's count characters.
    print(f"S5 len: {len(s5)}")
    print(f"S37 len: {len(s37)}")
    
    # Let's check overlap carefully
    # S5 has 'X' at indices where 'XXIXXIIXXIXX' is overlaid on 'I'*16
    # So 16, 17, 19, 20, 23, 24, 26, 27 are X
    # 18, 21, 22, 25 are I
    
    # S37 has 'Z' at indices where 'ZIIZIIIZIZ' is overlaid on 'I'*17
    # So 17, 20, 24, 26 are Z?
    # Wait, 'ZIIZIIIZIZ'
    # 0: Z, 1: I, 2: I, 3: Z, 4: I, 5: I, 6: I, 7: Z, 8: I, 9: Z
    # Start index 17.
    # 17: Z
    # 18: I
    # 19: I
    # 20: Z
    # 21: I
    # 22: I
    # 23: I
    # 24: Z
    # 25: I
    # 26: Z
    
    # Let's check overlap:
    # 16: X vs I
    # 17: X vs Z (Anticommutes)
    # 18: I vs I
    # 19: X vs I
    # 20: X vs Z (Anticommutes)
    # 21: I vs I
    # 22: I vs I
    # 23: X vs I
    # 24: X vs Z (Anticommutes)
    # 25: I vs I
    # 26: X vs Z (Anticommutes)
    # 27: X vs I (wait, S37 ends at 26?)
    
    # 4 anticommutations -> They commute!
    
    # So why did Stim say they anticommute?
    # Stim output:
    # stabilizers[5] = +________________XX_XX__XX_XX________________________________
    # stabilizers[37] = +__________________Z__Z___Z_Z_________________________________
    
    # Let's compare my manual expansion with Stim's representation.
    # Stim shows non-identity Paulis.
    # S5: XX_XX__XX_XX (indices 16,17, 19,20, 23,24, 26,27). Correct.
    # S37: __Z__Z___Z_Z (indices 18, 21, 25, 27). Wait.
    # Stim says S37 is Z at 18, 21, 25, 27.
    # My manual says Z at 17, 20, 24, 26.
    
    # Ah, the shift!
    # S37 in my file starts with 17 I's? Or 18?
    # `IIIIIIIIIIIIIIIIIZIIZIIIZIZ...`
    # Let's count I's.
    # I I I I I I I I I I I I I I I I I (17 I's)
    # So Z starts at index 17.
    
    # Wait, if Stim says S37 starts at 18 (one more _), then my file has an extra I?
    # Let's check the prompt again.
    # Prompt line 37: `IIIIIIIIIIIIIIIIIZIIZIIIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII`
    # Count I's: 17.
    
    # Wait, if Stim says `stabilizers[37]` is index 37, maybe I have a different line at index 37?
    
    pass

if __name__ == "__main__":
    check()
