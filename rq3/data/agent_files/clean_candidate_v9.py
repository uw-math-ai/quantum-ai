import re

def clean():
    with open("candidate_extracted_v9.stim", "r") as f:
        content = f.read()
    
    # Replace RX with H
    content = re.sub(r"^RX", "H", content)
    content = re.sub(r"\nRX", "\nH", content)
    
    # Remove TICK
    content = re.sub(r"TICK\n", "", content)
    
    with open("candidate_optimized_v9.stim", "w") as f:
        f.write(content)

if __name__ == "__main__":
    clean()
