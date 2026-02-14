import stim

# The flip vectors for each candidate
# 0: {0, 14}
# 1: {0, 9}
# 2: {0, 6, 14}
# 3: {0, 6, 9}

# I want vector {0}.
# Let's represent them as bitmasks.
# But I only care about Stabs 0, 6, 9, 14.
# Let's verify if they affect ANY OTHER stabs.
# The previous script only printed "BAD" if it hit a stab other than 0.
# It didn't print WHICH one it hit if it hit 0 as well.
# Wait, "Anti-commutes with Stab 14 (BAD)" implies it hit 14.
# Let's assume these are the ONLY ones affected.
# (I should verify this assumption by running a script that checks ALL).

# Bit vectors: [Stab0, Stab6, Stab9, Stab14]
v2 =  [1, 0, 0, 1]
v5 =  [1, 0, 1, 0]
v25 = [1, 1, 0, 1]
v28 = [1, 1, 1, 0]

# Target: [1, 0, 0, 0]

# v2 + v25 = [0, 1, 0, 0] -> Flips Stab 6 only. (Let's call this O_6)
# v5 + v28 = [0, 1, 0, 0] -> Flips Stab 6 only.
# v2 + v5 = [0, 0, 1, 1] -> Flips 9 and 14.

# Let's look at v2 + v25 = {6}.
# So Z_2 * Z_25 flips ONLY Stab 6.
# Wait, Z_2 flips {0, 14}. Z_25 flips {0, 6, 14}.
# Product flips {6}. Correct.

# Now I have an operator for {6}: Z_2 * Z_25.

# Look at v5 + v28 = {6}.
# Z_5 * Z_28 flips {6}.

# How to get {0}?
# v2 = {0, 14}
# I need to cancel {14}.
# Do I have an operator for {14}?
# v25 = {0, 6, 14}
# v28 = {0, 6, 9}
# v25 + v28 = {14, 9} (since 0s cancel, 6s cancel).

# Let's try to solve: a*v2 + b*v5 + c*v25 + d*v28 = [1, 0, 0, 0]
# a(1,0,0,1) + b(1,0,1,0) + c(1,1,0,1) + d(1,1,1,0) = (1,0,0,0)

# Eq for Stab 6 (2nd comp): c + d = 0 => c = d
# Eq for Stab 9 (3rd comp): b + d = 0 => b = d
# Eq for Stab 14 (4th comp): a + c = 0 => a = c
# So a = b = c = d.
# Let's try a=b=c=d=1.
# Sum:
# v2 + v5 + v25 + v28
# Stab 0: 1+1+1+1 = 0.
# Stab 6: 0+0+1+1 = 0.
# Stab 9: 0+1+0+1 = 0.
# Stab 14: 1+0+1+0 = 0.
# Result: [0, 0, 0, 0].
# This means the product Z_2 Z_5 Z_25 Z_28 commutes with ALL (0, 6, 9, 14).
# It is a logical operator or stabilizer?
# It commutes with ALL checked so far.
# But does it anti-commute with Stab 0? No (sum is 0).

# I need sum = 1 for Stab 0.
# But the equations say a=b=c=d=1 implies sum=0 for Stab 0.
# This implies that the vector [1, 0, 0, 0] is NOT in the span of these 4 vectors?
# v2 + v5 + v25 + v28 = 0000.
# This means v2, v5, v25, v28 are linearly dependent.
# v2 = v5 + v25 + v28?
# Let's check:
# v5+v25+v28 = [1+1+1, 0+1+1, 1+0+1, 0+1+0] = [1, 0, 0, 1] = v2.
# Yes.
# So I cannot generate [1, 0, 0, 0] using just these 4.
# This means Stab 0's anti-commutation pattern is dependent on the others?
# Or maybe there is another qubit I can use?

# Stabilizer 0: IIXIIXIIIIIIIIIIIIIIIIIXIIXII
# X at 2, 5, 25, 28.
# I checked Z at these locations.

# What about Y at these locations?
# Y_2 anti-commutes with X_2 (no wait, Y and X anti-commute).
# Y anti-commutes with Z.
# If I use Y_2, it anti-commutes with X_2 (Stab 0).
# But Y_2 also anti-commutes with Z_2 (Stab 16? No, Stab 16 has Z at 2).
# Let's check Stab 16.
# IIZIIZ... (Z at 2, 5, 25, 28).
# Wait.
# Stab 16: IIZIIZIIIIIIIIIIIIIIIIIIIZIIZII
# Z at 2, 5, 25, 28.
# This is the Z-version of Stab 0!
# If I apply Y_2, it anti-commutes with Stab 0 (X_2) AND Stab 16 (Z_2).
# I don't want to flip Stab 16 (it was already True).
# Unless Stab 16 was False?
# The tool said "preserved: 29". Only Stab 0 was false.
# So Stab 16 is True. I must NOT flip it.
# So I must commute with Stab 16.
# Operators that commute with Z: I, Z.
# Operators that anti-commute with X: Z, Y.
# Intersection: Z.
# So I MUST use Z-type operators on the qubits where Stab 0 has X.
# (Or use X-type operators on qubits where Stab 0 has Z/Y/I... wait)

# Stab 0 only has X and I.
# To anti-commute with Stab 0, I must apply Z (or Y) on at least one qubit where Stab 0 has X.
# (Or apply X/Y/Z on where Stab 0 has I? No, op on I always commutes).
# So I MUST use Z (or Y) on {2, 5, 25, 28}.
# Since I must preserve Stab 16 (which has Z on {2, 5, 25, 28}), I cannot use Y (which anti-commutes with Z).
# So I MUST use Z on {2, 5, 25, 28}.

# But I found that Z_2, Z_5, Z_25, Z_28 span a subspace that does NOT include "flip only Stab 0".
# This implies that the set of Stabs {0, 6, 9, 14} has a dependency?
# Or rather, the restriction to these 4 columns {2, 5, 25, 28} allows constructing [1,0,0,1], etc.
# But not [1,0,0,0].
# This implies that `Stab 0 * Stab 6 * Stab 9 * Stab 14` involves only I/Z on these 4 qubits?
# Or rather, product of their rows in the check matrix?

# If I cannot flip only Stab 0 using single-qubit Z's, maybe I need to flip Stab 0 AND some other Stab X,
# and then use another operator to flip Stab X back?
# But that's linear algebra again. If [1,0,0,0] is not in span, I can't do it.

# Is it possible that Stab 0 is NOT independent of the others?
# If Stab 0 is product of other Stabs, then its eigenvalue is product of their eigenvalues.
# If all others are +1, and Stab 0 is -1, and Stab 0 IS a product, then we have a contradiction (impossible state).
# But the problem says "prepares the stabilizer state defined by these generators".
# This implies a valid stabilizer state exists (generators are independent and commute).
# My script said "All stabilizers commute."
# And `check_stabilizers_tool` said 29/30 correct.
# This implies the state I prepared satisfies 29 of them.
# If Stab 0 was dependent, and the others were +1, then Stab 0 SHOULD be +1 (if dependence relation says so) or -1 (if relation says so).
# If Stab 0 is -1, it means my state is WRONG for Stab 0.
# If Stab 0 is dependent on others, say S0 = S6 * S9 * S14, and S6, S9, S14 are +1, then S0 MUST be +1.
# So if S0 is -1, it means S0 is NOT S6*S9*S14?
# Or maybe S0 * S6 * S9 * S14 = -I ? (Non-trivial phase?)
# But generators usually have +1 phase.
# If the product of Pauli strings has -1 phase, then +1 eigenstate is impossible.
# But `stim` checks commutativity with signs. My script checked `stim.PauliString` commutativity.
# Let's check if the stabilizers are independent.
# If they are dependent, `from_stabilizers` would have complained or handled it.
# `tableau.from_stabilizers` makes independent generators.

# Let's check linear independence of the stabilizers.
# If they are independent, I can flip any one of them independently.
# How?
# By applying an operator that anti-commutes with S0 and commutes with others.
# Such an operator MUST exist if S0 is independent.
# Why did my search fail?
# Because I only looked for Z_2, Z_5, Z_25, Z_28.
# I restricted myself to Z on the support of S0.
# But maybe I need Z (or X) on OTHER qubits?
# S0 is X on {2, 5, 25, 28} and I elsewhere.
# To anti-commute with S0, I need an operator P such that P and S0 anti-commute.
# Commutation: counts overlap of X/Z.
# S0 has X. I need Z (or Y) on those positions.
# OR S0 has I. I can put whatever there?
# No, if S0 has I, any P (X, Y, Z) there COMMUTES with I.
# So anti-commutativity MUST come from the support of S0.
# So I MUST have odd number of anti-commuting terms on {2, 5, 25, 28}.
# Terms that anti-commute with X are Z and Y.
# So I need odd number of Z/Y on {2, 5, 25, 28}.
# And I established I cannot use Y because of S16.
# So I need odd number of Z's on {2, 5, 25, 28}.
# Z_2 is one Z. It worked (anti-commuted with S0).
# But it also anti-commuted with S14.
# I need to fix the S14 anti-commutation.
# S14 has X on 2. And X on other places.
# To fix S14, I can multiply by an operator that anti-commutes with S14 and commutes with S0.
# Operator to flip S14?
# I can look for Z on support of S14 (excluding {2,5,25,28} if I want to preserve S0 commutativity).
# Support of S14:
# IIXIIIIIIIIIIIIIIXIXIIIIIXIIIII
# X at 2.
# X at 17?
# Let's check S14 indices.
