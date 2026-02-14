def check():
    s5 = "IIIIIIIIIIIIIIIIXXIXXIIXXIXXIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII"
    s37 = "IIIIIIIIIIIIIIIIIZIIZIIIZIZIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII"
    
    print("S5 indices:")
    for i, c in enumerate(s5):
        if c != 'I':
            print(f"{i}: {c}")
            
    print("\nS37 indices:")
    for i, c in enumerate(s37):
        if c != 'I':
            print(f"{i}: {c}")

if __name__ == "__main__":
    check()
