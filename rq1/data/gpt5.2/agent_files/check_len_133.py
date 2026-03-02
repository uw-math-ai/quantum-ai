with open("stabilizers_133.txt", "r") as f:
    lines = [l.strip() for l in f if l.strip()]
print(f"First line length: {len(lines[0])}")
print(f"Last line length: {len(lines[-1])}")

bad = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIXXXXIIIIIIIIIIIIIIIIIIIII"
print(f"Bad string length: {len(bad)}")
