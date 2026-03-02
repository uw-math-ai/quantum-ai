
def analyze_pattern():
    with open("C:\\Users\\anpaz\\Repos\\quantum-ai\\rq1\\stabilizers_161_v2.txt") as f:
        lines = [l.strip() for l in f if l.strip()]
    
    line28 = lines[28] # length 160
    line29 = lines[29] # length 161
    
    print(f"Line 28: {line28}")
    print(f"Line 29: {line29}")
    
    # Try to find the pattern from line 29
    # Line 29 has some leading Is.
    leading_Is = 0
    for char in line29:
        if char == 'I':
            leading_Is += 1
        else:
            break
    print(f"Line 29 leading Is: {leading_Is}")
    
    # Line 28 has 0 leading Is (starts with X).
    # The pattern in line 29 after leading Is seems to be:
    pattern_start = line29[leading_Is:]
    print(f"Line 29 pattern part: {pattern_start[:30]}")
    
    # Compare with line 28
    print(f"Line 28 start: {line28[:30]}")

if __name__ == "__main__":
    analyze_pattern()
