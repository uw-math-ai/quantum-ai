import textwrap

with open("candidate.stim", "r") as f:
    content = f.read()

# Stim allows newlines anywhere whitespace is allowed.
# We can wrap the text to be safe.
# But we should preserve existing newlines if they are important (e.g. for readability, though Stim doesn't care except for # comments)
# The file has some structure.
# We'll read lines, and wrap each line.

lines = content.splitlines()
formatted_lines = []
for line in lines:
    # Wrap at 80 chars, but break on spaces
    wrapped = textwrap.fill(line, width=80, break_long_words=False, break_on_hyphens=False)
    formatted_lines.append(wrapped)

print("\n".join(formatted_lines))
