
def main():
    with open('target_stabilizers_rq3_v4.txt', 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    
    print(f"Line 3: {lines[3]}")
    print(f"Line 105: {lines[105]}")
    
    import stim
    p3 = stim.PauliString(lines[3])
    p105 = stim.PauliString(lines[105])
    print(f"Commutes: {p3.commutes(p105)}")

if __name__ == "__main__":
    main()
