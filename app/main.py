
import os, traceback
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .processing import (
    load_dataset, sanitize_columns, basic_profile, summarize_stats,
    correlations, plot_univariate, answer_questions, render_report
)
from .llm import get_llm
from .utils import get_logger, new_run_dir

logger = get_logger("app")

APP_ROOT = Path(__file__).resolve().parent.parent
OUTPUTS_ROOT = APP_ROOT / "outputs"
OUTPUTS_ROOT.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Data Analyst Agent (Ultra-Safe)", version="1.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(APP_ROOT / "static")), name="static")
app.mount("/outputs", StaticFiles(directory=str(APP_ROOT / "outputs")), name="outputs")
templates = Jinja2Templates(directory=str(APP_ROOT / "templates"))

class ApiResponse(BaseModel):
    report_path: Optional[str] = None
    artifacts: List[str] = Field(default_factory=list)
    answers: dict = Field(default_factory=dict)
    run_id: Optional[str] = None

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    rid = os.urandom(4).hex()
    logger.error("Unhandled error [%s]: %s\n%s", rid, exc, traceback.format_exc())
    return JSONResponse(status_code=500, content={"error": "Internal Server Error", "ref": rid})

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/summary")
async def summary():
    return {
        "app": "Data Analyst Agent (Ultra-Safe)",
        "version": "1.2.0",
        "outputs_exists": OUTPUTS_ROOT.exists(),
        "env_llm": {
            "GEMINI_API_KEY": bool(os.getenv("GEMINI_API_KEY")),
            "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
        },
    }

@app.post("/api", response_model=ApiResponse)
async def api(
    dataset: Optional[UploadFile] = File(default=None),
    questions: UploadFile = File(...),
    has_header: str = Form("true"),
    sep: str = Form(","),
):
    run_dir = new_run_dir()
    run_id = run_dir.name
    logger.info("Run %s started", run_id)

    # Save inputs
    ds_path = None
    if dataset is not None:
        ds_ext = Path(dataset.filename).suffix.lower()
        if ds_ext not in {".csv", ".xlsx", ".xls", ".json", ".parquet"}:
            raise HTTPException(400, f"Unsupported dataset type: {ds_ext}")
        ds_path = run_dir / ("dataset" + ds_ext)
        try:
            with open(ds_path, "wb") as f:
                f.write(await dataset.read())
        except Exception as e:
            logger.error("Run %s dataset save failed: %s", run_id, e)
            raise HTTPException(400, f"Could not save dataset: {e}")

    q_path = run_dir / "questions.txt"
    try:
        with open(q_path, "wb") as f:
            f.write(await questions.read())
    except Exception as e:
        logger.error("Run %s questions save failed: %s", run_id, e)
        raise HTTPException(400, f"Could not save questions: {e}")

    # Load dataset (optional)
    df = None
    if ds_path is not None:
        try:
            df = load_dataset(ds_path, has_header=(has_header.lower() == "true"), sep=sep)
        except Exception as e:
            logger.error("Run %s dataset load failed: %s", run_id, e)
            raise HTTPException(400, f"Failed to read dataset: {e}")
        try:
            df = sanitize_columns(df)
        except Exception as e:
            logger.error("Run %s sanitize failed: %s", run_id, e)

    # Parse questions
    try:
        q_list = [ln.strip() for ln in q_path.read_text(encoding="utf-8", errors="ignore").splitlines() if ln.strip()]
        if not q_list:
            q_list = ["How many rows are there?", "How many columns are there?"]
    except Exception as e:
        logger.error("Run %s question parse failed: %s", run_id, e)
        raise HTTPException(400, f"Could not parse questions: {e}")

    # EDA
    try:
        profile = basic_profile(df) if df is not None else {"rows": 0, "cols": 0, "duplicates": 0, "memory_mb": 0, "missing_by_col": {}, "dtypes": {}}
        stats = summarize_stats(df) if df is not None and not df.empty else {}
        corr = correlations(df, run_dir) if df is not None and not df.empty else {}
        artifacts = plot_univariate(df, run_dir) if df is not None and not df.empty else []
    except Exception as e:
        logger.error("Run %s EDA failed: %s", run_id, e)
        profile, stats, corr, artifacts = (basic_profile(df) if df is not None else {}), {}, {}, []

    # Answers
    try:
        llm = get_llm()
    except Exception:
        llm = None
    try:
        answers = answer_questions(df, q_list, llm=llm)
    except Exception as e:
        logger.error("Run %s answer questions failed: %s", run_id, e)
        answers = {q: "Failed to answer due to internal error." for q in q_list}

    # Report
    try:
        report_path = render_report(run_dir, profile, stats, corr, artifacts, answers)
    except Exception as e:
        logger.error("Run %s render report failed: %s", run_id, e)
        report_path = None

    logger.info("Run %s finished", run_id)
    return ApiResponse(report_path=report_path, artifacts=artifacts, answers=answers, run_id=run_id)
