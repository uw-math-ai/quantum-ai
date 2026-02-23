import stim

def print_stabs():
    try:
        with open("data/gemini-3-pro-preview/agent_files/stabilizers.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return

    target_length = 105
    cleaned = []
    for line in lines:
        if len(line) >= target_length:
            cleaned.append(line[:target_length])
    
    print(cleaned)

if __name__ == "__main__":
    print_stabs()
