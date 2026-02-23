def check_shift_18():
    # If shift is 18
    # Line 34: Start 128. Xs: 128, 132, 140, 142.
    # Line 79: Start 131. Zs: 131, 135, 137, 138.
    
    xs = {128, 132, 140, 142}
    zs = {131, 135, 137, 138}
    
    overlap = xs.intersection(zs)
    print(f"Overlap with shift 18: {overlap}")
    
    # But wait, the file clearly has shift 17 visually.
    # Line 36: IIIIXXXX... (index 4)
    # Line 37: IIII...XXXX... (index 21)
    # 21 - 4 = 17.
    # The file content itself shows shift 17.
    
    pass

if __name__ == "__main__":
    check_shift_18()
