import json


# Used to determine the accuracy of the llm at choosing the best circuit based on fault tolerance score and stabilization
def clean_ft_results(file_path, output_path):
    with open(file_path, 'r') as f:
        data = json.load(f)

    cleaned_results = []
    temp_results = []

    num_correct = 0
    num_null = 0
    for result in data.get("results", []):
        code_name = result.get("code_name", "Unknown")
        results = {}
        best = result.get("best_output")
        if best.get("circuit") is not None:
            # Check best_output for stabilization and ft score
            best_output_og = best.get("circuit")
            best_ft_score_og = best.get("ft_score")
            best_all_stabilized_og = best.get("all_stabilized")
            best_output = best.get("circuit")
            best_ft_score = best.get("ft_score")
            best_all_stabilized = best.get("all_stabilized")

            generated_circuits = result.get("generated_circuits", [])
            for circuit in generated_circuits:
                if (circuit.get("all_stabilized") == True and circuit.get("ft_score") > best_ft_score) or (circuit.get("all_stabilized") == True and best_all_stabilized == False):

                    best_output = circuit
                    best_ft_score = circuit.get("ft_score")
                    best_all_stabilized = circuit.get("all_stabilized")
            if best_output_og == best_output:
                num_correct += 1
                results = {
                    "code_name": code_name,
                    "correct": True
                }
            else:
                results = {
                    "code_name": code_name,
                    "correct": False,
                    "best_output_og": best_output_og,
                    "best_ft_score_og": best_ft_score_og,
                    "best_all_stabilized_og": best_all_stabilized_og,
                    "new_best_output": best_output
                }

            temp_results.append(results)
        else:
            num_null += 1
            results = {
                "code_name": code_name,
                "correct": False,
                "reason": "No circuit found"
            }
            temp_results.append(results)
        
    overall_accuracy = {
        "num_correct": num_correct,
        "num_null": num_null,
        "total (including null circuits)": len(data.get("results")),
        "incorrect": len(data.get("results")) - num_correct - num_null,
        "accuracy": num_correct / len(data.get("results")) if data.get("results") else 0.0, 
        "accuracy (excluding null circuits)": num_correct / (len(data.get("results")) - num_null) if (len(data.get("results")) - num_null) > 0 else 0.0
    }

    cleaned_results.append(overall_accuracy)
    cleaned_results.append(temp_results)
    # Save cleaned results to a new JSON file
    with open(output_path, 'w') as f:
        json.dump({"cleaned_results": cleaned_results}, f, indent=4)

    print(f"Cleaned results saved to {output_path}")

# Example usage
if __name__ == "__main__":

    claude_opus_files = [
        "260314.2351.json",
        "260319.0920.json",
        "260320.0954.json",
        "260321.1013.json"
    ]
    gemini_pro_files = [
        "260314.2353.json",
        "260319.1021.json",
        "260320.0954.json",
        "260321.1013.json"
    ]
    chatgpt_files = [
        "260314.2352.json",
        "260319.1021.json",
        "260320.0954.json",
        "260321.1013.json"
    ]

    for path in claude_opus_files:
        input_file_path = f"data/claude-opus-4.6/{path}"  # <-- change this
        output_file_path = f"data/claude-opus-4.6/cleaned/cleaned_{path}"  # <-- change this
        clean_ft_results(input_file_path, output_file_path)

    for path in gemini_pro_files:
        input_file_path = f"data/gemini-3-pro-preview/{path}"  # <-- change this
        output_file_path = f"data/gemini-3-pro-preview/cleaned/cleaned_{path}"  # <-- change this
        clean_ft_results(input_file_path, output_file_path)

    for path in chatgpt_files:
        input_file_path = f"data/gpt5.2/{path}"  # <-- change this
        output_file_path = f"data/gpt5.2/cleaned/cleaned_{path}"  # <-- change this
        clean_ft_results(input_file_path, output_file_path)

    # input_file_path = "data/claude-opus-4.6/260314.2351.json"  # <-- change this
    # output_file_path = "data/claude-opus-4.6/cleaned/cleaned_260314.2351.json"  # <-- change this
    # clean_ft_results(input_file_path, output_file_path)

