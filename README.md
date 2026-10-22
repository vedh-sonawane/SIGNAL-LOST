# 📡 Transmission Log – Day 201 of ∞

> **Warning:** The orbital relay network shivers in the encroaching void. The Atbash cipher left us blind, and without a beacon the darkness threatens to swallow our signal entirely.  
> *Proceed with caution; every byte counts.*

---

## How to Play

1. **Read** the entire README – every clue, hint, and instruction is part of the transmission.  
2. **Solve** the daily puzzle (type rotates: coding → cipher → riddle → logic).  
3. **Submit** your solution by opening a Pull Request that adds a file under `solutions/` based on `solutions/TEMPLATE.md`.  
4. **Suggest** new lore twists, hidden relays, or alternate histories by opening an Issue.  
5. **Tomorrow’s README** will credit today’s solvers and lore contributors by GitHub username.

---

### Day 201 Puzzle — **coding**

The network’s core processor has been rebooted, but it lacks a verification routine. Write a **Python** function named `relay_checksum` that accepts a single argument `message` (a string of **UPPERCASE** letters, no spaces) and returns an integer calculated as follows:

1. Determine the alphabetical index of each character (`A=1`, `B=2`, … `Z=26`).  
2. Sum those indices.  
3. Multiply the sum by the total length of `message`.  

**Example:**  
```python
relay_checksum("STABLE")  # (19+20+1+2+12+5) * 6 = 59 * 6 = 354
```

Submit a file `solutions/your_username.md` containing the implementation and a brief explanation of how it works.

---

## Community Guidelines

- **Solutions** must be added under `solutions/` using the provided `TEMPLATE.md`.  
- **Lore suggestions** belong in Issues; keep them concise and thematic.  
- **Credits**: Tomorrow’s transmission will list the usernames of anyone whose solution or lore suggestion is merged.

---

## Hall of Fame

*No entries yet.*  

> *When the first signal pierces the darkness, their names will be etched here.*

---

## Credits

- **New Solvers (Day 201):** *None yet – the void awaits your code.*  
- **Lore Suggesters (Day 201):** *None yet – whisper your ideas in the Issues.*  

---
