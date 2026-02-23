import sys

with open("circuit_124_attempt.stim", "r") as f:
    content = f.read()
    sys.stdout.write(repr(content))
