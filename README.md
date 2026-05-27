# 🚀 Resume Analyzer

> A smart Resume Analyzer that extracts, evaluates, and scores resumes — evolving from a rule-based system to an ML-powered product.

---

## 📌 Overview

This project analyzes resumes (PDF format) and provides:
- 📊 Resume Score
- ⚠️ Improvement Warnings
- 🧠 (Upcoming) AI-based Resume Matching

Built step-by-step to transition from a **basic script → intelligent system → deployable product**.

---

## ✨ Features

### 🔹 Phase 1 — Resume Parsing
- Extract text from PDF resumes
- Process raw resume content
- Display extracted data

### 🔹 Phase 2 — Rule-Based Analysis
- Keyword-based evaluation
- Resume scoring system
- Smart warnings:
  - Missing skills
  - Weak sections
  - No projects

---

## 📊 Sample Output
Score: 65%

Warnings:
No projects mentioned
Missing key skills (React, APIs)
Weak experience section

---

## 🛠️ Tech Stack

- **Backend:** FastAPI
- **Language:** Python
- **Libraries:** PyPDF / PDF parsing tools
- **Logic:** Rule-based text processing

---

## 📁 Project Structure
resume-analyzer/src
│
├── main.py # FastAPI app
├── parser.py # Resume extraction
├── analyzer.py # Scoring logic
├── utils.py # Helper functions
└── sample_resume.pdf # Test file

---

## ⚙️ Setup & Run

### 1️⃣ Clone Repository

git clone https://github.com/Chittransh-89/Resume-Analyzer.git
cd resume-analyzer


### 2️⃣ Install Dependencies

pip install -r requirements.txt


### 3️⃣ Run Server

uvicorn main:app --reload

### 4️⃣ Test API
- Upload a resume (PDF)
- Get score + warnings in response

---

## 🧠 Upcoming Features

### 🔹 Phase 3 — ML / NLP
- TF-IDF Vectorization
- Cosine Similarity
- Resume vs Job Description matching

### 🔹 Phase 4 — Smart Analysis
- Section-wise scoring
- Advanced keyword extraction
- Personalized suggestions

### 🔹 Phase 5 — Frontend
- Resume upload UI
- Score visualization dashboard

### 🔹 Phase 6 — Deployment
- Cloud deployment (Render / AWS)
- Multi-user support
- Production-ready API

---

## 🎯 Vision

Transform this project into a **real-world product** that helps users improve their resumes using data and AI.

---

## ⚠️ Important Note

This is not just a basic project.  
The real value comes from:
- Completing ML integration
- Adding frontend
- Deploying it live
- Explaining it clearly

---

## 👨‍💻 Author

**Chittransh Verma**

---

## ⭐ Support

If you found this useful, consider giving it a ⭐ on GitHub.
