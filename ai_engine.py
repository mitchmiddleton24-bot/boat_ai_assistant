def analyze_contractors(data):
    # Placeholder logic
    return {"top_performers": [], "issues": []}
# At the bottom of ai_engine.py

def openai_call(prompt):
    # Mock response instead of real API for now
    return "Summary (mocked): Key decisions include assigning John to drawings. Concrete pour deadline confirmed."

def summarize_meeting(transcript: str):
    prompt = f"""You are a project assistant. Summarize this meeting with:
1. Key decisions
2. Deadlines
3. Assigned tasks
4. Missed follow-ups
---
Transcript:
{transcript}
"""
    return openai_call(prompt)
