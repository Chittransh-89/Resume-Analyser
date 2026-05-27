
from pydoc import text
import warnings

from fastapi import FastAPI, UploadFile
import pdfplumber

app = FastAPI()
filename = "resume2.pdf"
@app.post("/upload/")
async def upload(file: UploadFile):
    print("Received file:", file.filename)

    with open(filename, "wb") as f:
        content = await file.read()
        print("File size:", len(content))
        f.write(content)

    text = ""
    with pdfplumber.open(filename) as pdf:
        print("Total pages:", len(pdf.pages))

        for i, page in enumerate(pdf.pages):
            extracted = page.extract_text()
            print(f"Page {i} text:", extracted)

            if extracted:
                text += extracted
    
    score, warnings_list, found_skills = analyze_resume(text)           

        
    return {
        "filename": file.filename, 
        "text": text, 
        "score": score, 
        "warnings": warnings_list,
        "skills_found": found_skills
    }

def analyze_resume(text):
    text = text.lower()
    score = 0
    warnings_list = []
    found_skills = []

    skills_list = ["python", "java", "c++", "react", "node", "machine learning"]

    for skill in skills_list:
        if skill in text:
            found_skills.append(skill)
            score += 5

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
