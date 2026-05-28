from fastapi import FastAPI, UploadFile, File, Form
from functions import(analyze_resume as analyze_resume_logic, calculate_similarity, extract_text_from_pdf, extract_skills, skill_gap,normalize_skills)
import pdfplumber

app = FastAPI()

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
    # Read files
    content = await file.read()
    jd_content = await jd.read()

    # Extract text
    resume_text = extract_text_from_pdf(content)
    jd_text = extract_text_from_pdf(jd_content)

    # Similarity (BERT)
    score = calculate_similarity(resume_text, jd_text)

    # Extract skills using spaCy
    resume_skills_raw = extract_skills(resume_text)
    jd_skills_raw = extract_skills(jd_text)

    # Normalize skills
    resume_skills = normalize_skills(resume_skills_raw)
    jd_skills = normalize_skills(jd_skills_raw)

    # Skill gap
    missing_skills = list(set(jd_skills) - set(resume_skills))

    return {
        "match_score": f"{score:.2f}%",
        "skills_in_resume": resume_skills,
        "skills_required": jd_skills,
        "missing_skills": missing_skills
    }