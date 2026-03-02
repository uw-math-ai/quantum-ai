import json
from solve_95_fresh import stabilizers

def main():
    try:
        with open("circuit_95_fresh.stim", "r") as f:
            circuit = f.read()

        print(json.dumps({
            "circuit": circuit,
            "stabilizers": stabilizers
        }))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

