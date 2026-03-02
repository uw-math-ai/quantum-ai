with open("stabilizers_84.txt", "r") as f:
    lines = [line.strip() for line in f if line.strip()]

line23 = lines[22] # index 22 is line 23
print(f"Line 23 length: {len(line23)}")
print(f"Line 23 content: {line23}")
print(f"Line 23 'I' prefix length: {line23.find('X')}")

line35 = lines[34]
print(f"Line 35 length: {len(line35)}")
print(f"Line 35 'I' prefix length: {line35.find('X')}")

line47 = lines[46]
print(f"Line 47 length: {len(line47)}")
print(f"Line 47 'I' prefix length: {line47.find('Z')}")
