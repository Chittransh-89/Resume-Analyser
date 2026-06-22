import json
from config import groq_client, MODEL
import re
from skills_map import skills_list

def classify_document(text):
    prompt = f"""You are an advanced ATS system.

Your task is to classify the given document into one of the following categories:
- RESUME
- NOTES
- JOB_DESCRIPTION
- OTHER

JOB ROLES (choose ONE):
DATA_SCIENTIST
DATA_ANALYST
ML_ENGINEER
AI_ENGINEER
FRONTEND_DEVELOPER
BACKEND_DEVELOPER
FULLSTACK_DEVELOPER
SOFTWARE_ENGINEER

STRICT RULES:

RESUME:
- Personal work experience
- Projects
- Skills section
- Education

JOB_DESCRIPTION:
- Hiring intent
- Required skills
- Responsibilities
- Company language

NOTES:
- Theory
- Study material
- No hiring or personal career context

If unsure → classify as NOTES.
If no dominant specialization → SOFTWARE_ENGINEER.

Return ONLY valid JSON:

{{
  "type": "RESUME or NOTES or JOB_DESCRIPTION or OTHER",
  "job_role": "ROLE_NAME",
  "confidence": number
}}

Document:
{text[:1500]}
"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.05
    )

    result = response.choices[0].message.content.strip()

    start = result.find("{")
    end = result.rfind("}") + 1
    clean_json = result[start:end]

    try:
        data = json.loads(clean_json)
        return {
            "type": data.get("type", "OTHER"),
            "job_role": data.get("job_role", "UNKNOWN"),
            "confidence": data.get("confidence", 0)
        }
    except:
        return {"type": "OTHER", "job_role": "UNKNOWN", "confidence": 0}
    
def clean_text(text):
    text = text.lower()
    # Remove special chars
    text = re.sub(r'[\(\)\[\]\{\}\/\\]', ' ', text)
    # Normalize hyphens to spaces
    text = text.replace('-', ' ')
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    return text

def extract_skills_smart(text):
    """Extract skills with fuzzy matching & normalization."""
    text = clean_text(text)
    found = set()
    
    # Variants Check 
    for canonical, variants in skills_list.items():
        for variant in variants:
            # Check exact word match
            if f" {variant} " in f" {text} ": # space trick (Substring match) eg: "ml" doesn't match "html"
                found.add(canonical)
                break

            # Fuzzy match with threshold for longer variants
            elif len(variant) >= 3 and variant in text:
                # Avoid false positives for short words

                if variant in ["ml", "dl", "cv", "r"]:
                    # Word boundary check match for small variants
                    if re.search(rf'\b{variant}\b', text):
                        found.add(canonical)
                        break
                else:
                    found.add(canonical)
                    break
    
    return list(found)

def parse_resume(text: str) -> dict:
    """
    Resume Text → LLM → Resume JSON
    """
    prompt = f"""
You are a strict resume parser.

Extract structured information from the resume below.

IMPORTANT RULES:
- Return ONLY valid JSON.
- Do NOT invent information.
- Do NOT merge multiple entries into one.
- Extract ALL projects explicitly mentioned in the resume.
- If the resume has sections like Projects, Personal Projects, Academic Projects, Research Projects, Open Source, Hackathons, include all of them in "projects".
- Each distinct project must be a separate object in the "projects" list.
- If no project exists, return an empty list [].
- Preserve bullet points under the correct experience entry.
- If a field is missing, return an empty string "" or empty list [].

Return ONLY valid JSON:
{{
  "name": "string",
  "email": "string",
  "phone": "string",
  "job_role": "string",
  "skills": ["skill1", "skill2"],
  "experience": [
    {{
      "company": "string",
      "role": "string",
      "duration": "string",
      "bullets": ["point1", "point2"]
    }}
  ],
  "education": [
    {{
      "degree": "string",
      "institution": "string",
      "year": "string"
    }}
  ],
  "projects": [
    {{
      "name": "string",
      "description": "string",
      "tech_used": ["tech1", "tech2"]
    }}
  ]
}}

Resume:
{text[:8000]}
"""
    try:
        response = groq_client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.05
        )

        result = response.choices[0].message.content
        start = result.find("{")
        end = result.rfind("}") + 1
        return json.loads(result[start:end])

    except json.JSONDecodeError:
        raise ValueError("Resume parsing failed: Invalid JSON from LLM")


def parse_jd(text: str) -> dict:
    """
    JD Text → LLM → JD JSON
    """
    prompt = f"""
    You are a job description parser.

    IMPORTANT SKILL RULES:
    - Split ALL grouped skills into individual items
    - "ML frameworks (scikit-learn, PyTorch)" → ["scikit-learn", "pytorch", "tensorflow"]
    - "Containerization (Docker)" → ["docker"]
    - Each skill must be ONE clean word or phrase
    - No parentheses in skill names

    Return ONLY valid JSON:
    {{
      "job_title": "string",
      "company": "string",
      "job_role": "string",
      "required_skills": ["skill1", "skill2"],  
      "preferred_skills": ["skill1", "skill2"],
      ...
    }}

    Job Description:
    {text[:3000]}
"""
    try:
        response = groq_client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.05
        )

        result = response.choices[0].message.content
        start = result.find("{")
        end = result.rfind("}") + 1
        return json.loads(result[start:end])

    except json.JSONDecodeError:
        raise ValueError("JD parsing failed: Invalid JSON from LLM")


def classify_documents(resume_text: str, jd_text: str) -> dict:
    """
    Validate that document A is Resume and document B is JD
    """
    prompt = f"""
You are a document classifier.

Classify Document A and Document B.

TYPES: RESUME, JOB_DESCRIPTION, NOTES, OTHER

ROLES: DATA_SCIENTIST, DATA_ANALYST, ML_ENGINEER, AI_ENGINEER,
       FRONTEND_DEVELOPER, BACKEND_DEVELOPER, FULLSTACK_DEVELOPER,
       SOFTWARE_ENGINEER

Return ONLY valid JSON:
{{
  "document_a": {{
    "type": "RESUME or JOB_DESCRIPTION or NOTES or OTHER",
    "job_role": "ROLE_NAME",
    "confidence": number
  }},
  "document_b": {{
    "type": "RESUME or JOB_DESCRIPTION or NOTES or OTHER",
    "job_role": "ROLE_NAME",
    "confidence": number
  }}
}}

Document A:
{resume_text[:1500]}

Document B:
{jd_text[:1500]}
"""
    try:
        response = groq_client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.05
        )

        result = response.choices[0].message.content
        start = result.find("{")
        end = result.rfind("}") + 1
        return json.loads(result[start:end])

    except json.JSONDecodeError:
        return {
            "document_a": {"type": "OTHER", "job_role": "UNKNOWN", "confidence": 0},
            "document_b": {"type": "OTHER", "job_role": "UNKNOWN", "confidence": 0}
        }
