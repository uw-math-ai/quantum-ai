with open('current_task_stabilizers.txt', 'r') as f:
    line = f.readline().strip()
    print(f'Line length: {len(line)}')
    print(f'Line content: {repr(line)}')
