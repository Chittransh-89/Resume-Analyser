import re
import json
import asyncio
import httpx
import os
from config import GROQ_API_KEY, MODEL

def split_into_chunks(items, size=5):
    return [items[i:i+size] for i in range(0, len(items), size)]

def flatten(list_of_lists):
    return [item for sublist in list_of_lists for item in sublist]

# ✅ Top 5 suggestions nikalo (optional but recommended)
def get_top_suggestions(suggestions, top_n=5):
    # Sabse lambi/meaningful suggestions pehle
    sorted_suggestions = sorted(suggestions, key=len, reverse=True)
    return sorted_suggestions[:top_n]

def extract_bullets_from_text(text):
    lines = text.split("\n")
    bullets = []

    header_words = [
        "skills", "education", "experience",
        "projects", "contact", "summary", "objective"
    ]

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Remove PDF artifacts
        line = re.sub(r"\(cid:\d+\)", "", line).strip()
        lower_line = line.lower()

        # Skip professional summary title
        if lower_line in ["professional summary", "summary"]:
            continue

        # Skip job header lines
        if "|" in line and any(month in lower_line for month in [
            "jan","feb","mar","apr","may","jun",
            "jul","aug","sep","oct","nov","dec"
        ]):
            continue

        # Skip education lines
        if "b.tech" in lower_line or "university" in lower_line:
            continue

        # Skip course lines
        if "course" in lower_line:
            continue

        # Skip contact info
        if "@" in line:
            continue

        if "|" in line and any(x in lower_line for x in ["linkedin", "github"]):
            continue

        # Skip broken summary continuation
        if lower_line.islower() and lower_line.endswith(("and", "who", "of")):
            continue

        # Skip section headers
        if any(lower_line.startswith(h) for h in header_words):
            continue

        # Skip skill list
        if line.count(",") > 5:
            continue

        # Skip very short lines (but allow meaningful ones)
        if len(line.split()) <= 3 and lower_line.islower():
            continue

        # Keep bullets
        if line.startswith(("-", "•", "*", "–", "▪")):
            bullets.append(line.lstrip("-•*–▪ ").strip())
        else:
            bullets.append(line)

    return bullets


async def async_llm_call(prompt, temperature=0.3):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You ONLY return valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature
    }

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            print("HTTP ERROR:", response.status_code, response.text)
            return None

        data = response.json()

        if "choices" not in data:
            print("GROQ STRUCTURE ERROR:", data)
            return None

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print("ASYNC LLM CALL FAILED:", str(e))
        return None

from pathlib import Path

# def load_prompt(filename: str) -> str:
#     prompt_path = Path(__file__).parent / "prompts" / filename
#     return prompt_path.read_text(encoding="utf-8")

def load_prompt(filename: str) -> str:
    """
    Load prompt from txt file
    
    Args:
        filename: prompt file name (e.g. "llm_review_prompt.txt")
    
    Returns:
        Prompt string
    """
    prompt_path = Path(__file__).parent / "prompts" / filename
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    
    template = prompt_path.read_text(encoding="utf-8")
    placeholders = re.findall(r"\{(\w+)\}", template)
    print("Template placeholders:", placeholders)
    return prompt_path.read_text(encoding="utf-8")

async def improve_chunk(bullets, jd_text):

    bullets_text = "\n".join(
        f"{i+1}. {b}" for i, b in enumerate(bullets)
    )
    template = load_prompt("improve_bullets_prompt.txt")

    prompt = template.format(
        jd_text=str(jd_text[:2000]),
        bullets_text=bullets_text
    )
    try:
        result = await async_llm_call(prompt)

        if not result or not result.strip():
            raise ValueError("Empty LLM response")

        import re
        match = re.search(r"\[.*\]", result, re.DOTALL)

        if not match:
            print("INVALID RESPONSE:", result)
            raise ValueError("No JSON found")

        clean_json = match.group(0)

        parsed = json.loads(clean_json)

        # if len(parsed) != len(bullets):
        #     raise ValueError("Bullet count mismatch")

        return parsed
    except Exception as e:
        print("IMPROVE ERROR:", str(e))
        return [{"original": b, "improved": b} for b in bullets]


# async def improve_all_bullets(
#     resume_json: dict,
#     jd_json:     dict
# ) -> list[dict]:
#     """
#     Extract → Chunk → Async Parallel Improve → Flatten
#     """
#     bullets = extract_bullets(resume_json)

#     if not bullets:
#         return []

#     chunks = split_into_chunks(bullets, size=5)
#     tasks  = [improve_chunk(chunk, jd_json) for chunk in chunks]
#     results = await asyncio.gather(*tasks)

#     return flatten(results)