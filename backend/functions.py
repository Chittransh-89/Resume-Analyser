import pdfplumber
import io
from sentence_transformers import SentenceTransformer
from sentence_transformers import util
import spacy
from spacy.matcher import PhraseMatcher

def extract_text_from_pdf(content):
    text = ""
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted
    return text

# import spacy
nlp = spacy.load("en_core_web_sm")
skills_list = {
    "python": ["python", "py"],
    "java": ["java"],
    "c++": ["c++", "cpp"],

    "machine learning": ["ml", "machine learning"],
    "deep learning": ["deep learning", "dl"],
    "nlp": ["nlp", "natural language processing"],

    "data analysis": ["data analysis", "data analytics"],
    "data visualization": ["data visualization", "data viz"],

    "pandas": ["pandas"],
    "numpy": ["numpy"],

    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch", "torch"],

    "sql": ["sql"],
    "mongodb": ["mongodb", "mongo"],

    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],

    "aws": ["aws", "amazon web services"],
    "azure": ["azure", "microsoft azure"],

    "fastapi": ["fastapi"],
    "django": ["django"],

    "react": ["react", "reactjs"],
    "angular": ["angular"],
    "nodejs": ["nodejs", "node.js"],

    "git": ["git", "github"],
    "linux": ["linux"]
}
def normalize_skills(skills):
    normalized = []

    for skill in skills:
        skill = skill.lower()

        for main, variants in skills_list.items():
            if skill in variants:
                normalized.append(main)
                break
        else:
            normalized.append(skill)

    return list(set(normalized))

# from spacy.matcher import PhraseMatcher
matcher = PhraseMatcher(nlp.vocab)
patterns = []
for variants in skills_list.values():
    for skill in variants:
        patterns.append(nlp(skill))
matcher.add("SKILLS", patterns)

def extract_skills(text):
    doc = nlp(text.lower())
    matches = matcher(doc)
    skills = set()
    for match_id, start, end in matches:
        skills.add(doc[start:end].text.lower())

    return list(skills)

def skill_gap(user_skills, required_skills):
    return list(set(required_skills) - set(user_skills))

def analyze_resume(text):
    text = text.lower()
    score = 0
    warnings_list = []
    found_skills = []

    for main, variants in skills_list.items():
        for variant in variants:
            if variant in text:
                found_skills.append(main)
                score += 5
                break

    if "projects" in text:
        score += 20
    else:
        warnings_list.append("Add projects section")

    if "skills" in text:
        score += 10
    else:
        warnings_list.append("Add skills section")

    if "experience" in text or "intern" in text:
        score += 20
    else:
        warnings_list.append("Add experience section")
    if score > 100:
        score = 100

    return score, warnings_list, found_skills

# from sentence_transformers import SentenceTransformer

# model load (first time thoda time lega)

model = SentenceTransformer('all-MiniLM-L6-v2')
def calculate_similarity(resume_text, jd_text):
    resume_text = resume_text.lower().strip()
    jd_text = jd_text.lower().strip()

    # embeddings (meaning-based vectors)
    embeddings = model.encode([resume_text, jd_text],normalize_embeddings=True)
    resume_vec = embeddings[0]
    jd_vec = embeddings[1]

    # from sentence_transformers import util
    score = util.cos_sim(resume_vec, jd_vec).item()

    return round(score * 100, 2)
    