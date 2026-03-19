## Contributing to SIGNAL // Living README 

Welcome aboard. This repository is a living alternate reality game (ARG) that runs entirely through `README.md`, Issues, and Pull Requests.

This document explains how to:

- Submit puzzle solutions,
- Suggest lore and story twists,
- Understand the daily automation cycle.

---

### 1. Submitting a Puzzle Solution

**Step 1 — Fork or branch**

- Fork this repository, or create a branch in the main repo if you have permission.

**Step 2 — Create your solution file**

- Copy the template at `solutions/TEMPLATE.md`.
- Paste it into a new file under `solutions/`, for example:
  - `solutions/day-1-your-username.md`
- Fill in:
  - Your GitHub username,
  - The day and puzzle you’re solving (e.g. “Day 1 – Logic / Cipher Hybrid”),
  - Your reasoning (how you solved it),
  - Your final answer.

**Step 3 — Open a Pull Request**

- Commit your new file and open a PR back to this repository.
- Suggested PR title format:
  - `Day X solution by @your-username`
- Keep changes limited to:
  - Your new file under `solutions/`
  - (Optionally) tiny fixes like typo corrections, if clearly explained.

**Step 4 — Wait for the next daily run**

- Once your PR is reviewed and merged, the daily GitHub Action will:
  - Detect merged solution PRs that touch `solutions/`,
  - Treat their authors as **solvers** for that day,
  - Ask the AI narrator to credit you by GitHub username,
  - Potentially add you to the Hall of Fame in the next `README.md`.

---

### 2. Suggesting Lore and Story Twists

Want to steer the narrative? You can.

**Step 1 — Open an Issue**

- Create a new Issue with:
  - A descriptive title, ideally containing the word `lore`,
  - A clear description of your proposed twist, faction, mystery, or event.
- Example title:
  - `Lore: The relays remember a previous extinction`

**Step 2 — Label it as lore (if you can)**

- If you have permission to add labels, use a label like `lore`.
- If not, the word “lore” in the title is enough for the automation to find it.

**Step 3 — Discussion**

- Use the Issue thread to refine the idea with other players.

**Step 4 — Closure and canon**

- When the maintainers close your lore Issue as “accepted” or after discussion:
  - The next daily run will detect recently closed lore Issues,
  - It will feed those usernames and ideas into the model,
  - The narrator may incorporate them into the official story and credit you.

---

### 3. How the Daily Cycle Works

Once per day (at **09:00 UTC**) a GitHub Action runs:

1. **Checkout & setup**
   - The Action checks out the repository and sets up Python.

2. **State & activity**
   - `scripts/generate.py` reads `lore.json` (story state),
   - It queries the GitHub API (using `GITHUB_TOKEN`) to find:
     - Merged PRs touching `solutions/` (puzzle solvers),
     - Recently closed lore Issues (lore suggesters).

3. **LLM call (open-source friendly)**  
   - The script calls:
     - Groq’s `llama-3.3-70b-versatile` model first (via `GROQ_API_KEY`),
     - Falls back to Gemini `gemini-1.5-flash` (via `GEMINI_API_KEY`) if needed.
   - The model receives:
     - Story history from `lore.json`,
     - Recent solvers and lore suggesters,
     - Instructions to:
       - Advance the story,
       - Generate a new puzzle,
       - Credit contributors by GitHub username,
       - Output a new `README.md` plus updated lore metadata.

4. **Commit and push**
   - The script writes:
     - A new `README.md`,
     - An updated `lore.json`.
   - The Action commits those files with a message like:
     - `🤖 Day N update`
   - Then it pushes directly to the default branch.

Everything is driven via **environment variables and GitHub secrets**:

- `GROQ_API_KEY` — stored as a GitHub Actions secret.
- `GEMINI_API_KEY` — stored as a GitHub Actions secret.
- `GITHUB_TOKEN` — the default token granted to the workflow.
- `GITHUB_REPO` — repo identifier (`username/repo-name`), set by the workflow.

No API keys are hardcoded—ever.

---

### 4. Running Things Locally (Optional)

If you want to experiment locally:

1. Create a `.env` file based on `.env.example` and fill in:
   - `GROQ_API_KEY`
   - `GEMINI_API_KEY`
   - `GITHUB_TOKEN` (a PAT with at least `repo` scope)
   - `GITHUB_REPO` (e.g. `your-username/signal-living-readme`)

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the generator:

```bash
python scripts/generate.py
```

This will:

- Update `README.md` and `lore.json` locally,
- Using the same logic the GitHub Action uses.

---

### 5. Code of Conduct (Short Version)

- Be respectful and inclusive.
- No harassment, hate speech, or targeted abuse.
- Keep content PG-13 and suitable for a wide audience.
- Remember that your contributions become part of a public story.

If you’re unsure whether something is appropriate, err on the side of caution or open a discussion Issue first.

---

### 6. Questions & Meta

If you have questions about:

- The automation,
- The models used,
- How solvers are detected,
- Or suggestions for improving the project mechanics,

open an Issue with the `meta` keyword in the title (e.g. `Meta: scoring system idea`).

Welcome to the signal. Let’s see how long we can keep the transmission alive.

