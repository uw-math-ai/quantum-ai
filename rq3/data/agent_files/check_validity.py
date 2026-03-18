import stim

def check():
    with open('candidate.stim', 'r') as f:
        content = f.read()
    
    try:
        c = stim.Circuit(content)
        print("VALID")
    except Exception as e:
        print(f"INVALID: {e}")

if __name__ == "__main__":
    check()
