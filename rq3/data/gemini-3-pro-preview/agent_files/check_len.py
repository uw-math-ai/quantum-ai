with open('current_target_stabilizers.txt', 'r') as f:
    content = f.read().replace('\n', ',')
    parts = [s.strip() for s in content.split(',') if s.strip()]
    for i, p in enumerate(parts):
        if len(p) != 81:
            print(f"Line {i}: len={len(p)}")
            print(p)
