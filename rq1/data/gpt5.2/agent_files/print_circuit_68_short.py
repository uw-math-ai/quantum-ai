import stim

circuit = stim.Circuit.from_file(r"C:\Users\anpaz\Repos\quantum-ai\rq1\circuit_68_short_lines.stim")
for instruction in circuit:
    print(instruction)
