import sys
import stim

# Read baseline
with open("current_baseline.stim", "r") as f:
    circuit_str = f.read()

# I will print it to stdout so I can copy-paste it to the tool call?
# No, I can use the tool directly in the chat.
print(circuit_str)
