
s1 = "XXXXIIXIIXXIIIIIIXIIIII" # from block stab 4
s2 = "IZIIZIIZZZZZIIIIIIIIIIZ" # from block stab 11 (original stab 66)

# s1 indices:
# 0: X
# 1: X
# 2: X
# 3: X
# 4: I
# 5: I
# 6: X
# 7: I
# 8: I
# 9: X
# 10: X
# 11: I
# 12: I
# 13: I
# 14: I
# 15: I
# 16: I
# 17: X
# 18: I
# 19: I
# 20: I
# 21: I
# 22: I

# s2 indices:
# 0: I
# 1: Z
# 2: I
# 3: I
# 4: Z
# 5: I
# 6: I
# 7: Z
# 8: Z
# 9: Z
# 10: Z
# 11: Z
# 12: I
# 13: I
# 14: I
# 15: I
# 16: I
# 17: I
# 18: I
# 19: I
# 20: I
# 21: I
# 22: Z

# Overlap:
# 1: X vs Z -> Anti
# 9: X vs Z -> Anti
# 10: X vs Z -> Anti

# Total 3 anti-commuting pairs.
# So they anti-commute.

print("Confirmed anti-commutation.")
