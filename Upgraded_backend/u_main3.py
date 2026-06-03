import asyncio
import json
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from u_functions import (
    analyze_resume as analyze_resume_logic,
    classify_both_documents,
    extract_bullets_from_text,
    extract_skills_llm,
    extract_text_from_pdf,
    extract_skills_rule,
    final_score,
    normalize_skills,
    split_into_chunks,
    improve_chunk,
    async_llm_call,
    flatten
    
)

app = FastAPI()

# ✅ Enable this if frontend needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 🔹 STRONG Resume vs JD Matching (LLM + Semantic)
@app.post("/analyze/")
async def analyze_route(
    file: UploadFile = File(...),
    jd: UploadFile = File(...)
):
    content = await file.read()
    jd_content = await jd.read()
        
    resume_text = extract_text_from_pdf(content)
    jd_text = extract_text_from_pdf(jd_content)

    classification = classify_both_documents(resume_text, jd_text)
    is_resume = classification.get("document_a", {})
    is_jd = classification.get("document_b", {})

     # ✅ Proper type validation
    if is_resume["type"] != "RESUME":
        return {"error": "First document is not a valid Resume"}

    if is_jd["type"] != "JOB_DESCRIPTION":
        return {"error": "Second document is not a valid Job Description"}

    # ✅ Extract skills before scoring
    # resume_skills_rule = extract_skills_rule(resume_text)
    
    display_skills = extract_skills_llm(resume_text)

    # Normalize
    standardized_skills = normalize_skills(display_skills)
    
    # 🔥 STEP 2: FINAL INTELLIGENT SCORING
    result = final_score(resume_text, jd_text, standardized_skills)
    # ✅ Extract bullets for improve endpoint
    bullets = extract_bullets_from_text(resume_text)

    improved_bullets = []
    if bullets:
        chunks = split_into_chunks(bullets, size=5)
        tasks = [improve_chunk(chunk, jd_text) for chunk in chunks]
        results = await asyncio.gather(*tasks)
        improved_bullets = flatten(results)
        
    return {
        "validation": {
            "resume": is_resume,
            "jd": is_jd
        },
        "role_match": {
            "resume_role": is_resume.get("job_role", "UNKNOWN"),
            "jd_role": is_jd.get("job_role", "UNKNOWN"),
            "match": is_resume.get("job_role", "UNKNOWN") == is_jd.get("job_role", "UNKNOWN")
        },
        "scores": {
            "final": result["score"],
            "semantic": result["semantic_score"],
            "skill": result["skill_score"]
        },
        "skills": {
            "matched": result["matched_skills"],
            "missing": result["missing_skills"]
        },
        "reasoning": result["llm_reason"],
        "extracted_bullets": bullets,
        "improved_bullets": improved_bullets
    }
