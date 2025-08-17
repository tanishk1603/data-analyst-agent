
import csv, json, os, math
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SUPPORTED_EXTS = {".csv", ".xlsx", ".xls", ".json", ".parquet"}

def _safe_tight_save(path: Path):
    try: plt.tight_layout()
    except Exception: pass
    plt.savefig(path)
    plt.close()
    return f"/{path.as_posix()}"

def _sniff_csv_sep_and_header(path: Path, default_sep: str = ",", has_header: bool = True):
    sep = default_sep; header = 0 if has_header else None
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            sample = f.read(4096)
        sniff = csv.Sniffer()
        dialect = sniff.sniff(sample, delimiters=[",",";","|","\t"])
        sep = dialect.delimiter or default_sep
        header = 0 if sniff.has_header(sample) else None
    except Exception:
        pass
    return sep, header

def load_dataset(fpath: Path, has_header: bool = True, sep: str = ",") -> pd.DataFrame:
    if not fpath or not fpath.exists():
        raise FileNotFoundError("Dataset file not found.")
    ext = fpath.suffix.lower()
    if ext not in SUPPORTED_EXTS:
        raise ValueError(f"Unsupported dataset extension: {ext}")

    if ext == ".csv":
        sniffed_sep, sniffed_header = _sniff_csv_sep_and_header(fpath, default_sep=sep, has_header=has_header)
        header = 0 if has_header else None
        header = sniffed_header if has_header else None
        try:
            return pd.read_csv(fpath, sep=sniffed_sep or sep, header=header, low_memory=False, encoding="utf-8")
        except UnicodeDecodeError:
            return pd.read_csv(fpath, sep=sniffed_sep or sep, header=header, low_memory=False, encoding_errors="ignore")

    if ext in {".xlsx", ".xls"}:
        return pd.read_excel(fpath)
    if ext == ".json":
        try: return pd.read_json(fpath, lines=True)
        except ValueError: return pd.read_json(fpath, lines=False)
    if ext == ".parquet":
        return pd.read_parquet(fpath)
    raise ValueError("Unsupported format")

def sanitize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    new_cols = []
    seen = {}
    for c in df.columns:
        base = str(c).strip().replace("\n"," ").replace("\r"," ")
        if base not in seen:
            seen[base]=0; new_cols.append(base)
        else:
            seen[base]+=1; new_cols.append(f"{base}_{seen[base]}")
    df.columns = new_cols
    return df

def basic_profile(df: pd.DataFrame) -> Dict:
    if df is None or df.empty:
        return {"rows": 0, "cols": 0, "dtypes": {}, "missing_by_col": {}, "duplicates": 0, "memory_mb": 0.0}
    return {
        "rows": int(df.shape[0]),
        "cols": int(df.shape[1]),
        "dtypes": {c: str(t) for c, t in df.dtypes.items()},
        "missing_by_col": {c: int(df[c].isna().sum()) for c in df.columns},
        "duplicates": int(df.duplicated().sum()),
        "memory_mb": round(df.memory_usage(deep=True).sum() / (1024**2), 3),
    }

def _numeric_cols(df: pd.DataFrame) -> List[str]:
    return [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]

def _categorical_cols(df: pd.DataFrame) -> List[str]:
    nums = set(_numeric_cols(df)); return [c for c in df.columns if c not in nums]

def summarize_stats(df: pd.DataFrame) -> Dict[str, Dict]:
    if df is None or df.empty: return {}
    try:
        return df.describe(include="all", datetime_is_numeric=True).replace({np.nan: None}).to_dict()
    except Exception:
        return df.select_dtypes(include=[np.number]).describe().replace({np.nan: None}).to_dict()

def correlations(df: pd.DataFrame, out_dir: Path) -> Dict[str, object]:
    if df is None or df.empty: return {}
    res = {}
    num_cols = _numeric_cols(df)
    if len(num_cols) >= 2:
        try:
            corr_mat = df[num_cols].corr(method="pearson").fillna(0.0)
            plt.figure(figsize=(8,6)); plt.imshow(corr_mat.values, aspect="auto")
            plt.xticks(range(len(num_cols)), num_cols, rotation=90)
            plt.yticks(range(len(num_cols)), num_cols)
            plt.colorbar(label="Pearson r")
            res["pearson_heatmap"] = _safe_tight_save(out_dir / "corr_heatmap.png")
        except Exception: pass
    # Spearman top 10 (skip constant columns)
    pairs = []
    for i, a in enumerate(num_cols):
        for b in num_cols[i+1:]:
            try:
                a_vals = df[a].to_numpy(); b_vals = df[b].to_numpy()
                if len(a_vals)==0 or len(b_vals)==0: continue
                if np.all(a_vals == a_vals[0]) or np.all(b_vals == b_vals[0]): continue
                r = pd.Series(a_vals).corr(pd.Series(b_vals), method="spearman")
                if pd.notna(r): pairs.append(((a,b), float(r)))
            except Exception: continue
    pairs.sort(key=lambda x: abs(x[1]), reverse=True)
    res["spearman_top10"] = pairs[:10]
    # Categorical heuristic
    cat_cols = _categorical_cols(df); cat_pairs = []
    for i, a in enumerate(cat_cols):
        for b in cat_cols[i+1:]:
            try:
                ct = pd.crosstab(df[a].astype(str), df[b].astype(str))
                total = ct.values.sum()
                if total == 0 or ct.shape[0] < 2 or ct.shape[1] < 2: continue
                v = (ct.to_numpy() / total).max()
                if not np.isnan(v): cat_pairs.append(((a,b), float(v)))
            except Exception: continue
    cat_pairs.sort(key=lambda x: x[1], reverse=True)
    res["categorical_assoc_top10"] = cat_pairs[:10]
    return res

def plot_univariate(df: pd.DataFrame, out_dir: Path) -> List[str]:
    if df is None or df.empty: return []
    paths = []
    for col in _numeric_cols(df)[:12]:
        try:
            s = df[col].dropna().astype(float)
            if s.empty: continue
            plt.figure(figsize=(6,4)); plt.hist(s.values, bins=30)
            paths.append(_safe_tight_save(out_dir / f"hist_{col}.png"))
            plt.figure(figsize=(6,2.8)); plt.boxplot(s.values, vert=True); plt.title(col)
            paths.append(_safe_tight_save(out_dir / f"box_{col}.png"))
        except Exception: continue
    for col in _categorical_cols(df)[:12]:
        try:
            vc = df[col].astype(str).value_counts().head(20)
            if vc.empty: continue
            plt.figure(figsize=(7,4)); plt.bar(vc.index.astype(str), vc.values); plt.xticks(rotation=90); plt.title(col)
            paths.append(_safe_tight_save(out_dir / f"bar_{col}.png"))
        except Exception: continue
    return paths

def answer_questions(df: Optional[pd.DataFrame], questions: List[str], llm=None) -> Dict[str, str]:
    answers = {}
    for q in questions:
        q_clean = (q or "").strip()
        if not q_clean: continue
        ans = None
        try:
            ql = q_clean.lower()
            if df is None or df.empty:
                ans = "No dataset provided; generic answer only."
            elif ("how many" in ql and "row" in ql) or ("row" in ql and "count" in ql):
                ans = f"Rows: {len(df)}"
            elif ("column" in ql and "count" in ql) or ("how many" in ql and "column" in ql):
                ans = f"Columns: {df.shape[1]}"
            elif any(k in ql for k in ["missing","null","na"]):
                ans = f"Total missing cells: {int(df.isna().sum().sum())}"
            elif "correlation" in ql and "between" in ql:
                tokens = [t.strip(" ,.:;()[]") for t in q_clean.split()]
                cols = [c for c in df.columns if str(c).lower() in [t.lower() for t in tokens]]
                if len(cols) >= 2:
                    a,b = cols[:2]
                    try:
                        r = df[[a,b]].corr(method="pearson").iloc[0,1]
                        ans = f"Pearson({a},{b}) = {r:.3f}"
                    except Exception:
                        ans = f"Could not compute correlation for {a} and {b}."
            elif "top" in ql and ("value" in ql or "category" in ql):
                cat = [c for c in _categorical_cols(df) if df[c].nunique() > 1]
                if cat:
                    col = cat[0]; vc = df[col].value_counts().head(5).to_dict()
                    ans = f"Top values in {col}: {vc}"
            elif "mean" in ql or "average" in ql:
                nums = _numeric_cols(df)[:5]
                if nums:
                    means = {c: float(df[c].mean()) for c in nums}
                    ans = f"Means: {means}"
        except Exception as e:
            ans = f"Automatic parse failed: {e}"
        if ans is None and llm is not None:
            try: ans = llm(q_clean, df=df)
            except Exception as e: ans = f"LLM failed: {e}"
        if ans is None: ans = "Question recorded, but no automatic answer."
        answers[q] = ans
    return answers

def render_report(out_dir: Path, profile: Dict, stats: Dict, corr: Dict, artifacts: List[str], answers: Dict[str, str]) -> str:
    md = ["# Data Analyst Agent — Report","",
          "## Profile",
          f"- Rows: **{profile.get('rows',0)}**",
          f"- Columns: **{profile.get('cols',0)}**",
          f"- Duplicates: **{profile.get('duplicates',0)}**",
          f"- Memory: **{profile.get('memory_mb',0)} MB**","",
          "### Dtypes",""]
    for c,t in profile.get("dtypes",{}).items(): md.append(f"- `{c}`: {t}")
    md += ["","### Missing by Column",""]
    for c,m in profile.get("missing_by_col",{}).items(): md.append(f"- `{c}`: {m}")
    md += ["","## Summary Statistics","","```json", json.dumps(stats, indent=2), "```","",
           "## Correlations/Associations",""]
    if corr.get("pearson_heatmap"): md.append(f"![Pearson Heatmap]({corr['pearson_heatmap']})")
    md.append("### Spearman top pairs")
    for (a,b),r in corr.get("spearman_top10",[]): md.append(f"- {a} ↔ {b}: {r:.3f}")
    md.append("### Categorical association (heuristic)")
    for (a,b),v in corr.get("categorical_assoc_top10",[]): md.append(f"- {a} ↔ {b}: score={v:.3f}")
    md += ["","## Visuals",""]
    for p in artifacts: md.append(f"![{os.path.basename(p)}]({p})")
    md += ["","## Answers",""]
    for q,a in answers.items(): md.append(f"**Q:** {q}\n\n**A:** {a}\n")
    out_md = out_dir / "report.md"; out_md.write_text("\n".join(md), encoding="utf-8")
    return f"/{out_md.as_posix()}"
