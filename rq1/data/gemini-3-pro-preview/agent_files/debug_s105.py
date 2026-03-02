import solve_105_new
import numpy as np

s = solve_105_new.stabilizers
print(f"S0:  {s[0]}")
print(f"S45: {s[45]}")

def check(s1, s2):
    cnt = 0
    for i in range(len(s1)):
        c1 = s1[i]
        c2 = s2[i]
        if c1 != 'I' and c2 != 'I' and c1 != c2:
            cnt += 1
    print(f"Anticommuting positions: {cnt}")
    return cnt % 2 == 1

print(f"Commute? {not check(s[0], s[45])}")
