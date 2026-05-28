import pdfplumber
import io
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

skills_list = {
    "python": ["python", "py"],
    "java": ["java"],
    "c++": ["c++", "cpp"],
    "machine learning": ["ml", "machine learning"],
    "deep learning": ["deep learning", "dl"],
    "nlp": ["nlp"],
    "data analysis": ["data analysis"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "sql": ["sql"],
    "docker": ["docker"],
    "aws": ["aws"],
    "fastapi": ["fastapi"],
    "django": ["django"],
    "react": ["react"],
    "nodejs": ["nodejs"],
    "git": ["git"],
    "linux": ["linux"]
}

def extract_text_from_pdf(content):
    text = ""
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text()
    return text.lower()


def extract_skills(text):
    found = set()
    for main, variants in skills_list.items():
        for v in variants:
            if v in text:
                found.add(main)
                break
    return list(found)


def normalize_skills(skills):
    return list(set(skills))


def skill_gap(user_skills, required_skills):
    return list(set(required_skills) - set(user_skills))


def analyze_resume(text):
    score = 0
    warnings = []
    skills = extract_skills(text)

    if "project" in text:
        score += 30
    else:
        warnings.append("Add projects section")

    if "skill" in text:
        score += 20
    else:
        warnings.append("Add skills section")

    if "experience" in text or "intern" in text:
        score += 30
    else:
        warnings.append("Add experience section")

    score += len(skills) * 5
    return min(score, 100), warnings, skills


def calculate_similarity(resume_text, jd_text):
    docs = [resume_text, jd_text]

    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform(docs)

    score = cosine_similarity(tfidf[0], tfidf[1])[0][0]

    return round(score * 100, 2)