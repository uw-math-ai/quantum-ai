s_tool = "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIXIIXIIIIIIIIIIIIIIIIIIIII"

with open("stabilizers_54_v2.txt", "r") as f:
    lines = [l.strip() for l in f if l.strip()]
    
s_file = lines[15]

print(f"Tool string len: {len(s_tool)}")
print(f"File string len: {len(s_file)}")

if s_tool == s_file:
    print("Strings MATCH perfectly.")
else:
    print("Strings DIFFER!")
    print(f"Tool: {s_tool}")
    print(f"File: {s_file}")
