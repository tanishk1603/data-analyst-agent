# Data Analyst Agent (Ultra-Safe Edition)

Fully hardened FastAPI app + minimal UI to analyze a dataset and answer questions.
- Windows-friendly requirements (prebuilt wheels where possible)
- Defensive parsing & plotting with graceful fallbacks
- Clear logs and unique per-run output dirs
- Optional LLMs via environment keys

## Run
```
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

uvicorn app.main:app --reload
# open http://localhost:8000
```
