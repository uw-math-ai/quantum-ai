def main():
    with open("best_candidate.stim", "r") as f:
        content = f.read()
    
    # Replace " 105 106" with ""
    # Be careful not to replace "105" in "1050" (unlikely for qubit index)
    # But indices are space separated.
    # Pattern " 105 106" at end of line or before newline.
    
    new_content = content.replace(" 105 106", "")
    
    with open("best_candidate_v2.stim", "w") as f:
        f.write(new_content)
        
if __name__ == "__main__":
    main()
