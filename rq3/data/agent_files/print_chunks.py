def main():
    with open("data/safe_candidate.stim", "r") as f:
        lines = f.readlines()
    
    chunk_size = 100
    for i in range(0, len(lines), chunk_size):
        print(f"--- CHUNK {i} ---")
        print("".join(lines[i:i+chunk_size]), end="")
        print("--- END CHUNK ---")

if __name__ == "__main__":
    main()
