import re
import sys

def normalize(input_file, output_file):
    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
        
        normalized_lines = []
        current_line = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line starts with a command (letter) or is a continuation (number)
            is_start_of_command = line[0].isalpha()
            
            if is_start_of_command:
                if current_line:
                    normalized_lines.append(current_line)
                current_line = line
            else:
                # Continuation
                if current_line:
                    current_line += " " + line
                else:
                    # Should not happen if file starts with command
                    current_line = line
                
        if current_line:
            normalized_lines.append(current_line)
            
        with open(output_file, 'w') as f:
            for line in normalized_lines:
                f.write(line + "\n")
        print("Normalization complete.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    normalize("data/gemini-3-pro-preview/agent_files_ft/candidate_fixed.stim", "data/gemini-3-pro-preview/agent_files_ft/candidate_normalized.stim")
