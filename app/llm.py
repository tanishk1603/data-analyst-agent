
import os
from typing import Optional, Callable
from dotenv import load_dotenv
load_dotenv()

def get_llm() -> Optional[Callable]:
    gemini_key = os.getenv("GEMINI_API_KEY") or ""
    openai_key = os.getenv("OPENAI_API_KEY") or ""
    timeout = int(os.getenv("LLM_TIMEOUT_SECONDS", "180"))
    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            def _ask(prompt: str, df=None):
                head = ""
                try:
                    if df is not None: head = df.head(20).to_csv(index=False)
                except Exception: head = ""
                rp = model.generate_content(
                    f"You are a data analyst. Dataset head (CSV):\\n{head}\\n\\nQuestion:\\n{prompt}\\nProvide a concise, factual answer.",
                    safety_settings=None,
                    request_options={"timeout": timeout}
                )
                return (rp.text or "").strip()
            return _ask
        except Exception:
            pass
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            def _ask(prompt: str, df=None):
                head = ""
                try:
                    if df is not None: head = df.head(20).to_csv(index=False)
                except Exception: head = ""
                msg = [
                    {"role": "system", "content": "You are a precise data analyst."},
                    {"role": "user", "content": f"Dataset head (CSV):\\n{head}\\n\\nQuestion:\\n{prompt}"}
                ]
                rp = client.chat.completions.create(model="gpt-4o-mini", messages=msg, timeout=timeout)
                return rp.choices[0].message.content.strip()
            return _ask
        except Exception:
            pass
    return None
