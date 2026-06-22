import json
from config import groq_client, MODEL
import re
from pathlib import Path

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

def llm_review(
    resume_json:     dict,
    jd_json:         dict,
    final_score:      float,
    matched_skills:  list,
    missing_skills:  list
) -> dict:
    """
    Final LLM Review → Adjust Score + Reasoning
    """
    
    # ✅ Load prompt from txt file
    template = load_prompt("review_prompt.txt")
    
    # ✅ Fill placeholders
    prompt = template.format(
        jd_json = jd_json,
        job_title           = jd_json.get("job_title", ""),
        required_skills     = jd_json.get("required_skills", []),
        responsibilities    = jd_json.get("responsibilities", []),
        candidate_skills    = resume_json.get("skills", []),
        candidate_experience = [e.get("role") for e in resume_json.get("experience", [])],
        candidate_projects  = [p.get("name") for p in resume_json.get("projects", [])],
        final_score=round(final_score, 2),
        matched_skills      = matched_skills,
        missing_skills      = missing_skills
    )

    try:
        response = groq_client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

        result = response.choices[0].message.content
        start = result.find("{")
        end = result.rfind("}") + 1
        data = json.loads(result[start:end])

        if start == -1 or end == 0:
            raise ValueError("No valid JSON found in LLM response")

        return {
            "final_score": round(final_score, 2),
            "verdict": data.get("verdict", "UNCERTAIN"),
            "strengths": data.get("strengths", []),
            "weaknesses": data.get("weaknesses", []),
            "reason": data.get("reason", "")
        }

    except json.JSONDecodeError:
        return {
            "final_score": round(final_score, 2),
            "verdict":     "UNCERTAIN",
            "strengths":   [],
            "weaknesses":  [],
            "reason":      "LLM review failed, fallback score used"
        }