def check_line_71():
    with open("stabilizers_84_fixed.txt", "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    
    line71 = lines[71]
    print(f"Line 71: {line71}")
    print(f"Length: {len(line71)}")
    
    # Check if this matches the "failed" string from tool output
    failed_str = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIZZZZIIIIIIII"
    if line71 == failed_str:
        print("MATCHES failed string")
    else:
        print("DOES NOT MATCH failed string")
        
    # Maybe check neighbors
    print(f"Line 70: {lines[70]}")
    print(f"Line 72: {lines[72]}")

if __name__ == "__main__":
    check_line_71()
