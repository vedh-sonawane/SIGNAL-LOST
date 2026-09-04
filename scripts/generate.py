import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv
from github import Auth, Github  # pyright: ignore[reportMissingImports]

try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


load_dotenv()


LORE_PATH = Path("lore.json")
README_PATH = Path("README.md")
ANSWERS_PATH = Path("data/answers.json")


def load_lore() -> Dict[str, Any]:
    if not LORE_PATH.exists():
        return {
            "day": 1,
            "story_summary": "",
            "last_challenge": "",
            "last_challenge_type": "",
            "last_challenge_solved": False,
            "total_solvers": 0,
            "solver_hall_of_fame": [],
        }
    return json.loads(LORE_PATH.read_text(encoding="utf-8"))


def save_lore(lore: Dict[str, Any]) -> None:
    LORE_PATH.write_text(json.dumps(lore, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_answers() -> Dict[str, Any]:
    """Load existing answers from data/answers.json"""
    if not ANSWERS_PATH.exists():
        return {}
    return json.loads(ANSWERS_PATH.read_text(encoding="utf-8"))


def save_answer(day: int, puzzle_type: str, answer: Optional[str], hints: List[str]) -> None:
    """Save answer for a specific day to data/answers.json"""
    answers = load_answers()
    
    day_key = f"day_{day}"
    answers[day_key] = {
        "type": puzzle_type,
        "answer": answer if answer else "",
        "hint_1": hints[0] if len(hints) > 0 else "Think carefully about the problem...",
        "hint_2": hints[1] if len(hints) > 1 else "Review the puzzle description...",
        "hint_3": hints[2] if len(hints) > 2 else "You're very close to the solution..."
    }
    
    # Save back to file
    ANSWERS_PATH.parent.mkdir(exist_ok=True)
    ANSWERS_PATH.write_text(json.dumps(answers, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def get_github_client() -> Github:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN environment variable is required.")
    auth = Auth.Token(token)
    return Github(auth=auth)


def get_repo(g: Github):
    repo_name = os.environ.get("GITHUB_REPO")
    if not repo_name:
        raise RuntimeError("GITHUB_REPO environment variable is required (e.g. username/repo-name).")
    return g.get_repo(repo_name)


def get_recent_activity() -> Tuple[List[str], List[str]]:
    """
    Returns (solver_usernames, lore_suggester_usernames) from the last 24 hours.
    - Solvers: authors of merged PRs that touch the solutions/ directory.
    - Lore suggesters: authors of closed issues labeled 'lore' or with 'lore' in the title.
    """
    g = get_github_client()
    repo = get_repo(g)

    now = datetime.now(timezone.utc)
    since = now - timedelta(days=1)

    solvers = set()
    lore_suggesters = set()

    # Find merged PRs in last 24h
    for pr in repo.get_pulls(state="closed", sort="updated", direction="desc"):
        if not pr.merged:
            continue
        if pr.merged_at is None or pr.merged_at < since:
            # PRs are returned sorted by updated desc; we can break once older than since
            if pr.merged_at and pr.merged_at < since:
                break
            continue
        try:
            files = list(pr.get_files())
        except Exception:
            files = []
        touches_solutions = any(f.filename.startswith("solutions/") for f in files)
        if touches_solutions and pr.user:
            solvers.add(pr.user.login)

    # Find closed issues in last 24h that suggest lore
    for issue in repo.get_issues(state="closed", sort="updated", direction="desc"):
        if issue.pull_request is not None:
            continue
        if issue.closed_at is None or issue.closed_at < since:
            if issue.closed_at and issue.closed_at < since:
                break
            continue
        labels = {lbl.name.lower() for lbl in issue.labels}
        title = (issue.title or "").lower()
        if "lore" in labels or "lore" in title:
            if issue.user:
                lore_suggesters.add(issue.user.login)

    return sorted(solvers), sorted(lore_suggesters)


def build_system_prompt() -> str:
    return """You are the cryptic narrator of an evolving sci-fi alternate reality game (ARG)
that lives entirely inside a GitHub repository's README.

Every day, you advance the story, present a new puzzle, and credit the community
members who solved yesterday's challenge or suggested lore.

Strict output format (VERY IMPORTANT):
1) First, output ONLY a complete README in Markdown.
2) Then, on a new line, output a fenced JSON block of the form:
```json
{
  "day": <integer>,
  "story_summary": "<short recap of the story so far>",
  "last_challenge": "<one-paragraph description of today's puzzle>",
  "last_challenge_type": "coding|cipher|riddle|logic",
  "last_challenge_solved": <true|false>,
  "new_solvers": ["github-username-1", "github-username-2"],
  "hall_of_fame_additions": ["github-username-1", "github-username-2"],
  "puzzle_answer": "<the correct answer to today's puzzle>",
  "puzzle_hints": ["hint 1", "hint 2", "hint 3"]
}
```

CRITICAL: You MUST include "puzzle_answer" and "puzzle_hints" in your JSON response.
- For cipher puzzles: puzzle_answer should be the decoded plaintext
- For coding puzzles: puzzle_answer should be a description of what the code should do
- For logic/riddle puzzles: puzzle_answer should be the exact answer

Do not include any other commentary outside the README and the JSON block."""


def build_user_prompt(
    lore: Dict[str, Any],
    solvers: List[str],
    lore_suggesters: List[str],
) -> str:
    day = lore.get("day", 1)
    story_summary = lore.get("story_summary", "") or ""
    last_challenge = lore.get("last_challenge", "") or ""
    last_type = lore.get("last_challenge_type", "") or ""
    last_solved = bool(lore.get("last_challenge_solved", False))
    total_solvers = lore.get("total_solvers", 0)
    hall_of_fame = lore.get("solver_hall_of_fame", []) or []

    parts = [
        f"Today is Day {day} of the ARG.",
        "",
        "Existing story summary:",
        story_summary or "(no story yet — this is the first transmission).",
        "",
        "Yesterday's challenge:",
        last_challenge or "(none, this is the first challenge).",
        f"Yesterday's challenge type: {last_type or 'n/a'}",
        f"Was yesterday's challenge solved? {'yes' if last_solved else 'no'}",
        "",
        f"Total unique solvers so far: {total_solvers}",
        f"Current Hall of Fame usernames: {', '.join(hall_of_fame) if hall_of_fame else '(empty)'}",
        "",
        "New activity from the last 24 hours:",
        f"- Potential solvers (merged PRs touching solutions/): {', '.join(solvers) if solvers else '(none)'}",
        f"- Lore suggesters (closed lore issues): {', '.join(lore_suggesters) if lore_suggesters else '(none)'}",
        "",
        "Narrative and tone rules:",
        "- The setting is a slowly awakening, possibly hostile, network of orbital signal relays.",
        "- The README is written as a cryptic transmission being received by visitors to the repo.",
        "- If yesterday's puzzle was UNSOLVED, slightly darken the tone and raise the stakes.",
        "- If it was solved, reward the community with subtle progress and recognition.",
        "",
        "Puzzle rules:",
        "- Generate EXACTLY one new puzzle for today.",
        "- Rotate the puzzle type daily between: coding challenge, cipher, riddle, and logic puzzle.",
        "- The puzzle must be solvable by reading the README alone.",
        "- Make the puzzle clearly labeled (e.g. '### Day X Puzzle — <type>').",
        "- IMPORTANT: In your JSON response, include the correct answer to the puzzle you create.",
        "- IMPORTANT: In your JSON response, include 3 progressive hints for the puzzle.",
        "",
        "Community rules (must be clearly spelled out in the README):",
        "- Players submit solutions by opening a Pull Request that adds a file under solutions/ based on solutions/TEMPLATE.md.",
        "- Players can suggest new lore twists by opening Issues.",
        "- Tomorrow's README must credit today's solvers and notable lore suggestions by GitHub username.",
        "",
        "In the README you generate now, you MUST:",
        f"- Show a visible counter like 'Day {day} of ∞'.",
        "- Include a 'How to Play' section with clear instructions.",
        "- Include or update a 'Hall of Fame' section listing credited solvers by username.",
        "- Credit today's new solvers and lore suggesters by username somewhere prominent.",
        "",
        "Remember: At the very end of your response, provide the JSON lore_state block exactly as specified in the system message, INCLUDING puzzle_answer and puzzle_hints.",
    ]

    return "\n".join(parts)


def call_groq(system_prompt: str, user_prompt: str) -> str:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
    "model": "openai/gpt-oss-120b",   # was: llama-3.3-70b-versatile (deprecated)
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ],
    "temperature": 0.9,
    "max_tokens": 2500,
}
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def call_gemini(system_prompt: str, user_prompt: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")

    if not GENAI_AVAILABLE:
        raise RuntimeError("google.genai package not installed. Please add google-genai to requirements.txt")

    client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
        model="models/gemini-2.5-flash",   # free-tier eligible; Pro models are not
        contents=[
            {"role": "user", "parts": [{"text": system_prompt + "\n\n---\n\n" + user_prompt}]}
        ]
    )
    return response.text


def call_model(system_prompt: str, user_prompt: str) -> str:
    last_error: Optional[Exception] = None

    try:
        return call_groq(system_prompt, user_prompt)
    except Exception as e:
        last_error = e

    try:
        return call_gemini(system_prompt, user_prompt)
    except Exception as e:
        last_error = e

    raise RuntimeError(f"Both Groq and Gemini calls failed: {last_error}")


def parse_model_output(raw: str) -> Tuple[str, Dict[str, Any]]:
    """
    Splits the model output into (readme_markdown, lore_state_dict).
    Expects a ```json ... ``` fenced block containing the lore JSON.
    """
    start = raw.find("```json")
    if start == -1:
        raise ValueError("Model output missing ```json block.")
    end = raw.find("```", start + 7)
    if end == -1:
        raise ValueError("Model output has unterminated ```json block.")

    readme = raw[:start].strip()
    json_str = raw[start + len("```json"): end].strip()

    lore_state = json.loads(json_str)
    return readme, lore_state


def merge_lore(old: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    # Base fields
    new_day = int(update.get("day", old.get("day", 1)))
    story_summary = update.get("story_summary", old.get("story_summary", ""))
    last_challenge = update.get("last_challenge", old.get("last_challenge", ""))
    last_type = update.get("last_challenge_type", old.get("last_challenge_type", ""))
    last_solved = bool(update.get("last_challenge_solved", old.get("last_challenge_solved", False)))

    old_hof = set(old.get("solver_hall_of_fame", []) or [])
    total_solvers = int(old.get("total_solvers", 0))

    new_solvers = list(update.get("new_solvers", []))
    hof_additions = list(update.get("hall_of_fame_additions", []))

    # Update counts and hall of fame
    for username in new_solvers:
        if username not in old_hof:
            total_solvers += 1
    updated_hof = sorted(old_hof.union(hof_additions))

    return {
        "day": new_day,
        "story_summary": story_summary,
        "last_challenge": last_challenge,
        "last_challenge_type": last_type,
        "last_challenge_solved": last_solved,
        "total_solvers": total_solvers,
        "solver_hall_of_fame": updated_hof,
    }


def main() -> None:
    lore = load_lore()
    solvers, lore_suggesters = get_recent_activity()

    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(lore, solvers, lore_suggesters)

    raw = call_model(system_prompt, user_prompt)
    readme, lore_state = parse_model_output(raw)

    # Write README
    README_PATH.write_text(readme.strip() + "\n", encoding="utf-8")

    # Extract and save puzzle answer automatically
    puzzle_answer = lore_state.get("puzzle_answer")
    puzzle_hints = lore_state.get("puzzle_hints", [])
    puzzle_type = lore_state.get("last_challenge_type", "")
    current_day = lore_state.get("day", lore.get("day", 1))
    
    # Save answer to data/answers.json
    if puzzle_answer or puzzle_type:
        save_answer(
            day=current_day,
            puzzle_type=puzzle_type,
            answer=puzzle_answer,
            hints=puzzle_hints if puzzle_hints else []
        )

    # Merge and save lore
    merged = merge_lore(lore, lore_state)
    # Increment day for next run if model didn't already
    if merged.get("day", 1) <= lore.get("day", 1):
        merged["day"] = int(lore.get("day", 1)) + 1
    save_lore(merged)


if __name__ == "__main__":
    main()
