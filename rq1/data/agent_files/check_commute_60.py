def check_commute():
    s5 = "IIIIIIIIIIIIIIIIXXIXXIIXXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII"
    s37 = "IIIIIIIIIIIIIIIIIZIIZIIIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII"
    
    anticommutes = 0
    for i, (c1, c2) in enumerate(zip(s5, s37)):
        if c1 != 'I' and c2 != 'I' and c1 != c2:
            print(f"Index {i}: {c1} vs {c2}")
            anticommutes += 1
            
    print(f"Anticommutes count: {anticommutes}")
    if anticommutes % 2 == 1:
        print("Anticommutes!")
    else:
        print("Commutes!")

if __name__ == "__main__":
    check_commute()
