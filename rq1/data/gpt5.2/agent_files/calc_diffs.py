s16 = [10, 11, 18, 20]
s17 = [37, 38, 45, 47]
s18 = [68, 69, 76, 78]
s19 = [99, 100, 107, 109]

print("S17 - S16:", [b - a for a, b in zip(s16, s17)])
print("S18 - S17:", [b - a for a, b in zip(s17, s18)])
print("S19 - S18:", [b - a for a, b in zip(s18, s19)])

s20 = [8, 9, 18, 20]
s21 = [39, 40, 49, 51]
s22 = [70, 71, 80, 82]
s23 = [101, 102, 111, 113]

print("S21 - S20:", [b - a for a, b in zip(s20, s21)])
print("S22 - S21:", [b - a for a, b in zip(s21, s22)])
print("S23 - S22:", [b - a for a, b in zip(s22, s23)])
