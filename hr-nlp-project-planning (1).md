# HR NLP Application — Full Planning Chat

> Complete conversation log including all questions, responses, diagrams, and code snippets.
> Use this to continue the project in a new chat.

---

## Table of Contents

1. [Project Overview & Stack Planning](#1-project-overview--stack-planning)
2. [NLP Core — Models & Tasks](#2-nlp-core--models--tasks)
3. [Where to Get Models & Data](#3-where-to-get-models--data)
4. [Fine-Tuning Roadmap](#4-fine-tuning-roadmap)
5. [Backend — FastAPI](#5-backend--fastapi)
6. [Frontend](#6-frontend)
7. [Full Tech Stack Summary](#7-full-tech-stack-summary)
8. [Where to Write Commands](#8-where-to-write-commands)
9. [Pushing Model to HuggingFace Hub](#9-pushing-model-to-huggingface-hub)
10. [Database Usage](#10-database-usage)
11. [What is PyTorch](#11-what-is-pytorch)
12. [Moving Fine-Tuned Model to Local Code](#12-moving-fine-tuned-model-to-local-code)
13. [Communicating with the Model After Pushing](#13-communicating-with-the-model-after-pushing)
14. [Fine-Tuning Explained — Open Source & API vs Local](#14-fine-tuning-explained--open-source--api-vs-local)
15. [Google Colab vs VS Code Extension](#15-google-colab-vs-vs-code-extension)
16. [FastAPI Discussion](#16-fastapi-discussion)
17. [Initial File Structure](#17-initial-file-structure)
18. [Plugin / Modular Architecture Decision](#18-plugin--modular-architecture-decision)
19. [Using uv as Package Manager](#19-using-uv-as-package-manager)
20. [Workflow Summary](#20-workflow-summary)
21. [Build Plan — Backend + Frontend with JWT](#21-build-plan--backend--frontend-with-jwt)
22. [Removing Unnecessary Folders](#22-removing-unnecessary-folders)
23. [Final Clean File Structure](#23-final-clean-file-structure)

---

## 1. Project Overview & Stack Planning

**User:** I'm building an application that supports HR. The application has a core AI function — NLP analysis on the HR review. It generates analysis and recommendation for the given HR feedback review. I want you to plan and discuss with me the stack to use. You will provide for me the places where to get the NLP model from your research, how to fine tune it, how to integrate it in the app. All with resources and detailed steps of how to do it. It is a bachelor's project and I want to learn the most from it to become an AI engineer.

**Answers provided:**
- Background: Python (comfortable), Some ML/Data Science
- NLP tasks needed: Sentiment analysis, Key skill/competency extraction, Recommendation generation (text), Performance scoring
- Infrastructure: Can use free tiers (HuggingFace, GCP, etc.)

---

## 2. NLP Core — Models & Tasks

Your four NLP tasks map to different model types:

### Sentiment Analysis
Most straightforward — classifies text as positive/negative/neutral. Best models:
- `cardiffnlp/twitter-roberta-base-sentiment-latest`
- `j-hartmann/emotion-english-distilroberta-base`
- `ProsusAI/finbert` (domain-adapted BERT — good structural reference)

### Key Skill/Competency Extraction
Named Entity Recognition (NER) task. Recognizes entities like skills ("Python", "leadership") and competencies ("strategic thinking").
- Base model: `dslim/bert-base-NER`
- Fine-tune on HR-specific labeled data

### Performance Scoring
Regression or classification task — text in, score out (1–5 or Exceeds/Meets/Below).
- Model: `bert-base-uncased` fine-tuned with a classification head

### Recommendation Generation
Text generation given analysis context.
- Model: `google/flan-t5-base` — instruction-tuned, free, runs locally, no GPU needed for inference

---

## 3. Where to Get Models & Data

### Models — HuggingFace Hub (huggingface.co/models)

| Model | Task |
|---|---|
| `bert-base-uncased` | Workhorse for fine-tuning classification |
| `dslim/bert-base-NER` | Base for competency extraction |
| `j-hartmann/emotion-english-distilroberta-base` | Sentiment |
| `google/flan-t5-base` | Recommendation generation |
| `sentence-transformers/all-MiniLM-L6-v2` | Semantic similarity (bonus) |

### Datasets

- HuggingFace `datasets` library: `load_dataset("ag_news")` for structure reference
- **Glassdoor reviews dataset** on Kaggle — real employee reviews
- **Synthetically generate** fine-tuning data using Claude/GPT API — generate 500–1000 labeled HR review examples (legitimate and widely used technique)

---

## 4. Fine-Tuning Roadmap

### Environment Setup (Colab)

```bash
pip install transformers datasets torch accelerate evaluate scikit-learn
```

### Step 1 — Fine-tune Sentiment Model

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
from datasets import load_dataset

tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=3)

def tokenize(batch):
    return tokenizer(batch["text"], truncation=True, padding=True, max_length=512)

dataset = dataset.map(tokenize, batched=True)

training_args = TrainingArguments(
    output_dir="./hr-sentiment",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
)

trainer = Trainer(model=model, args=training_args, train_dataset=train_data, eval_dataset=eval_data)
trainer.train()
```

Same pattern for performance scoring — just change `num_labels` and dataset labels.

### Step 2 — Fine-tune NER for Competency Extraction

Uses BIO tagging format: B-SKILL, I-SKILL, O

```
"She demonstrates [B-SKILL]strong[I-SKILL] leadership[I-SKILL] skills[O]"
```

Reference: `huggingface.co/docs/transformers/tasks/token_classification`

### Step 3 — Recommendation Generation with Flan-T5

No heavy fine-tuning needed — use prompt engineering first:

```python
from transformers import T5ForConditionalGeneration, T5Tokenizer

model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")
tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")

prompt = """
HR Review Analysis:
- Sentiment: Mostly Negative
- Performance Score: 2/5
- Key Skills Identified: communication, teamwork
- Missing Competencies: leadership, time management

Generate 3 specific, actionable HR recommendations for this employee:
"""

inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0]))
```

If fine-tuning needed: use **LoRA** via the `peft` library.

### Step 4 — Push to HuggingFace Hub

```python
model.push_to_hub("your-username/hr-sentiment-model")
tokenizer.push_to_hub("your-username/hr-sentiment-model")
```

---

## 5. Backend — FastAPI

```python
from fastapi import FastAPI
from transformers import pipeline

app = FastAPI()

sentiment_pipe = pipeline("text-classification", model="your-username/hr-sentiment-model")
ner_pipe = pipeline("token-classification", model="your-username/hr-ner-model")

@app.post("/analyze")
async def analyze_review(review: str):
    sentiment = sentiment_pipe(review)
    entities = ner_pipe(review)
    return {
        "sentiment": sentiment,
        "skills_found": entities,
        "performance_score": score,
        "recommendations": recommendations
    }
```

**Model loading pattern — load ONCE at startup:**

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    ml_models["sentiment"] = pipeline("text-classification", model="your-username/hr-sentiment-model")
    ml_models["ner"] = pipeline("token-classification", model="your-username/hr-ner-model")
    ml_models["scoring"] = pipeline("text-classification", model="your-username/hr-scoring-model")
    yield
    ml_models.clear()

app = FastAPI(lifespan=lifespan)
```

---

## 6. Frontend

React + Tailwind CSS. HR manager pastes/uploads a review, clicks Analyze, sees structured report.

---

## 7. Full Tech Stack Summary

| Layer | Technology | Why |
|---|---|---|
| NLP Models | HuggingFace Transformers | Industry standard |
| Fine-tuning | Google Colab + PyTorch | Free GPU |
| Parameter-efficient fine-tuning | PEFT / LoRA | Colab-friendly |
| Model Registry | HuggingFace Hub | Free hosting |
| Backend | FastAPI | Pythonic, fast |
| Database | SQLite → PostgreSQL | Start simple |
| Frontend | React + Tailwind | Clean dashboard |
| Deployment | Render / Railway | Free tier |

### Key Resources

- `huggingface.co/learn` — HuggingFace NLP course (free, best NLP course available)
- `huggingface.co/docs/transformers/tasks` — task-specific fine-tuning guides
- FastAPI docs: `fastapi.tiangolo.com`
- PEFT/LoRA: `huggingface.co/docs/peft`
- Kaggle datasets: search "employee performance review", "Glassdoor reviews"

---

## 8. Where to Write Commands

### On Google Colab (recommended for training)

Add `!` before the command in a code cell:

```bash
!pip install transformers datasets torch accelerate evaluate scikit-learn
```

Enable GPU: Runtime → Change runtime type → T4 GPU

### On Local Machine

```bash
python -m venv hr-nlp-env
hr-nlp-env\Scripts\activate      # Windows
source hr-nlp-env/bin/activate   # Mac/Linux

pip install transformers datasets torch accelerate evaluate scikit-learn
```

**Rule:** Use Colab for all model training. Use local machine for FastAPI backend and React frontend.

---

## 9. Pushing Model to HuggingFace Hub

### Step 1 — Create HuggingFace Account
Go to `huggingface.co` and sign up.

### Step 2 — Get Access Token
Go to `huggingface.co/settings/tokens` → New Token → role: **Write** → copy token.

### Step 3 — Login in Colab

```python
from huggingface_hub import login
login(token="hf_yourTokenHere")
```

### Step 4 — Push Model

```python
model.push_to_hub("ahmed123/hr-sentiment-model")
tokenizer.push_to_hub("ahmed123/hr-sentiment-model")
```

### After Push

HuggingFace creates a repository at `huggingface.co/ahmed123/hr-sentiment-model`. Load it anywhere with:

```python
pipeline("text-classification", model="ahmed123/hr-sentiment-model")
```

> Think of HuggingFace Hub as **GitHub but for AI models**.

---

## 10. Database Usage

### What Gets Saved

Every analysis result is saved as one row:

| id | employee_name | review_text | sentiment | confidence | skills_found | performance_score | recommendations | created_at |
|---|---|---|---|---|---|---|---|---|
| 1 | John Smith | "John consistently..." | Positive | 0.94 | leadership, communication | 4/5 | Focus on... | 2024-01-15 |

### Database Setup

**`backend/database.py`**

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./database/hr_reviews.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**`backend/models/review.py`**

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from database import Base
import datetime

class ReviewRecord(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    employee_name = Column(String)
    department = Column(String)
    review_text = Column(Text)
    sentiment = Column(String)
    sentiment_confidence = Column(Float)
    skills_found = Column(String)
    performance_score = Column(String)
    score_confidence = Column(Float)
    recommendations = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.now)
```

**`backend/schemas/review.py`**

```python
from pydantic import BaseModel
from datetime import datetime

class ReviewInput(BaseModel):
    employee_name: str
    department: str
    review_text: str

class ReviewOutput(BaseModel):
    id: int
    employee_name: str
    department: str
    sentiment: str
    sentiment_confidence: float
    skills_found: list
    performance_score: str
    recommendations: str
    created_at: datetime

    class Config:
        from_attributes = True
```

**`backend/services/review_service.py`**

```python
from sqlalchemy.orm import Session
from models.review import ReviewRecord
from schemas.review import ReviewInput
from services.nlp_service import full_analysis

def save_analysis(input_data: ReviewInput, db: Session):
    results = full_analysis(input_data.review_text)

    record = ReviewRecord(
        employee_name=input_data.employee_name,
        department=input_data.department,
        review_text=input_data.review_text,
        sentiment=results["sentiment"]["label"],
        sentiment_confidence=results["sentiment"]["confidence"],
        skills_found=", ".join(results["skills_found"]),
        performance_score=results["performance_score"]["score"],
        score_confidence=results["performance_score"]["confidence"],
        recommendations=results["recommendations"]
    )

    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def get_all_reviews(db: Session):
    return db.query(ReviewRecord).order_by(ReviewRecord.created_at.desc()).all()

def get_employee_reviews(employee_name: str, db: Session):
    return db.query(ReviewRecord).filter(ReviewRecord.employee_name == employee_name).all()

def get_department_reviews(department: str, db: Session):
    return db.query(ReviewRecord).filter(ReviewRecord.department == department).all()
```

**`backend/main.py`**

```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import engine, get_db, Base
from schemas.review import ReviewInput, ReviewOutput
from services.review_service import save_analysis, get_all_reviews, get_employee_reviews
from models import review

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/analyze", response_model=ReviewOutput)
async def analyze_review(input_data: ReviewInput, db: Session = Depends(get_db)):
    result = save_analysis(input_data, db)
    return result

@app.get("/reviews", response_model=list[ReviewOutput])
async def get_reviews(db: Session = Depends(get_db)):
    return get_all_reviews(db)

@app.get("/reviews/{employee_name}", response_model=list[ReviewOutput])
async def get_employee_history(employee_name: str, db: Session = Depends(get_db)):
    return get_employee_reviews(employee_name, db)
```

### Complete Flow

```
React Frontend
    sends: { employee_name, department, review_text }
            ↓
FastAPI /analyze endpoint
            ↓
review_service.save_analysis()
    calls → nlp_service.full_analysis()  →  4 models run
    saves → SQLite database
    returns → complete results
            ↓
React Frontend
    receives: { sentiment, skills, score, recommendations }
    displays: analysis dashboard
```

### Extra Features the Database Unlocks

- **Employee history** — track score evolution across reviews over time
- **Department analytics** — average sentiment and scores per department
- **Skill gap analysis** — most commonly missing competencies across all employees

---

## 11. What is PyTorch

PyTorch is a mathematical computation library built by Meta that makes it possible to build and train neural networks. It's the engine underneath everything.

```
Your fine-tuning code (what you write)
        ↓
HuggingFace Transformers (makes it easy)
        ↓
PyTorch (does the actual math)
        ↓
GPU/CPU (executes the computation)
```

### What PyTorch Actually Does

Three mathematical things happen on every batch — PyTorch handles all three:

1. **Forward pass** — feeds text through model, gets prediction
2. **Loss calculation** — measures how wrong the prediction was
3. **Backpropagation** — adjusts weights to be less wrong next time

### Where You'll See PyTorch in Your Project

**Checking GPU availability:**
```python
import torch
device = "cuda" if torch.cuda.is_available() else "cpu"
print(device)  # should print "cuda" on Colab
model = model.to(device)
```

**Dataset class:**
```python
import torch
from torch.utils.data import Dataset

class HRReviewDataset(Dataset):
    def __init__(self, texts, labels, tokenizer):
        self.encodings = tokenizer(texts, truncation=True, padding=True)
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item
```

**Custom inference:**
```python
inputs = tokenizer("John exceeds all expectations", return_tensors="pt")
with torch.no_grad():
    outputs = model(**inputs)
predicted_class = torch.argmax(outputs.logits, dim=1)
```

### Role Summary

| Layer | Technology | Your Involvement |
|---|---|---|
| You write | Fine-tuning scripts | High |
| Makes it easy | HuggingFace Transformers | High |
| Does the math | PyTorch | Low but must understand basics |
| Runs the math fast | GPU (CUDA) | Zero — hardware handles it |

> Learning resource: `pytorch.org/tutorials/beginner/basics/intro.html`

---

## 12. Moving Fine-Tuned Model to Local Code

### Option 3 — Save Directly to Project Folder (Chosen Option)

**In Colab — save and download:**

```python
model.save_pretrained("/content/hr-sentiment-model")
tokenizer.save_pretrained("/content/hr-sentiment-model")

import shutil
shutil.make_archive("/content/hr-sentiment-model", 'zip', "/content/hr-sentiment-model")

from google.colab import files
files.download("/content/hr-sentiment-model.zip")
```

Extract the zip and place in project:

```
hr-nlp-app/
├── ai/
│   └── models/
│       ├── hr-sentiment-model/
│       │   ├── config.json
│       │   ├── pytorch_model.bin
│       │   └── ...
│       ├── hr-ner-model/
│       ├── hr-scoring-model/
│       └── hr-flan-t5-model/
```

**Load in FastAPI using local path:**

```python
sentiment_pipe = pipeline(
    "text-classification",
    model="./ai/models/hr-sentiment-model"
)
```

### Complete nlp_service.py

```python
# backend/modules/nlp/service.py
from transformers import pipeline, T5ForConditionalGeneration, T5Tokenizer
import torch

MODEL_PATH = "./ai/models"

print("Loading models... please wait")

sentiment_pipe = pipeline(
    "text-classification",
    model=f"{MODEL_PATH}/hr-sentiment-model",
    device=0 if torch.cuda.is_available() else -1
)

ner_pipe = pipeline(
    "token-classification",
    model=f"{MODEL_PATH}/hr-ner-model",
    aggregation_strategy="simple"
)

scoring_pipe = pipeline(
    "text-classification",
    model=f"{MODEL_PATH}/hr-scoring-model"
)

t5_model = T5ForConditionalGeneration.from_pretrained(f"{MODEL_PATH}/hr-flan-t5-model")
t5_tokenizer = T5Tokenizer.from_pretrained(f"{MODEL_PATH}/hr-flan-t5-model")

print("All models loaded successfully!")

def analyze_sentiment(text: str):
    result = sentiment_pipe(text)[0]
    return {"label": result["label"], "confidence": round(result["score"], 2)}

def extract_skills(text: str):
    entities = ner_pipe(text)
    skills = [e["word"] for e in entities if e["entity_group"] == "SKILL"]
    return skills

def score_performance(text: str):
    result = scoring_pipe(text)[0]
    return {"score": result["label"], "confidence": round(result["score"], 2)}

def generate_recommendations(sentiment: str, skills: list, score: str):
    prompt = f"""
    HR Review Analysis:
    - Sentiment: {sentiment}
    - Performance Score: {score}
    - Skills Identified: {', '.join(skills)}

    Generate 3 specific actionable HR recommendations:
    """
    inputs = t5_tokenizer(prompt, return_tensors="pt", truncation=True)
    outputs = t5_model.generate(**inputs, max_new_tokens=200)
    return t5_tokenizer.decode(outputs[0], skip_special_tokens=True)

def full_analysis(text: str):
    sentiment = analyze_sentiment(text)
    skills = extract_skills(text)
    score = score_performance(text)
    recommendations = generate_recommendations(sentiment["label"], skills, score["score"])
    return {
        "sentiment": sentiment,
        "skills_found": skills,
        "performance_score": score,
        "recommendations": recommendations
    }
```

---

## 13. Communicating with the Model After Pushing

### Two Options

**Option 1 — Load Directly in FastAPI (Recommended)**

Download model once into FastAPI server, run locally. No API calls, no internet needed after first download, free forever, no rate limits.

```python
sentiment_pipe = pipeline("text-classification", model="your-username/hr-sentiment-model")
result = sentiment_pipe("John consistently exceeds expectations")
```

**Option 2 — HuggingFace Inference API**

```python
import requests
API_URL = "https://api-inference.huggingface.co/models/your-username/hr-sentiment-model"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}
response = requests.post(API_URL, headers=headers, json={"inputs": text})
```

> Downside: rate limits, model "sleeps" (30s wake time on free tier), needs internet always.

### Token Usage Summary

| Situation | Token Needed? |
|---|---|
| Downloading open models (BERT, Flan-T5) | No |
| Downloading gated models (LLaMA) | Yes |
| Pushing fine-tuned model to Hub | Yes (Write token) |
| Using HuggingFace Inference API | Yes |
| Loading your own public model | No |

---

## 14. Fine-Tuning Explained — Open Source & API vs Local

### Two Ways to Use HuggingFace Models

**Way 1 — Download and Run Locally (for Fine-Tuning)**

```python
from transformers import pipeline
# Downloads ~500MB to local cache on first run
sentiment = pipeline("text-classification", model="distilbert-base-uncased")
```

**Way 2 — HuggingFace Inference API (Remote)**

```python
import requests
API_URL = "https://api-inference.huggingface.co/models/distilbert-base-uncased"
headers = {"Authorization": "Bearer hf_yourTokenHere"}
response = requests.post(API_URL, headers=headers, json={"inputs": "This employee performs well"})
```

> Cannot fine-tune through the API — you're calling their hosted version only.

### Are the Models Open Source?

Most yes — BERT, DistilBERT, Flan-T5, RoBERTa are fully open source. Download, modify, fine-tune, redistribute freely for research/academic use. Some models are **gated** (e.g. LLaMA) — free but requires access request.

### What Fine-Tuning Means

> BERT = person who read the entire internet and learned English deeply. Fine-tuning = giving them a short specialized HR course.

```
Original BERT weights (frozen knowledge)
        +
Your HR dataset (new task-specific knowledge)
        +
A few training epochs (the learning process)
        =
Your fine-tuned HR sentiment model (specialized)
```

### Fine-Tuning Steps

1. Prepare labeled CSV data (text, label columns)
2. Load base model from HuggingFace
3. Tokenize data (text → number sequences)
4. Train with Trainer class
5. Evaluate (target accuracy >80%)
6. Push to HuggingFace Hub

---

## 15. Google Colab vs VS Code Extension

**Use Google Colab website** (`colab.research.google.com`) — NOT the VS Code extension.

The website gives you a free cloud T4 GPU running on Google's servers. Your laptop does zero heavy work.

```
You open Colab in Chrome
        ↓
You run your training code
        ↓
Colab's server downloads BERT from HuggingFace (to Google's server)
        ↓
Fine-tuning runs on Colab's GPU (not your laptop)
        ↓
You push the fine-tuned model to HuggingFace Hub
        ↓
Done — your laptop did nothing heavy
```

### Workflow Split

| Task | Where to Run |
|---|---|
| Fine-tuning / training models | Colab (needs GPU) |
| Testing a model after training | Colab or local |
| FastAPI backend | Your local VS Code |
| React frontend | Your local VS Code |
| Loading fine-tuned model in the app | Your local machine (inference only) |

### Save to Google Drive

```python
from google.colab import drive
drive.mount('/content/drive')
```

---

## 16. FastAPI Discussion

FastAPI is the right choice because:

- **It's Python** — same language as your entire AI stack
- **Built for AI/ML backends** — most production ML APIs use FastAPI
- **Auto-generated docs** — interactive API docs at `localhost:8000/docs` automatically
- **Async support** — server doesn't freeze while models run

### Alternatives Comparison

| Framework | Verdict |
|---|---|
| Flask | Older, no async, needs extra libraries |
| Django | Too heavy, built for full web apps |
| Node.js/Express | Different language, bridge required |
| **FastAPI** | ✅ Perfect fit |

---

## 17. Initial File Structure

```
hr-nlp-app/
│
├── ai/
│   ├── notebooks/
│   ├── data/
│   │   ├── raw/
│   │   ├── processed/
│   │   └── synthetic/
│   └── models/
│       ├── hr-sentiment-model/
│       ├── hr-ner-model/
│       ├── hr-scoring-model/
│       └── hr-flan-t5-model/
│
├── backend/
│   ├── main.py
│   ├── models/
│   ├── schemas/
│   ├── services/
│   │   ├── nlp_service.py
│   │   └── review_service.py
│   ├── database.py
│   ├── config.py
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/
│       ├── services/
│       │   └── api.js
│       ├── App.jsx
│       └── main.jsx
│
├── database/
│   └── hr_reviews.db
│
├── .env
└── .gitignore
```

---

## 18. Plugin / Modular Architecture Decision

**Decision: Build as modular plugin architecture.**

Instead of one fixed web app, each part is independent and can be used alone or together:

```
┌─────────────────────────────────────────────────────┐
│                 Full HR Web App                      │
│  ┌─────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │  Auth   │  │  NLP Engine │  │    Dashboard    │  │
│  │ Module  │  │   Module    │  │     Module      │  │
│  └─────────┘  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────┘

OR someone with their own HR system uses ONLY:

┌─────────────────┐
│   NLP Engine    │  ← standalone API anyone can plug into their system
│   Module        │
│  /analyze       │
│  /history       │
│  /analytics     │
└─────────────────┘
```

### Two Deployment Modes

```
Mode 1 — Full App (your React frontend + your FastAPI backend)
Mode 2 — Plugin/API only (just FastAPI, plugged into someone else's system)
```

### NLP Module Standalone Endpoints

```
POST /api/v1/nlp/analyze          ← send one review, get full analysis
POST /api/v1/nlp/batch-analyze    ← send multiple reviews at once
GET  /api/v1/nlp/history          ← get past analyses
GET  /api/v1/nlp/analytics        ← get aggregated insights
```

### External System Integration Example

```python
import requests

response = requests.post(
    "https://your-api.com/api/v1/nlp/analyze",
    headers={"Authorization": "Bearer their_jwt_token"},
    json={
        "employee_name": "John Smith",
        "department": "Engineering",
        "review_text": "John consistently delivers high quality work..."
    }
)
analysis = response.json()
```

---

## 19. Using uv as Package Manager

### Install uv

```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Mac/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Initialize Project

```bash
uv init hr-nlp-app
cd hr-nlp-app
```

### Install Dependencies

```bash
uv add fastapi uvicorn sqlalchemy pydantic pydantic-settings
uv add python-jose[cryptography] passlib[bcrypt] python-multipart
uv add python-dotenv
uv add transformers torch accelerate evaluate scikit-learn
uv add huggingface-hub
```

### pyproject.toml

```toml
[project]
name = "hr-nlp-app"
version = "0.1.0"
description = "HR Review NLP Analysis Application"
requires-python = ">=3.10"

dependencies = [
    "fastapi>=0.110.0",
    "uvicorn>=0.29.0",
    "sqlalchemy>=2.0.0",
    "pydantic>=2.0.0",
    "transformers>=4.40.0",
    "torch>=2.0.0",
    "accelerate>=0.29.0",
    "evaluate>=0.4.0",
    "scikit-learn>=1.4.0",
    "huggingface-hub>=0.22.0",
    "python-dotenv>=1.0.0",
]
```

### Key uv Commands

```bash
uv init          # start new project
uv add           # install a package
uv remove        # uninstall a package
uv run           # run a script or command
uv sync          # install all deps (like npm install)
uv lock          # update the lockfile
```

### Run FastAPI

```bash
uv run uvicorn backend.main:app --reload
```

> **Note:** uv is for your local machine only. Colab still uses `!pip install`.

---

## 20. Workflow Summary

```
[HuggingFace Hub]
 Pre-trained BERT / Flan-T5
        ↓  pull (free, open source)
[Google Colab]
 Fine-tune on your HR dataset
 Model learns HR-specific patterns
        ↓  push (your improved model)
[HuggingFace Hub]
 your-username/hr-sentiment-model
 your-username/hr-ner-model
 your-username/hr-scoring-model
 your-username/hr-flan-t5-model
        ↓  download once (zip & extract)
[Your Local Project — ai/models/]
 hr-sentiment-model/
 hr-ner-model/
 hr-scoring-model/
 hr-flan-t5-model/
        ↓  load directly
[FastAPI Backend]
 runs models locally
 no API calls
 no tokens
 no rate limits
 no cost
        ↓
[SQLite Database]
 saves every analysis
        ↓
[React Frontend]
 displays results to HR manager
```

### 3 Phases

| Phase | Location | Tasks |
|---|---|---|
| Phase 1 — AI Work | Colab | Import base model → prepare HR dataset → fine-tune → evaluate → push to Hub |
| Phase 2 — Backend Work | VS Code + uv | Download models locally → build FastAPI → connect models → connect SQLite |
| Phase 3 — Frontend Work | VS Code | Build React dashboard → connect to FastAPI → display results |

---

## 21. Build Plan — Backend + Frontend with JWT

**Pages/Features chosen:**
- Submit review form
- Analysis results display
- Employee history dashboard
- Department analytics
- JWT Authentication

### Build Order

```
Backend (FastAPI)
├── Step 1  — Project setup (uv + folder structure)
├── Step 2  — config.py + .env
├── Step 3  — database.py
├── Step 4  — models/user.py + models/review.py
├── Step 5  — schemas/user.py + schemas/review.py
├── Step 6  — services/auth_service.py (JWT)
├── Step 7  — services/nlp_service.py (MOCK for now)
├── Step 8  — services/review_service.py
├── Step 9  — routers/auth.py
├── Step 10 — routers/reviews.py
├── Step 11 — routers/analytics.py
└── Step 12 — main.py

Frontend (React + Tailwind)
├── Step 13 — Vite setup + folder structure
├── Step 14 — api.js (axios config)
├── Step 15 — AuthContext (JWT handling)
├── Step 16 — Login page
├── Step 17 — Submit review form
├── Step 18 — Analysis results display
├── Step 19 — Employee history dashboard
└── Step 20 — Department analytics
```

### Mock NLP Service Strategy

The only file that touches the models is `backend/modules/nlp/service.py`.

```python
# RIGHT NOW (mock)
def full_analysis(text: str):
    return {
        "sentiment": {"label": "Positive", "confidence": 0.91},
        "skills_found": ["leadership", "communication"],
        "performance_score": {"score": "4/5", "confidence": 0.88},
        "recommendations": "Mock recommendation for now"
    }

# LATER — replace function body only, nothing else changes
def full_analysis(text: str):
    sentiment = sentiment_pipe(text)
    skills = ner_pipe(text)
    score = scoring_pipe(text)
    recommendations = generate_recommendations(sentiment, skills, score)
    return { ... }
```

---

## 22. Removing Unnecessary Folders

**Decision:** Remove `ai/data/` folder since all data preparation and fine-tuning happens in Colab, not locally.

```
Colab handles everything data related:
├── downloading the dataset (Kaggle, HuggingFace)
├── cleaning and labeling
├── tokenizing
├── training
└── pushing model to HuggingFace Hub

Your local project only receives the final result:
└── ai/models/hr-sentiment-model/  ← just the trained model, nothing else
```

**Decision:** Remove `ai/notebooks/` since notebooks are not needed to run the project.

---

## 23. Final Clean File Structure

```
hr-nlp-app/
│
├── ai/
│   └── models/                                 # ← YOUR FINE-TUNED MODELS LIVE HERE
│       ├── hr-sentiment-model/                 # Downloaded from HuggingFace Hub
│       │   ├── config.json
│       │   ├── pytorch_model.bin
│       │   ├── tokenizer_config.json
│       │   ├── vocab.txt
│       │   └── special_tokens_map.json
│       │
│       ├── hr-ner-model/
│       │   ├── config.json
│       │   ├── pytorch_model.bin
│       │   ├── tokenizer_config.json
│       │   └── vocab.txt
│       │
│       ├── hr-scoring-model/
│       │   ├── config.json
│       │   ├── pytorch_model.bin
│       │   ├── tokenizer_config.json
│       │   └── vocab.txt
│       │
│       └── hr-flan-t5-model/
│           ├── config.json
│           ├── pytorch_model.bin
│           ├── tokenizer_config.json
│           └── spiece.model
│
│
├── backend/                                    # Standalone FastAPI — works alone
│   │
│   ├── core/                                   # Shared foundation for all modules
│   │   ├── __init__.py
│   │   ├── config.py                           # All environment variables
│   │   ├── database.py                         # SQLite connection and session
│   │   └── security.py                         # JWT creation and verification
│   │
│   ├── modules/                                # Each module is independent
│   │   │
│   │   ├── auth/                               # Authentication module
│   │   │   ├── __init__.py
│   │   │   ├── router.py                       # POST /api/v1/auth/register
│   │   │   │                                   # POST /api/v1/auth/login
│   │   │   │                                   # GET  /api/v1/auth/me
│   │   │   ├── service.py                      # register, login, get_current_user
│   │   │   ├── schemas.py                      # UserCreate, UserLogin, UserOut, Token
│   │   │   └── model.py                        # User table definition
│   │   │
│   │   ├── nlp/                                # ← CORE PLUGIN MODULE
│   │   │   ├── __init__.py
│   │   │   ├── router.py                       # POST /api/v1/nlp/analyze
│   │   │   │                                   # POST /api/v1/nlp/batch-analyze
│   │   │   ├── service.py                      # loads models / MOCK now → real later
│   │   │   └── schemas.py                      # AnalyzeInput, AnalyzeOutput
│   │   │
│   │   ├── reviews/                            # Review storage module
│   │   │   ├── __init__.py
│   │   │   ├── router.py                       # GET  /api/v1/reviews
│   │   │   │                                   # GET  /api/v1/reviews/{employee_name}
│   │   │   │                                   # DELETE /api/v1/reviews/{id}
│   │   │   ├── service.py                      # save, get, delete review records
│   │   │   ├── schemas.py                      # ReviewRecord, ReviewOut
│   │   │   └── model.py                        # ReviewRecord table definition
│   │   │
│   │   └── analytics/                          # Analytics module
│   │       ├── __init__.py
│   │       ├── router.py                       # GET /api/v1/analytics/department
│   │       │                                   # GET /api/v1/analytics/overview
│   │       │                                   # GET /api/v1/analytics/employee/{name}
│   │       ├── service.py                      # aggregations and stats from DB
│   │       └── schemas.py                      # DepartmentStats, OverviewStats
│   │
│   └── main.py                                 # Registers all modules, CORS, DB init
│
│
├── frontend/                                   # React + Tailwind
│   ├── public/
│   └── src/
│       ├── components/
│       │   ├── Navbar.jsx
│       │   ├── ProtectedRoute.jsx              # Redirects if not logged in
│       │   └── LoadingSpinner.jsx
│       │
│       ├── pages/
│       │   ├── LoginPage.jsx
│       │   ├── SubmitReviewPage.jsx
│       │   ├── ResultsPage.jsx
│       │   ├── EmployeeHistoryPage.jsx
│       │   └── DepartmentAnalyticsPage.jsx
│       │
│       ├── context/
│       │   └── AuthContext.jsx                 # JWT token state management
│       │
│       ├── services/
│       │   └── api.js                          # All axios calls to FastAPI
│       │
│       ├── App.jsx
│       └── main.jsx
│   │
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
│
├── database/
│   └── hr_reviews.db                           # Auto-created on first run
│
├── .env                                        # Secret keys — NEVER commit
├── .gitignore
├── pyproject.toml                              # uv dependencies
├── uv.lock
└── README.md
```

### .gitignore Contents

```
.venv/
__pycache__/
*.pyc
*.pyo
.env
database/hr_reviews.db
ai/models/                    # model files too large for git
node_modules/
dist/
```

### config.py Model Paths

```python
# backend/core/config.py
class Settings(BaseSettings):
    MODELS_PATH: str = "./ai/models"
    SENTIMENT_MODEL: str = "./ai/models/hr-sentiment-model"
    NER_MODEL: str = "./ai/models/hr-ner-model"
    SCORING_MODEL: str = "./ai/models/hr-scoring-model"
    FLAN_T5_MODEL: str = "./ai/models/hr-flan-t5-model"
```

---

## Next Steps

The planning phase is complete. The next phase is coding, starting with:

1. `uv init` and folder creation
2. `backend/core/config.py` + `.env`
3. `backend/core/database.py`
4. Database models
5. Schemas
6. JWT auth service
7. Mock NLP service
8. Review service
9. All routers
10. `main.py`
11. React frontend setup
12. All pages

> **Key reminder:** `backend/modules/nlp/service.py` uses MOCK functions during development. When fine-tuned models are ready, only this one file changes — nothing else in the project needs modification.
