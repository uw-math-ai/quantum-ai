import stim

def verify_indices():
    s = stim.PauliString("IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIII")
    # Length 84.
    # Last 8 are I.
    # So indices 76..83 are I.
    # Indices 72..75 are X.
    
    print(f"String representation: {s}")
    s_str = str(s)
    
    # Check what is at index 72+1
    print(f"Index 72: {s_str[73]}")
    print(f"Index 75: {s_str[76]}")
    print(f"Index 76: {s_str[77]}")
    print(f"Index 77: {s_str[78]}")
    
    # Check specific indices reported by check_pair_84.py
    # "Index 77: X vs Z"
    # This means i-1 = 77 => i = 78.
    print(f"Position 78 in string: {s_str[78]}")

if __name__ == "__main__":
    verify_indices()
