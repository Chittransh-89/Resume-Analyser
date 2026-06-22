import re

# Canonical skill map
SKILLS_MAP = {
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
    "mlflow":    ["mlflow", "ml flow"],
    "kubeflow":  ["kubeflow", "kube flow"],
    "dvc":       ["dvc", "data version control"],
    "azure ml":  ["azure ml", "azureml", "azure machine learning"],
    "prometheus": ["prometheus"],
    "onnx":      ["onnx"],
    "tensorrt":  ["tensorrt", "tensor rt"],
}

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[\(\)\[\]\{\}\/\\]', ' ', text)
    text = text.replace('-', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def clean_skill_string(skill: str) -> list[str]:
    """
    Split grouped skill strings into individual skills
    
    "ML frameworks (scikit-learn, PyTorch, TensorFlow)" 
    → ["scikit-learn", "PyTorch", "TensorFlow", "ML frameworks"]
    
    "Containerization (Docker)" 
    → ["Docker", "Containerization"]
    """
    results = []

    # Extract content inside parentheses first
    inside = re.findall(r'\(([^)]+)\)', skill)
    for group in inside:
        # Split by comma inside parentheses
        parts = [p.strip() for p in group.split(",")]
        results.extend(parts)

    # Remove parentheses content and keep the main part
    main = re.sub(r'\(.*?\)', '', skill).strip()
    if main:
        # Split main part by comma too (in case no parentheses)
        parts = [p.strip() for p in main.split(",")]
        results.extend(parts)

    return [r for r in results if r]  # remove empty strings


def extract_skills_from_text(text: str) -> list[str]:
    """
    Rule-based skill extraction using SKILLS_MAP
    with word boundary matching
    """
    text = clean_text(text)
    found = set()

    for canonical, variants in SKILLS_MAP.items():
        for variant in variants:
            pattern = rf'\b{re.escape(variant.lower())}\b'
            if re.search(pattern, text):
                found.add(canonical)
                break

    return list(found)


def normalize_skills(skills):
    skills = [s.lower() for s in skills]
    normalized = set()
    text = " ".join(skills)

    for canonical, variants in SKILLS_MAP.items():
        for variant in variants:
            pattern = rf'\b{re.escape(variant.lower())}\b'
            if re.search(pattern, text):
                normalized.add(canonical)
                break

    return list(normalized)

# In rule_matcher.py
# Replace the raw string fallback with extract_skills_smart style matching

def match_skills(
    resume_skills: list[str],
    jd_required: list[str],
    jd_preferred: list[str]
) -> dict:

    # Normalize via SKILLS_MAP
    resume_normalized       = set(normalize_skills(resume_skills))
    jd_required_normalized  = set(normalize_skills(jd_required))
    jd_preferred_normalized = set(normalize_skills(jd_preferred))

    # ── Borrow smart matching for unknown skills ─────────────────
    # Skills SKILLS_MAP could not recognize → fallback to smart match
    resume_text = clean_text(" ".join(resume_skills))

    def smart_match(skill: str) -> bool:
        """Check if skill exists in resume using smart matching."""
        skill = clean_text(skill)

        # Exact word boundary match
        if re.search(rf'\b{re.escape(skill)}\b', resume_text):
            return True

        # Substring match with space trick (avoids ml→html)
        if f" {skill} " in f" {resume_text} ":
            return True

        return False

    # For skills that failed SKILLS_MAP normalization
    already_normalized = set(
        clean_text(v)
        for variants in SKILLS_MAP.values()
        for v in variants
    )

    # Required fallback
    matched_required  = list(resume_normalized & jd_required_normalized)
    missing_required  = list(jd_required_normalized - resume_normalized)

    # Check missing ones with smart match
    still_missing_required = []
    smart_recovered_required = []

    for skill in missing_required:
        if smart_match(skill):
            smart_recovered_required.append(skill)
        else:
            still_missing_required.append(skill)

    # Also check raw JD skills not in SKILLS_MAP
    for skill in jd_required:
        skill_clean = clean_text(skill)
        if skill_clean not in already_normalized:
            if smart_match(skill_clean):
                smart_recovered_required.append(skill)
            else:
                still_missing_required.append(skill)

    matched_required = list(set(matched_required + smart_recovered_required))
    missing_required = list(set(still_missing_required))

    # Preferred fallback
    matched_preferred  = list(resume_normalized & jd_preferred_normalized)
    missing_preferred  = list(jd_preferred_normalized - resume_normalized)

    still_missing_preferred = []
    smart_recovered_preferred = []

    for skill in missing_preferred:
        if smart_match(skill):
            smart_recovered_preferred.append(skill)
        else:
            still_missing_preferred.append(skill)

    for skill in jd_preferred:
        skill_clean = clean_text(skill)
        if skill_clean not in already_normalized:
            if smart_match(skill_clean):
                smart_recovered_preferred.append(skill)
            else:
                still_missing_preferred.append(skill)

    matched_preferred = list(set(matched_preferred + smart_recovered_preferred))
    missing_preferred = list(set(still_missing_preferred))

    # ── Score calculation ────────────────────────────────────────
    total_required  = len(matched_required)  + len(missing_required)
    total_preferred = len(matched_preferred) + len(missing_preferred)

    required_score = (
        len(matched_required) / total_required * 100
        if total_required else 0
    )

    preferred_score = (
        len(matched_preferred) / total_preferred * 100
        if total_preferred else 0
    )

    skill_score = (0.7 * required_score) + (0.3 * preferred_score)

    return {
        "matched_required":  matched_required,
        "missing_required":  missing_required,
        "matched_preferred": matched_preferred,
        "missing_preferred": missing_preferred,
        "required_score":    round(required_score, 2),
        "preferred_score":   round(preferred_score, 2),
        "skill_score":       round(skill_score, 2)
    }