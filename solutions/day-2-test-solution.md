---
day: 2
solver: vedh-sonawane
date: 2025-03-18
solution: "binary_to_ascii_decoder"
puzzle_type: code
---

# Day 2 Solution - Binary Decoder

## My Approach
Convert binary strings to ASCII characters.

## Solution
```python
def decode_relay_message(message):
    # Split into 8-bit chunks
    chunks = [message[i:i+8] for i in range(0, len(message), 8)]
    
    # Convert each chunk to character
    decoded = ''.join([chr(int(chunk, 2)) for chunk in chunks])
    
    return decoded

# Test
print(decode_relay_message("10101010"))
```

## Explanation
Binary "10101010" = ASCII 170 = character '*'
---
**Solver:** @vedh-sonawane
