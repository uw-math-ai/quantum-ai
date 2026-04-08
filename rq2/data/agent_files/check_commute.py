import json

stabs_str = "XZZXIIIIIIIIIIIIIIIIIIIII, IIIIIXZZXIIIIIIIIIIIIIIII, IIIIIIIIIIXZZXIIIIIIIIIII, IIIIIIIIIIIIIIIXZZXIIIIII, IIIIIIIIIIIIIIIIIIIIXZZXI, IXZZXIIIIIIIIIIIIIIIIIIII, IIIIIIXZZXIIIIIIIIIIIIIII, IIIIIIIIIIIXZZXIIIIIIIIII, IIIIIIIIIIIIIIIIXZZXIIIII, IIIIIIIIIIIIIIIIIIIIIXZZX, XIXZZIIIIIIIIIIIIIIIIIIII, IIIIIXIXZZIIIIIIIIIIIIIII, IIIIIIIIIIXIXZZIIIIIIIIII, IIIIIIIIIIIIIIIXIXZZIIIII, IIIIIIIIIIIIIIIIIIIIXIXZZ, ZXIXZIIIIIIIIIIIIIIIIIIII, IIIIIZXIXZIIIIIIIIIIIIIII, IIIIIIIIIIZXIXZIIIIIIIIII, IIIIIIIIIIIIIIIZXIXZIIIII, IIIIIIIIIIIIIIIIIIIIZXIXZ, XXXXXZZZZZZZZZZXXXXXIIIII, IIIIIXXXXXZZZZZZZZZZXXXXX, XXXXXIIIIIXXXXXZZZZZZZZZZ, ZZZZZXXXXXIIIIIXXXXXZZZZZ"
stabs = [s.strip() for s in stabs_str.split(',')]

# Error from validation output (loc 17, CX 0)
# "0": "Z", "1": "Y", "2": "X", "3": "I", "4": "X", "5": "Z", "6": "Z", "7": "Z", "8": "Z", "9": "Z", "10": "X", "11": "Z", "12": "Z", "13": "X", "14": "I", "15": "X", "16": "Y", "17": "I", "18": "Y", "19": "X", "20": "Z", "21": "I", "22": "X", "23": "X", "24": "I"
error_dict = {"0": "Z", "1": "Y", "2": "X", "3": "I", "4": "X", "5": "Z", "6": "Z", "7": "Z", "8": "Z", "9": "Z", "10": "X", "11": "Z", "12": "Z", "13": "X", "14": "I", "15": "X", "16": "Y", "17": "I", "18": "Y", "19": "X", "20": "Z", "21": "I", "22": "X", "23": "X", "24": "I"}

def pauli_commute(p1, p2):
    if p1 == 'I' or p2 == 'I': return True
    if p1 == p2: return True
    return False # Anti-commute (e.g. X, Z)

def check_commutation(stab_str, err_dict):
    anticommutes = 0
    for i in range(25):
        s_p = stab_str[i]
        e_p = err_dict.get(str(i), 'I')
        if not pauli_commute(s_p, e_p):
            anticommutes += 1
    return (anticommutes % 2) == 0

print("Commutation results for Error A:")
for i, s in enumerate(stabs):
    commutes = check_commutation(s, error_dict)
    if not commutes:
        print(f"Stabilizer {i} ({s}) ANTI-COMMUTES")
