# 🚀 Resume Analyzer

A lightweight Resume Analyzer that extracts text from PDF resumes and evaluates them using a rule-based scoring system to generate structured feedback and improvement suggestions.

---

## 📌 Overview

Resume Analyzer processes resumes and provides:
- Resume Score
- Missing skill detection
- Section-wise basic evaluation
- Improvement warnings

---

## ⚙️ Features

### 📄 Resume Parsing
- Extracts text from PDF resumes
- Converts resume into readable structured text

### 🧠 Rule-Based Analysis
- Keyword-based scoring system
- Basic evaluation of:
  - Skills
  - Experience
  - Projects

### ⚠️ Feedback System
- Missing skills detection
- Weak section identification
- Simple improvement warnings

---

## 📊 Sample Output
Score: 70%

Warnings:

No projects mentioned
Missing key skills: React, APIs
Weak experience section

---

## 🛠️ Tech Stack

- Python
- FastAPI
- PDF parsing library (pdfplumber / PyPDF)
- Basic NLP (string processing & keyword matching)

---

## 📁 Project Structure
resume-analyzer/
│
├── backend/
│   ├── main.py
│   ├── functions.py
│   ├── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── compare.html
│   ├── css/
│   │    ├── index.css
│   │    ├── index2.css
│   ├── js/
│   │    ├── script.js
│   │    ├── script2.js
│
└── README.md


---

## 🚀 How to Run

### 1. Clone repository
git clone https://github.com/Chittransh-89/Resume-Analyzer.git
cd resume-analyzer


### 2. Install dependencies

pip install -r requirements.txt


### 3. Start server

uvicorn main:app --reload


### 4. Use
- Upload a PDF resume
- Get score and feedback

---

## 👨‍💻 Author

**Chittransh Verma**
