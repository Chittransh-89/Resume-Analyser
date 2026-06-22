from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load once globally
model = SentenceTransformer("intfloat/e5-base")


def get_section_text(resume_json: dict) -> dict:
    """
    Resume JSON → section wise text for weighted scoring
    """
    skills_text = " ".join(resume_json.get("skills", []))

    experience_text = " ".join([
        " ".join(exp.get("bullets", []))
        for exp in resume_json.get("experience", [])
    ])

    projects_text = " ".join([
        proj.get("description", "") + " " + " ".join(proj.get("tech_used", []))
        for proj in resume_json.get("projects", [])
    ])

    education_text = " ".join([
        edu.get("degree", "") + " " + edu.get("institution", "")
        for edu in resume_json.get("education", [])
    ])

    return {
        "skills":     skills_text,
        "experience": experience_text,
        "projects":   projects_text,
        "education":  education_text
    }


def build_jd_text(jd_json: dict) -> str:
    """
    JD JSON → single text for embedding
    """
    parts = []
    parts.append(jd_json.get("job_title", ""))
    parts.extend(jd_json.get("required_skills", []))
    parts.extend(jd_json.get("preferred_skills", []))
    parts.extend(jd_json.get("responsibilities", []))
    parts.extend(jd_json.get("qualifications", []))
    return " ".join(parts)


def calculate_semantic_score(resume_json: dict, jd_json: dict) -> dict:
    """
    Sentence Transformer → Cosine Similarity → Weighted Score
    """
    WEIGHTS = {
        "skills":     0.35,
        "experience": 0.30,
        "projects":   0.25,
        "education":  0.10
    }

    sections = get_section_text(resume_json)
    jd_text  = build_jd_text(jd_json)

    jd_embedding = model.encode("query: " + jd_text)

    section_scores = {}

    for section, text in sections.items():
        if not text.strip():
            section_scores[section] = 0.0
            continue

        section_emb = model.encode("passage: " + text)
        score = cosine_similarity([section_emb], [jd_embedding])[0][0]
        section_scores[section] = float(round(score * 100, 2))

    weighted_score = sum(
        section_scores[s] * WEIGHTS[s]
        for s in section_scores
    )

    return {
        "semantic_score":  round(weighted_score, 2),
        "section_scores":  section_scores
    }