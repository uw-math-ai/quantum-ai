
def analyze():
    with open("stabilizers.txt") as f:
        stabs = [line.strip() for line in f if line.strip()]
    
    for i, s in enumerate(stabs):
        weight = 31 - s.count('I')
        print(f"Stabilizer {i}: Weight {weight}, String: {s}")

if __name__ == "__main__":
    analyze()
