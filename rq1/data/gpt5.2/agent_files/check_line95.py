with open(r"C:\Users\anpaz\Repos\quantum-ai\rq1\solve_105_new.py", "r") as f:
    lines = f.readlines()
    # stabilizers start at line 5 (index 4)
    # line 95 is line index 94?
    # No, I see line numbers in view.
    # Line 95 in view is index 94.
    s = lines[94].strip()
    # remove comma and quotes
    s = s.strip(',').strip('"')
    print(f"Line 95: {len(s)}")
    print(s)
