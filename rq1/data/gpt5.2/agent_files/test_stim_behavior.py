import stim

def test_stim_consistency():
    # Z and -Z are inconsistent
    try:
        stim.Tableau.from_stabilizers([stim.PauliString("Z"), stim.PauliString("-Z")], allow_underconstrained=True)
        print("Z, -Z: Success")
    except Exception as e:
        print(f"Z, -Z: Failed with {e}")

    # XX, ZZ, YY. (XX)(ZZ) = -YY. So YY is inconsistent with XX, ZZ if we want +YY.
    # XX * ZZ = -YY
    # If we ask for +XX, +ZZ, +YY. It's inconsistent.
    try:
        stim.Tableau.from_stabilizers([stim.PauliString("XX"), stim.PauliString("ZZ"), stim.PauliString("YY")], allow_underconstrained=True)
        print("XX, ZZ, YY: Success")
    except Exception as e:
        print(f"XX, ZZ, YY: Failed with {e}")

if __name__ == "__main__":
    test_stim_consistency()
