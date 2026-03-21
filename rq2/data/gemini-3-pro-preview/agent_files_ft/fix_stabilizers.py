def main():
    with open('data/gemini-3-pro-preview/agent_files_ft/stabilizers.txt', 'r') as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]

    if not lines:
        return
        
    max_len = max(len(s) for s in lines)
    print(f"Max length: {max_len}")
    
    padded_lines = []
    for s in lines:
        if len(s) < max_len:
            s = s + 'I' * (max_len - len(s))
        padded_lines.append(s)
        
    with open('data/gemini-3-pro-preview/agent_files_ft/stabilizers_fixed.txt', 'w') as f:
        for s in padded_lines:
            f.write(s + '\n')
            
    print(f"Saved {len(padded_lines)} stabilizers of length {max_len} to stabilizers_fixed.txt")

if __name__ == "__main__":
    main()
