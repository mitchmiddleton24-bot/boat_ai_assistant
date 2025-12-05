# src/services/weekly_ai_engine.py

import datetime
import os
from typing import List, Dict, Any

from openai import OpenAI
import anthropic

from src.services.ms_graph_client import get_recent_emails
from src.services.ms_graph_client import send_email


# Load API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

openai_client = OpenAI(api_key=OPENAI_API_KEY)
claude_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)


def fetch_emails_last_7_days() -> List[Dict[str, Any]]:
    """
    Fetch emails and keep only those from the past 7 days.
    Ensures all datetimes are timezone-aware (UTC).
    """
    utc = datetime.timezone.utc
    now_utc = datetime.datetime.now(utc)
    cutoff = now_utc - datetime.timedelta(days=7)

    raw_emails = get_recent_emails(top=50)
    filtered = []

    for msg in raw_emails:
        dt_str = msg["receivedDateTime"]

        # Convert '2025-12-03T13:13:31Z' to an aware datetime
        dt = datetime.datetime.fromisoformat(
            dt_str.replace("Z", "+00:00")
        )

        # Ensure dt is aware, just in case
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=utc)

        if dt >= cutoff:
            filtered.append(msg)

    return filtered

def extract_structured_items_gpt(emails: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Use GPT to extract structured insights from email metadata.
    Later we can pass the full body.
    """
    prompt = f"""
You are an AI operations analyst.

You are given a JSON list of email metadata (subject, sender, timestamps).
Extract structured information needed for a weekly construction or service-company report.

For each email, extract:
- subcontractor or responsible party (guess if needed)
- issue type (delay, scheduling, approval, materials, customer complaint, update)
- urgency from 1 to 5
- project reference if mentioned
- summary of what the email represents

Return a JSON object with fields:
- items: list of extracted items
- subcontractors: list of unique subcontractors or parties
- issues_by_category: {{}}

Here is the email data:
{emails}
    """

    resp = openai_client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    try:
        return eval(resp.choices[0].message.content)
    except Exception:
        return {"items": [], "subcontractors": [], "issues_by_category": {}}


def generate_weekly_report_claude(structured: Dict[str, Any]) -> str:
    """
    Claude produces the final polished executive summary.
    """
    prompt = f"""
You are an expert operations analyst and executive report writer.

You are given structured operational insights extracted from emails:
{structured}

Create a polished, professional weekly report that includes:

1. Executive Summary (5-8 sentences)
2. Subcontractor Performance Overview
3. Key Issues & Delays
4. Approvals Needed
5. Material or Supply Chain Notes
6. Customer or Client Concerns
7. Estimated Risks for Next Week
8. Recommended Actions

Write clearly, formally, and concisely.  
The report should be suitable for a construction owner or operations executive.

Return the final report as plain text.
    """

    resp = claude_client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1200,
        temperature=0.2,
        messages=[{"role": "user", "content": prompt}],
    )

    return resp.content[0].text


def generate_weekly_ai_report() -> Dict[str, Any]:
    """
    Main orchestrator:
    1. Fetch last 7 days of emails
    2. Extract structured items with GPT
    3. Generate executive summary with Claude
    """
    emails = fetch_emails_last_7_days()
    structured = extract_structured_items_gpt(emails)
    final_report = generate_weekly_report_claude(structured)

    return {
        "email_count": len(emails),
        "structured_data": structured,
        "final_report": final_report,
    }

def generate_and_email_weekly_report(to_addresses: list[str]) -> dict:
    """
    1. Generate the weekly AI report.
    2. Email the final report text to the given recipients.
    Returns the same dict as generate_weekly_ai_report, plus a 'sent_to' field.
    """
    result = generate_weekly_ai_report()
    final_report_text = result["final_report"]

    subject = "Weekly Operations AI Report"
    body_text = final_report_text

    send_email(subject=subject, body_text=body_text, to_addresses=to_addresses)

    result["sent_to"] = to_addresses
    return result