from rule_matcher import match_skills
from semantic import calculate_semantic_score


def calculate_final_score(
    resume_json:  dict,
    jd_json:      dict,
    skill_result: dict,
    semantic_result: dict
) -> dict:
    """
    Rule Match + Semantic Similarity → Final Score
    """
    skill_score    = skill_result["skill_score"]
    semantic_score = semantic_result["semantic_score"]

    # Base score formula
    # Semantic = 60%, Skill Match = 40%
    final_score = (0.6 * semantic_score) + (0.4 * skill_score)

    # Penalty: no projects
    if not resume_json.get("projects"):
        final_score = min(final_score, 45)

    # Penalty: no experience
    if not resume_json.get("experience"):
        final_score = min(final_score, 50)

    if final_score >= 80:
        verdict = "Strong Match"
    elif final_score >= 60:
        verdict = "Good Match"
    elif final_score >= 40:
        verdict = "Moderate Match"
    else:
        verdict = "Low Match"
    return {
        "final_score":    round(final_score, 2),
        "semantic_score": semantic_score,
        "skill_score":   skill_score,
        "verdict" : verdict
    }