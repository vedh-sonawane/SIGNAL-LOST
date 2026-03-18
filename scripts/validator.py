#!/usr/bin/env python3
import sys
import re
import json
from pathlib import Path

def load_answers():
    """Load all answers from data/answers.json"""
    answers_file = Path('data/answers.json')
    if answers_file.exists():
        with open(answers_file, 'r') as f:
            return json.load(f)
    return {}

def validate_solution(filepath):
    """Validate any day's solution automatically"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Extract day number
        day_match = re.search(r'day:\s*(\d+)', content)
        if not day_match:
            print("❌ NO DAY NUMBER FOUND")
            return False
        
        day = int(day_match.group(1))
        
        # Extract solution
        solution_match = re.search(r'solution:\s*["\'](.+?)["\']', content, re.DOTALL)
        if not solution_match:
            print("❌ NO SOLUTION FOUND")
            return False
        
        solution = solution_match.group(1).strip()
        
        # Load answers
        answers = load_answers()
        day_key = f"day_{day}"
        
        if day_key not in answers:
            print(f"⚠️ NO ANSWER CONFIGURED FOR DAY {day}")
            return False
        
        day_data = answers[day_key]
        puzzle_type = day_data.get("type", "cipher")
        
        # Validate based on type
        if puzzle_type == "cipher":
            correct_answer = day_data.get("answer", "")
            
            # Normalize
            sol_clean = re.sub(r'[^a-z0-9]', '', solution.lower())
            ans_clean = re.sub(r'[^a-z0-9]', '', correct_answer.lower())
            
            if sol_clean == ans_clean:
                print(f"🎯 CORRECT! Day {day} cipher solved!")
                return True
            else:
                print(f"❌ WRONG! Expected: {correct_answer}")
                return False
        
        elif puzzle_type == "code":
            # For code puzzles, just check if they provided code
            code_match = re.search(r'```python\n(.*?)\n```', content, re.DOTALL)
            if code_match:
                print(f"✅ CODE FOUND for Day {day}!")
                # In a full implementation, run test cases here
                return True
            else:
                print("❌ NO CODE BLOCK FOUND")
                return False
        
        elif puzzle_type == "logic":
            correct_answer = day_data.get("answer", "")
            if solution.strip().lower() == correct_answer.lower():
                print(f"🎯 CORRECT! Day {day} logic puzzle solved!")
                return True
            else:
                print(f"❌ WRONG!")
                return False
        
        else:
            print(f"⚠️ UNKNOWN PUZZLE TYPE: {puzzle_type}")
            return False
    
    except Exception as e:
        print(f"🔥 ERROR: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validator.py <solution_file>")
        sys.exit(1)
    
    is_valid = validate_solution(sys.argv[1])
    sys.exit(0 if is_valid else 1)