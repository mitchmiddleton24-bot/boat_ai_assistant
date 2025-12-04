# src/services/weekly_summary_engine.py

import os
from pathlib import Path
from typing import List

from .openai_client import summarize_text  # we will define this in openai_client.py

BASE_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = BASE_DIR / "data" / "uploaded_files"
REPORTS_DIR = BASE_DIR / "data" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def _load_uploaded_texts() -> List[str]:
    """
    Load text from all files in the uploaded_files folder.
    For now we handle .txt and .md. You can extend this later.
    """
    if not UPLOAD_DIR.exists():
        return []

    texts: List[str] = []
    for path in UPLOAD_DIR.iterdir():
        if path.is_file() and path.suffix.lower() in {".txt", ".md"}:
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
                if content.strip():
                    texts.append(f"File: {path.name}\n\n{content}")
            except Exception:
                # Skip unreadable files for now
                continue
    return texts


def generate_weekly_report() -> str:
    """
    Build a real weekly report using OpenAI over uploaded files.

    - Reads all text files from src/data/uploaded_files
    - Sends them to OpenAI for summarization
    - Writes the summary to src/data/reports/weekly_report.txt
    - Returns the path as a string
    """
    texts = _load_uploaded_texts()

    if not texts:
        summary = (
            "Weekly report\n\n"
            "No uploaded files were found in src/data/uploaded_files, "
            "so there is nothing to summarize this week."
        )
    else:
        joined = "\n\n\n---\n\n\n".join(texts)
        prompt = (
            "You are an operations analyst for a construction or service company.\n"
            "You will receive raw notes, emails, and meeting transcripts combined "
            "from the past week.\n\n"
            "Write a concise weekly executive summary with sections:\n"
            "1. Key wins\n"
            "2. Problems and risks\n"
            "3. Subcontractor or vendor issues (if any)\n"
            "4. Time and cost saving opportunities\n\n"
            "Use short bullet points under each heading. Avoid fluff."
        )

        summary = summarize_text(prompt=prompt, content=joined)

    report_path = REPORTS_DIR / "weekly_report.txt"
    report_path.write_text(summary, encoding="utf-8")

    # Return a path string relative to project root to keep it simple
    rel_path = os.path.relpath(report_path, BASE_DIR.parent)
    return rel_path
