import asyncio
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles      # ← ADD
from fastapi.responses import FileResponse       # ← ADD
import os                                        # ← ADD
from pdf_extractor  import extract_text_from_pdf
from parsers        import parse_resume, parse_jd, classify_documents,extract_skills_smart,classify_document
from rule_matcher   import match_skills, extract_skills_from_text, normalize_skills
from semantic       import calculate_semantic_score
from scorer         import calculate_final_score
from llm_review     import llm_review
from bullet_improver import extract_bullets_from_text, async_llm_call,improve_chunk,split_into_chunks,flatten,get_top_suggestions

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/classify/")
async def classify_route(
    file: UploadFile = File(...),
):
    content = await file.read()
    resume_text = extract_text_from_pdf(content)

    # Single call — no duplicate
    classification = classify_document(resume_text)

    doc_type = classification.get("type", "OTHER")
    job_role = classification.get("job_role", "UNKNOWN")
    confidence = classification.get("confidence", 0)

    # is_resume ko type se check karo — document_a se nahi
    is_resume = doc_type == "RESUME"

    return {
        "validation": {
            "type": doc_type,
            "confidence": confidence,
            "job_role": job_role,
            "resume": is_resume
        }
    }

@app.post("/analyze/")
async def analyze(
    resume: UploadFile = File(...),
    jd:     UploadFile = File(...),
    debug: bool = False 
):
    # ─────────────────────────────────────────────
    # STEP 1: PDF → TEXT  (PyMuPDF)
    # ─────────────────────────────────────────────
    resume_bytes = await resume.read()
    jd_bytes     = await jd.read()

    resume_text = extract_text_from_pdf(resume_bytes)
    jd_text     = extract_text_from_pdf(jd_bytes)

    # ─────────────────────────────────────────────
    # STEP 2: CLASSIFY (GATE CHECK)
    # ─────────────────────────────────────────────
    classification = classify_documents(resume_text, jd_text)

    doc_a = classification.get("document_a", {})
    doc_b = classification.get("document_b", {})

    if doc_a.get("type") != "RESUME":
        return {"error": "First document is not a valid Resume"}

    if doc_b.get("type") != "JOB_DESCRIPTION":
        return {"error": "Second document is not a valid Job Description"}

    # ─────────────────────────────────────────────
    # STEP 3: LLM → Resume JSON
    # ─────────────────────────────────────────────
    resume_json = parse_resume(resume_text)
    resume_json["skills"] = normalize_skills(resume_json.get("skills", []))

    # ─────────────────────────────────────────────
    # STEP 4: LLM → JD JSON
    # ─────────────────────────────────────────────
    jd_json = parse_jd(jd_text)
    jd_json["required_skills"] = normalize_skills(jd_json.get("required_skills", []))
    jd_json["preferred_skills"] = normalize_skills(jd_json.get("preferred_skills", []))

    # ─────────────────────────────────────────────
    # STEP 5: RULE MATCHING
    # ─────────────────────────────────────────────
    resume_match_skills = normalize_skills(extract_skills_smart(resume_text))
    # resume_skills = normalize_skills(resume_json.get("skills", []))

    skill_result = match_skills(
        resume_skills=resume_match_skills,
        jd_required=jd_json.get("required_skills", []),
        jd_preferred=jd_json.get("preferred_skills", [])
    )

    # ─────────────────────────────────────────────
    # STEP 6: SENTENCE TRANSFORMER → COSINE SIMILARITY
    # ─────────────────────────────────────────────
    semantic_result = calculate_semantic_score(resume_json, jd_json)

    # ─────────────────────────────────────────────
    # STEP 7: FINAL SCORE
    # ─────────────────────────────────────────────
    score_result = calculate_final_score(
        resume_json=resume_json,
        jd_json=jd_json,
        skill_result=skill_result,
        semantic_result=semantic_result
    )

    # ─────────────────────────────────────────────
    # STEP 8: LLM REVIEW
    # ─────────────────────────────────────────────
    review = llm_review(
        resume_json=resume_json,
        jd_json=jd_json,
        final_score=score_result["final_score"],
        matched_skills=skill_result["matched_required"],
        missing_skills=skill_result["missing_required"]
    )

    # ─────────────────────────────────────────────
    # STEP 9: BULLET IMPROVEMENT (ASYNC PARALLEL)
    # ─────────────────────────────────────────────
    
    bullets = extract_bullets_from_text(resume_text)

    improved_bullets = []
    if bullets:
        chunks = split_into_chunks(bullets, size=5)
        tasks = [improve_chunk(chunk, jd_text) for chunk in chunks]
        results = await asyncio.gather(*tasks)
        improved_bullets = flatten(results)

     # ─────────────────────────────────────────────
    # STEP 10: ROLE MATCH
    # ─────────────────────────────────────────────
    resume_roles = doc_a.get("job_role", [])
    jd_roles = doc_b.get("job_role", [])

    if isinstance(resume_roles, str):
        resume_roles = [resume_roles]
    if isinstance(jd_roles, str):
        jd_roles = [jd_roles]

    common_roles = list(set(resume_roles) & set(jd_roles))
    role_match = len(common_roles) > 0

    # ─────────────────────────────────────────────
    # RAW RESULTS (Terminal mein print)
    # ─────────────────────────────────────────────
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Phir print ki jagah:
    logger.info(f"Matched: {skill_result.get('matched_required', [])}")
    logger.info(f"Missing: {skill_result.get('missing_required', [])}")
    logger.info(f"Skill Score: {skill_result.get('skill_score', 0)}")
    logger.info(f"Semantic Score: {semantic_result.get('semantic_score', 0)}")
    logger.info(f"Verdict: {review.get('verdict', '')}")
    # ─────────────────────────────────────────────
    # LINE BY LINE IMPROVEMENTS
    # ─────────────────────────────────────────────
    line_by_line = []
    final_suggestions = []

    for item in improved_bullets:
        original = item.get("original", "").strip()
        improved = item.get("improved", "").strip()
        changed = original.lower() != improved.lower()

        line_by_line.append({
            "original": original,
            "improved": improved,
            "changed": changed
        })
        
        if changed:
            final_suggestions.append(improved)
    
    
    top_suggestions = get_top_suggestions(final_suggestions, top_n=5)

    # ─────────────────────────────────────────────
    # FINAL RESPONSE
    # ─────────────────────────────────────────────
    response = {
        "document_validation": {
            "document_a_type": doc_a.get("type"),
            "document_b_type": doc_b.get("type"),
            "resume_roles": resume_roles,
            "jd_roles": jd_roles,
            "common_roles": common_roles,
            "role_match": role_match
        },

        "candidate": {
            "name": resume_json.get("name", "UNKNOWN"),
            "email": resume_json.get("email", "UNKNOWN"),
            "experience_years": resume_json.get("experience_years", "UNKNOWN"),
            "projects_count": len(resume_json.get("projects", [])),
        },

        "job_needs": {
            "title": jd_json.get("job_title", "UNKNOWN"),
            "required_skills": list(set(jd_json.get("required_skills", []))),
            "preferred_skills": list(set(jd_json.get("preferred_skills", []))),
        },

        "analysis": {
            "matched_skills": list(set(skill_result.get("matched_required", []))),
            "missing_skills": skill_result.get("missing_required", []),
            "semantic_score": semantic_result.get("semantic_score", 0),
        },

        "score": {
            "final_score": score_result["final_score"],
            "verdict": review.get("verdict", "UNCERTAIN"),
        },

        "review": {
            "strengths": review.get("strengths", []),
            "weaknesses": review.get("weaknesses", []),
            "reason": review.get("reason", ""),
        },

        "improvements": {
            "line_by_line": line_by_line,
            "top_suggestions":top_suggestions,
            "summary": {
                "total_bullets": len(line_by_line),
                "improved_count": len(final_suggestions),
            }
        }
    }

    # Debug mode mein raw results bhi bhejo
    if debug:
        response["raw_results"] = {
            "resume_skills": resume_match_skills,
            "skill_result": skill_result,
            "semantic_result": semantic_result,
            "score_result": score_result,
            "llm_review": review,
        }

    return response

from brain import CareerBuddyBrain
from pydantic import BaseModel
brain = CareerBuddyBrain()


# ─── Request ka format ───
class ChatRequest(BaseModel):
    message: str
    use_web_search: bool = False


# ═══════════════════════════════════════
# ROUTE 1: Chat karo
# ═══════════════════════════════════════
@app.post("/api/chat")
async def chat(req: ChatRequest):
    result = brain.chat(
        req.message,
        use_web_search=req.use_web_search
    )
    # Agar result dict hai toh waise hi bhejo, warna fallback
    if isinstance(result, dict):
        return result
    return {"response": result, "used_web_search": False, "youtube_links": []}


# ═══════════════════════════════════════
# ROUTE 2: History clear karo
# ═══════════════════════════════════════
@app.post("/api/chat/clear")
async def clear_chat():
    result = brain.reset_chat()
    return {"status": "cleared", "message": result}


# ═══════════════════════════════════════
# ROUTE 3: Health check
# ═══════════════════════════════════════
@app.get("/api/health")
async def health():
    return {"status": "online", "name": "CareerBuddy AI"}

# ════════════════════════════════════════════════
# STATIC FILES — ADD AT BOTTOM (order matters!)
# ════════════════════════════════════════════════

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Root → serve index.html
@app.get("/")
async def serve_root():
    return FileResponse("static/index.html")