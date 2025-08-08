# TalentMatch AI — Candidate Recommendation Engine

Intelligent web app that ranks candidate resumes against a job description using a TF-IDF-style similarity score and generates concise, professional fit summaries via **Claude**.

-  **Match Scoring:** Simple word-frequency embeddings + cosine similarity  
-  **AI Summaries:** 2–3 sentence justification per candidate (Claude)  
-  **Resume Inputs:** Paste text (separate candidates with `---`) and/or upload **.txt** or **.pdf**  
-  **Limits:** Up to **10** total candidates (text + files), shows **Top 10**  
- **Key Security:** No keys in code; uses environment variables (`.env` locally, Render secrets in prod)

---

## Architecture

- **Frontend:** `index.html` (vanilla JS + PDF.js)  
  - Parses uploaded PDFs in the browser  
  - Computes similarity client-side  
  - Calls backend once per candidate to get an AI summary
- **Backend:** `app.py` (Flask)  
  - `/` serves `index.html`  
  - `/analyze` calls Anthropic Claude and returns a brief analysis  
  - Fallback summary is used if Claude API fails so **Top 10** always renders

---

## Repo Contents

.
├── app.py # Main Streamlit/Flask app
├── index.html # Frontend template
├── requirements.txt # Python dependencies
├── .env.example # Example environment variables (safe to commit)
├── .gitignore # Git ignore rules (includes .env, venv, etc.)
├── README.md # Project documentation



---

## Prerequisites

- Python 3.9+  
- An Anthropic **Claude** API key

---

## Setup (Local)

1. **Clone & install:**
```bash
pip install -r requirements.txt
```


Secrets: create .env in the project root (do not commit this):

# .env (local only)
```bash
CLAUDE_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

(An example is provided at .env.example — safe to commit.)

Run the server:
```bash
python app.py
# Open http://127.0.0.1:8000
```

Usage: 

1. Paste a job description.

2. Add candidates via:

3. Text area — separate each candidate with a line containing ---, and/or

4. Upload up to 10 total .txt/.pdf files

5. Click Analyze Candidates.

6. Review the Top 10 ranked candidates with AI summaries.

Tip: The first line of each text candidate is used as the candidate’s name.
