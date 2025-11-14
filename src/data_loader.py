# src/data_loader.py
import json
from pathlib import Path
import os

dummy_emails = [
    "Subject: Delay in HVAC install\nThe HVAC installation on the second floor has been delayed due to a missing part. Expected arrival: Thursday.",
    "Subject: Budget approval\nThe finance team approved the Q3 budget. No changes required.",
]

dummy_transcript = """
Project kickoff meeting for Building B.
- Discussed electrical subcontractor delays (need update by Thursday).
- Deadline confirmed for concrete pour: next Monday.
- John assigned to update architectural drawings.
- Follow-up: Send revised schedule by Friday.
"""

def get_dummy_emails():
    return dummy_emails

def get_dummy_transcript():
    return dummy_transcript.strip()

DATA_PATH = Path(__file__).resolve().parents[1] / "data"

def load_json_file(filename):
    file_path = DATA_PATH / filename
    if not file_path.exists():
        raise FileNotFoundError(f"{filename} not found in data folder.")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_email_data():
    return load_json_file("test_email_data.json")

def load_subcontractor_data():
    return load_json_file("mock_subs.json")

def load_transcript_data():
    return load_json_file("mock_transcripts.json")

def load_stats_summary():
    return load_json_file("mock_stats.json")

DATA_PATH = Path(__file__).resolve().parent / "data"  # Adjust this first
print("Resolved DATA_PATH:", DATA_PATH)

def load_json_file(filename):
    file_path = DATA_PATH / filename
    print(f"Looking for file: {file_path}")  # Add this line
    if not file_path.exists():
        raise FileNotFoundError(f"{filename} not found in data folder.")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)