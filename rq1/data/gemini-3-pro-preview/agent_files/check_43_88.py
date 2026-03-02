def check_43_88():
    # 43 start 123. Pattern XXXXXIXXIIIIX.
    # X indices relative to start: 0, 1, 2, 3, 4, 6, 7, 12.
    # Abs X indices: 123, 124, 125, 126, 127, 129, 130, 135.
    
    # 88 start 127. Pattern ZIZIIZIZ.
    # Z indices relative to start: 0, 2, 5, 7.
    # Abs Z indices: 127, 129, 132, 134.
    
    xs = {123, 124, 125, 126, 127, 129, 130, 135}
    zs = {127, 129, 132, 134}
    
    overlap = xs.intersection(zs)
    print(f"Overlap: {overlap}")
    # {127, 129}
    # Two overlaps -> Commutes ((-1)^2 = 1).
    
    # Wait, check check_pair output for 43 vs 88.
    pass

if __name__ == "__main__":
    check_43_88()
