from urllib import response

import httpx
import pdfplumber
import io
import json
import requests
from sympy import re
from groq_api import GROQ_API
from config import groq_client

from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# ✅
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
# ✅
def classify_both_documents(resume_text, jd_text):
    prompt = f"""
You are an advanced ATS system.

Your task:

1. Classify Document A and Document B separately.
2. Identify dominant job role for both.

CLASSIFICATION TYPES:
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
  "document_a": {{
    "type": "RESUME or NOTES or JOB_DESCRIPTION or OTHER",
    "confidence": number,
    "job_role": "ROLE_NAME",
    "role_confidence": number
  }},
  "document_b": {{
    "type": "RESUME or NOTES or JOB_DESCRIPTION or OTHER",
    "confidence": number,
    "job_role": "ROLE_NAME",
    "role_confidence": number
  }}
}}

Document A:
{resume_text[:1500]}

Document B:
{jd_text[:1500]}
"""
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.05
    )

    result = response.choices[0].message.content

    start = result.find("{")
    end = result.rfind("}") + 1
    clean_json = result[start:end]

    try:
        return json.loads(clean_json)
    except:
        return {
            "document_a": {"type": "OTHER", "confidence": 0, "job_role": "UNKNOWN", "role_confidence": 0},
            "document_b": {"type": "OTHER", "confidence": 0, "job_role": "UNKNOWN", "role_confidence": 0}
        }

# ✅
def analyze_resume(text, jd_text):
    text = text.lower()
    jd_text = jd_text.lower()
    # 🔥 STEP 1: CLASSIFICATION (GATE)
    classification = classify_both_documents(text, jd_text)

    if classification["type"] != "RESUME":
        return {
            "score": 0,
            "status": "REJECTED",
            "document_type": classification["type"],
            "confidence": classification["confidence"],
            "reason": classification["reason"],
            "warnings": ["This is not a valid Resume"],
            "skills_found": []
        }
    
    if classification["type"] != "JOB DESCRIPTION":
        return {
            "score" : 0,
            "status" : "REJECTED",
            "document_type": classification["type"],
            "confidence": classification["confidence"],
            "reason": classification["reason"],
            "warnings": ["This is not a valid Job Description"],
            "skills_found": []
        }

    if classification["confidence"] < 70:
        return {
            "score": 0,
            "status": "UNCERTAIN",
            "document_type": classification["type"],
            "confidence": classification["confidence"],
            "reason": "Low confidence in classification",
            "warnings": ["Document unclear"],
            "skills_found": []
        }

    # 🔥 STEP 2: SKILL EXTRACTION (ONLY ONCE)
    resume_skills = extract_skills_llm(text)

    # 🔥 STEP 3: STRUCTURE CHECK (LIGHT WEIGHT)
    warnings = []

    if "project" not in text:
        warnings.append("Add projects with real work")

    if "experience" not in text:
        warnings.append("Add experience section")

    if "skill" not in text:
        warnings.append("Add skills section")

    # 🔥 STEP 4: FINAL SCORING
    final = final_score(text, jd_text, resume_skills)

    return {
        "score": int(final["score"]),
        "status": "ACCEPTED",
        "document_type": classification["type"],
        "confidence": classification["confidence"],
        "warnings": warnings,
        "skills_found": resume_skills,
        "semantic_score": final["semantic_score"],
        "skill_score": final["skill_score"],
        "matched_skills": final["matched_skills"],
        "missing_skills": final["missing_skills"],
        "llm_reason": final["llm_reason"]
    }

skills_list = {
    # ===== PROGRAMMING LANGUAGES =====
    "python": ["python", "py", "python3"],
    "javascript": ["javascript", "js", "es6", "ecmascript", "node", "nodejs", "node.js"],
    "typescript": ["typescript", "ts"],
    "java": ["java", "core java", "java 8", "java 11"],
    "c++": ["c++", "cpp", "c plus plus"],
    "c": ["c programming", "c language"],
    "c#": ["c#", "csharp", "c sharp"],
    "go": ["golang", "go lang"],
    "rust": ["rust", "rustlang"],
    "ruby": ["ruby", "rails"],
    "php": ["php", "php7", "php8"],
    "swift": ["swift", "swiftui"],
    "kotlin": ["kotlin"],
    "scala": ["scala"],
    "r": ["r language", "r programming"],

    # ===== WEB FRONTEND =====
    "react": ["react", "reactjs", "react.js", "react native"],
    "angular": ["angular", "angularjs", "angular 2"],
    "vue": ["vue", "vuejs", "vue.js"],
    "next.js": ["next", "nextjs", "next.js"],
    "nuxt": ["nuxt", "nuxtjs"],
    "svelte": ["svelte", "sveltekit"],
    "html": ["html", "html5"],
    "css": ["css", "css3", "scss", "sass", "less"],
    "tailwind": ["tailwind", "tailwindcss", "tailwind css"],
    "bootstrap": ["bootstrap"],
    "redux": ["redux", "react-redux"],

    # ===== WEB BACKEND =====
    "nodejs": ["node", "nodejs", "node.js", "express", "expressjs", "express.js"],
    "django": ["django"],
    "flask": ["flask"],
    "fastapi": ["fastapi", "fast api"],
    "spring": ["spring", "spring boot", "springboot"],
    "nestjs": ["nestjs", "nest.js"],
    "laravel": ["laravel"],
    "asp.net": ["asp.net", "aspnet", ".net", "dotnet"],

    # ===== DATABASES =====
    "sql": ["sql", "mysql", "postgresql", "postgres", "sqlite", "plsql", "t-sql"],
    "mongodb": ["mongodb", "mongo", "nosql"],
    "redis": ["redis"],
    "elasticsearch": ["elasticsearch", "elastic search", "elastcisearch"],
    "cassandra": ["cassandra"],
    "dynamodb": ["dynamodb", "dynamo db"],
    "firebase": ["firebase", "firestore"],

    # ===== MACHINE LEARNING / AI =====
    "machine learning": ["ml", "machine learning", "machinelearning"],
    "deep learning": ["deep learning", "dl", "deeplearning"],
    "neural networks": ["neural network", "neural networks", "ann", "cnn", "rnn", "lstm"],
    "computer vision": ["computer vision", "cv", "opencv", "image processing"],
    "nlp": ["nlp", "natural language processing", "text processing", "text mining"],
    "transformers": ["transformers", "transformer models", "bert", "gpt", "llm"],
    "pytorch": ["pytorch", "torch"],
    "tensorflow": ["tensorflow", "tf", "tensor flow", "keras"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "matplotlib": ["matplotlib", "plt"],
    "seaborn": ["seaborn"],
    "xgboost": ["xgboost", "xgb"],
    "lightgbm": ["lightgbm", "lgbm"],
    "huggingface": ["huggingface", "hugging face", "transformers library"],
    "langchain": ["langchain", "lang chain"],
    "llama": ["llama", "llama2", "llama 2", "llama-2", "llama3"],
    "rag": ["rag", "retrieval augmented generation"],
    "vector database": ["vector database", "vector db", "faiss", "pinecone", "weaviate", "chromadb"],
    "prompt engineering": ["prompt engineering", "prompt design"],
    "agents": ["ai agents", "autogen", "langgraph", "agentic"],

    # ===== DATA ENGINEERING =====
    "spark": ["spark", "pyspark", "apache spark"],
    "hadoop": ["hadoop", "hdfs", "mapreduce"],
    "kafka": ["kafka", "apache kafka"],
    "airflow": ["airflow", "apache airflow"],
    "databricks": ["databricks"],
    "snowflake": ["snowflake"],
    "bigquery": ["bigquery", "big query"],

    # ===== DEVOPS / CLOUD =====
    "docker": ["docker", "dockerfile", "docker-compose", "compose"],
    "kubernetes": ["kubernetes", "k8s", "k8"],
    "aws": ["aws", "amazon web services", "ec2", "s3", "lambda", "sagemaker", "aws sagemaker"],
    "azure": ["azure", "microsoft azure", "azure ml"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "terraform": ["terraform", "tf"],
    "ansible": ["ansible"],
    "jenkins": ["jenkins"],
    "ci/cd": ["ci/cd", "cicd", "continuous integration", "github actions", "gitlab ci"],
    "git": ["git", "github", "gitlab", "bitbucket", "version control"],

    # ===== APIs / TOOLS =====
    "rest api": ["rest api", "rest", "restful", "api development", "api design"],
    "graphql": ["graphql", "graph ql"],
    "postman": ["postman"],
    "swagger": ["swagger", "openapi"],

    # ===== TESTING =====
    "pytest": ["pytest", "unit testing", "test automation"],
    "jest": ["jest"],
    "selenium": ["selenium"],
    "cypress": ["cypress"],

    # ===== OS / TOOLS =====
    "linux": ["linux", "ubuntu", "unix", "bash", "shell scripting"],
    "windows": ["windows server", "powershell"],

    # ===== METHODOLOGIES =====
    "agile": ["agile", "scrum", "kanban"],
    "microservices": ["microservices", "microservice", "service mesh"],
    "system design": ["system design", "high level design", "hld", "lld"],
    "data structures": ["data structures", "dsa", "algorithms"],
    "oop": ["oop", "object oriented", "object-oriented"],

    # ===== DevOps / CI-CD =====
    "ci cd": [
        "ci/cd",
        "ci cd",
        "ci-cd",
        "cicd",
        "continuous integration",
        "continuous deployment",
        "continuous delivery"
    ],
    "github actions": [
        "github actions", "gh actions", "github action",
        "gha", "github workflow", "github ci"
    ],
    "gitlab ci": [
        "gitlab ci", "gitlab-ci", "gitlabci", "gitlab pipeline"
    ],
    "jenkins": ["jenkins", "jenkinsfile", "jenkins pipeline"],
    "circleci": ["circleci", "circle ci"],
    "travis": ["travis ci", "travisci"],
    "argo": ["argo cd", "argocd", "argo workflow"],
    
    # ===== Container =====
    "docker": [
        "docker", "dockerfile", "docker-compose",
        "docker compose", "compose file"
    ],
    "kubernetes": [
        "kubernetes", "k8s", "k8", "kube",
        "kubectl", "helm", "minikube"
    ],
    "containerd": ["containerd", "container d"],
    
    # ===== Cloud =====
    "aws": [
        "aws", "amazon web services", "aws ec2", "aws s3",
        "aws lambda", "aws sagemaker", "amazon s3",
        "ec2", "s3", "lambda", "sagemaker", "rds", "cloudwatch"
    ],
    "azure": [
        "azure", "microsoft azure", "azure devops",
        "azure ml", "azure functions"
    ],
    "gcp": [
        "gcp", "google cloud", "google cloud platform",
        "bigquery", "firebase", "cloud run"
    ],
    
    # ===== AI / ML =====
    "machine learning": [
        "ml", "machine learning", "machinelearning",
        "ml algorithms", "ml models"
    ],
    "deep learning": [
        "deep learning", "dl", "deeplearning",
        "neural network", "neural networks",
        "cnn", "rnn", "lstm", "gan"
    ],
    "transformers": [
        "transformer", "transformers", "bert", "gpt",
        "llm", "large language model", "huggingface"
    ],
    "pytorch": ["pytorch", "torch"],
    "tensorflow": ["tensorflow", "tf", "tensor flow", "keras"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "langchain": ["langchain", "lang chain"],
    "rag": ["rag", "retrieval augmented generation"],
    "vector database": [
        "vector database", "vector db", "faiss",
        "pinecone", "weaviate", "chromadb", "qdrant"
    ],
    
    # ===== Languages =====
    "python": ["python", "py", "python3", "python 3"],
    "javascript": ["javascript", "js", "nodejs", "node js", "node"],
    "typescript": ["typescript", "ts"],
    "java": ["java", "core java"],
    "c++": ["c++", "cpp", "c plus plus"],
    "go": ["golang", "go lang"],
    "rust": ["rust", "rustlang"],
    
    # ===== Web =====
    "react": ["react", "reactjs", "react.js"],
    "next.js": ["nextjs", "next.js", "next js"],
    "django": ["django"],
    "fastapi": ["fastapi", "fast api"],
    "flask": ["flask"],
    "spring": ["spring", "spring boot", "springboot"],
    
    # ===== DBs =====
    "sql": [
        "sql", "mysql", "postgresql", "postgres",
        "sqlite", "plsql", "t-sql", "tsql"
    ],
    "mongodb": ["mongodb", "mongo", "nosql"],
    "redis": ["redis", "redis cache"],
    
    # ===== Tools =====
    "git": [
        "git", "github", "gitlab", "bitbucket",
        "version control", "git workflow"
    ],
    "linux": [
        "linux", "ubuntu", "unix", "debian",
        "bash", "shell", "shell scripting"
    ],
    
    # ===== Testing =====
    "pytest": ["pytest", "py test", "unit test", "unit testing"],
    "jest": ["jest", "react testing"],
    
    # ===== Methodologies =====
    "agile": ["agile", "scrum", "kanban", "jira"],
    "microservices": [
        "microservices", "microservice", "service mesh",
        "istio", "grpc"
    ],
    "rest api": [
        "rest api", "rest", "restful", "restful api",
        "api development"
    ],
    "graphql": ["graphql", "graph ql"],
}


# # 🔹 PDF → TEXT
# ✅
def extract_text_from_pdf(content):
    text = ""
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text()
    return text.lower()

# 🔹 SPLIT sections
# ✅
def split_sections(text):
    text = text.lower()
    sections = {
        "skills": "",
        "projects": "",
        "experience": "",
        "education": ""
    }

    current = None
    for line in text.split("\n"):
        line_lower = line.lower()

        if "skill" in line_lower:
            current = "skills"
        elif "project" in line_lower:
            current = "projects"
        elif "experience" in line_lower or "intern" in line_lower:
            current = "experience"
        elif "education" in line_lower:
            current = "education"

        if current:
            sections[current] += " " + line

    return sections


# 🔹 SKILL EXTRACTION
# ✅
def extract_skills_llm(text):
    text = text.lower()
    prompt = f"""
Extract ONLY real skills from this RESUME.

STRICT RULES:
- Ignore skills mentioned in explanation/theory
- Only include skills the candidate CLAIMS to have used
- Ignore educational/theoretical mentions

Text:
{text[:2000]}

Return JSON:
{{
  "skills": ["skill1", "skill2"]
}}
"""
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )

    result = response.choices[0].message.content

    start = result.find("{")
    end = result.rfind("}") + 1
    clean_json = result[start:end]

    try:
        return json.loads(clean_json)["skills"]
    except:
        return []

import re
# ✅
def clean_text(text):
    text = text.lower()
    # Remove special chars
    text = re.sub(r'[\(\)\[\]\{\}\/\\]', ' ', text)
    # Normalize hyphens to spaces
    text = text.replace('-', ' ')
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    return text

# ✅
# Is stage me:
# Substring match
# Word boundary match
# Fuzzy matching
# Variants check
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

# ✅
# def normalize_skills(skills):
#     skills = [s.lower() for s in skills]
#     """Convert any skill list to standardized canonical names."""
#     normalized = set()
#     text = " ".join(skills).lower()
    
#     for canonical, variants in skills_list.items():
#         for variant in variants:
#             if variant in text:
#                 normalized.add(canonical)
#                 break
    
#     return list(normalized)
import re
# Word Mapping with regex for better accuracy
def normalize_skills(skills):
    skills = [s.lower() for s in skills]
    normalized = set()
    text = " ".join(skills)

    for canonical, variants in skills_list.items():
        for variant in variants:
            pattern = rf'\b{re.escape(variant.lower())}\b'
            if re.search(pattern, text):
                normalized.add(canonical)
                break

    return list(normalized)

# ❌
def extract_skills_rule(text):
    text = text.lower()
    found = set()

    for skill, variants in skills_list.items():
        for v in variants:
            if v in text:
                found.add(skill)

    return list(found)

# ✅
def skill_match_score(resume_skills, jd_text):
    # Normalize both
    jd_skills = extract_skills_smart(jd_text)
    resume_skills = extract_skills_smart(resume_skills) if isinstance(resume_skills, str) else resume_skills
    
    if not jd_skills:
        return 0.0, [], []
    
    resume_text = " ".join(resume_skills).lower()
    jd_text_clean = clean_text(jd_text)
    resume_full = clean_text(resume_text) 
    
    matched = []
    missing = []
    
    for jd_skill in jd_skills:
        # Check in both structured skills and full text
        if jd_skill in resume_skills or jd_skill in resume_full or jd_skill in jd_text_clean:
            matched.append(jd_skill)
        else:
            missing.append(jd_skill)
    
    score = (len(matched) / len(jd_skills) * 100) if jd_skills else 0
    return float(score), matched, missing

# 🔹 PENALTY SYSTEM
# ✅
# 👉 Resume ke kuch sections ka score kam kar deta hai
# agar unme weak / theoretical content ho.
def penalize_irrelevant(section_scores, sections):
    penalty_words = ["notes", "basic", "introduction", "course"]

    for section, text in sections.items():
        for word in penalty_words:
            if word in text:
                section_scores[section] *= 0.85

        if section == "education":
            section_scores[section] *= 0.8

    return section_scores

# 🔹 EMBEDDING MODEL
model = SentenceTransformer("intfloat/e5-large")

# 🔹 SEMANTIC SIMILARITY
# ✅
def calculate_similarity(resume_text, jd_text):
    sections = split_sections(resume_text)

    weights = {
        "skills": 0.5,
        "projects": 0.3,
        "experience": 0.15,
        "education": 0.05
    }

    jd_emb = model.encode("query: " + jd_text)

    section_scores = {}

    for section, text in sections.items():
        if not text.strip():
            section_scores[section] = 0
            continue

        emb = model.encode("passage: " + text)
        score = cosine_similarity([emb], [jd_emb])[0][0]
        section_scores[section] = score

    section_scores = penalize_irrelevant(section_scores, sections)

    final_score = sum(section_scores[s] * weights[s] for s in section_scores)

    return float(round(final_score * 100, 2))


# 🔥 🔹 LOCAL LLM (GEMMA via OLLAMA)
# ✅
def llm_evaluate(resume_text, jd_text, base_score, matched, missing):
    prompt = f"""
You are a STRICT ATS system.

IMPORTANT RULES:
- If resume looks like notes/tutorial → score MUST be below 30
- If no real projects → score MUST be below 50
- DO NOT give high score for theory knowledge
- Be harsh and realistic like real recruiter

Job Description:
{jd_text}

Resume:
{resume_text}

Base Score: {base_score}
Matched Skills: {matched}
Missing Skills: {missing}

Return ONLY JSON:
{{
  "final_score": number,
  "reason": "short explanation"
}}
"""
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )

    result = response.choices[0].message.content

    start = result.find("{")
    end = result.rfind("}") + 1
    clean_json = result[start:end]

    try:
        return json.loads(clean_json)
    except:
        return {
            "final_score": round(base_score, 2),
            "reason": "LLM failed, fallback score used"
        }  

# 🔥 🔹 FINAL SCORE (MAIN BRAIN)
# ✅
def final_score(resume_text, jd_text, resume_skills):
    semantic_score = calculate_similarity(resume_text, jd_text)
    skill_score, matched, missing = skill_match_score(resume_skills, jd_text)

    base_score = (0.7 * semantic_score) + (0.3 * skill_score)

    if "project" not in resume_text:
        base_score = min(base_score, 45)

    # USE_LLM_EVALUATION = False

    # if USE_LLM_EVALUATION:
    llm_result = llm_evaluate(
        resume_text,
        jd_text,
        base_score,
        matched,
        missing
    )
    final = min(llm_result["final_score"], base_score)
    reason = llm_result["reason"]
    # else:
    #     final = base_score
    #     reason = "Fast mode (no LLM evaluation)"

    return {
        "score": float(final),
        "base_score": float(base_score),
        "semantic_score": float(semantic_score),
        "skill_score": float(skill_score),
        "matched_skills": matched,
        "missing_skills": missing,
        "llm_reason": reason
    }

def split_into_chunks(items, size=5):
    return [items[i:i+size] for i in range(0, len(items), size)]

def flatten(list_of_lists):
    return [item for sublist in list_of_lists for item in sublist]
import httpx
import json
import re
import os

import re
import re

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
        "Authorization": f"Bearer {GROQ_API}",
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
    
async def improve_chunk(bullets, jd_text):

    bullets_text = "\n".join(
        f"{i+1}. {b}" for i, b in enumerate(bullets)
    )
    prompt = f"""
You are a professional resume editor.

Rewrite the bullet points to be:
- Action oriented
- Specific and concrete
- ATS friendly
- Aligned with the job description

RULES:
- Do NOT invent metrics or exact numbers.
- Do NOT introduce tools that are not mentioned.
- If no measurable impact is given, improve clarity by explaining:
  • what was built
  • what problem it solved
  • what it was used for

Avoid vague phrases like:
"helped", "worked on", "learned", "got good accuracy"

Replace vague language with specific technical contribution.

Only rewrite for clarity and strength.
Do NOT fabricate achievements.

If a bullet is extremely short (e.g., "used logistic regression"),
expand it into a complete technical contribution sentence 
without adding fake numbers.

Return ONLY valid JSON array.
    Format:
    [
    {{"original": "...", "improved": "..."}}
    ]

    Job Description:
    {jd_text[:2000]}

    Resume Bullets:
    {bullets_text}
    """
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
