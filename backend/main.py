from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from functions import (
    analyze_resume as analyze_resume_logic,
    calculate_similarity,
    extract_text_from_pdf,
    extract_skills,
    normalize_skills,
    skill_gap
)

app = FastAPI()

# CORS (frontend allow)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Upload + Analyze Resume
@app.post("/upload/")
async def upload(file: UploadFile = File(...)):
    content = await file.read()

    text = extract_text_from_pdf(content)
    score, warnings_list, found_skills = analyze_resume_logic(text)

    return {
        "filename": file.filename,
        "score": score,
        "warnings": warnings_list,
        "skills_found": found_skills
    }


# 🔹 Resume vs JD Matching
@app.post("/analyze/")
async def analyze_route(
    file: UploadFile = File(...),
    jd: UploadFile = File(...)
):
    content = await file.read()
    jd_content = await jd.read()

    resume_text = extract_text_from_pdf(content)
    jd_text = extract_text_from_pdf(jd_content)

    # similarity (lightweight TF-IDF)
    score = calculate_similarity(resume_text, jd_text)

    # skills extraction
    resume_skills = normalize_skills(extract_skills(resume_text))
    jd_skills = normalize_skills(extract_skills(jd_text))

    missing_skills = list(set(jd_skills) - set(resume_skills))

    return {
        "match_score": f"{score:.2f}%",
        "skills_in_resume": resume_skills,
        "skills_required": jd_skills,
        "missing_skills": missing_skills
    }