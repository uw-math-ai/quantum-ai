import sys

chunk = int(sys.argv[1])
size = 20000

with open("solution.stim", "r") as f:
    text = f.read()
    
start = (chunk - 1) * size
end = start + size

if start < len(text):
    print(text[start:end], end="")
