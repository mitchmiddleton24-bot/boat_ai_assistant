# src/services/weekly_ai_engine.py

import datetime
import os
from typing import List, Dict, Any

from openai import OpenAI
import anthropic

from src.services.ms_graph_client import (
    get_recent_inbox_and_sent_emails,
    send_email,
)


# Load API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

openai_client = OpenAI(api_key=OPENAI_API_KEY)
claude_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)


def fetch_emails_last_7_days() -> List[Dict[str, Any]]:
    """
    Fetch emails from Inbox and Sent Items, keep only those from the past 7 days.
    Ensures all datetimes are timezone aware (UTC).
    """
    utc = datetime.timezone.utc
    now_utc = datetime.datetime.now(utc)
    cutoff = now_utc - datetime.timedelta(days=7)

    raw_emails = get_recent_inbox_and_sent_emails(top=200)
    filtered: List[Dict[str, Any]] = []

    for msg in raw_emails:
        dt_str = msg.get("receivedDateTime") or msg.get("sentDateTime")
        if not dt_str:
            continue

        dt = datetime.datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=utc)

        if dt >= cutoff:
            filtered.append(msg)

    return filtered

def group_emails_into_conversations(
    emails: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Group emails into conversation threads by conversationId.
    Sort messages inside each conversation by time.
    """
    conv_map: Dict[str, List[Dict[str, Any]]] = {}

    for msg in emails:
        conv_id = msg.get("conversationId") or "no-conversation-id"
        conv_map.setdefault(conv_id, []).append(msg)

    conversations: List[Dict[str, Any]] = []

    for conv_id, msgs in conv_map.items():
        # sort by sent or received time
        def sort_key(m: Dict[str, Any]):
            dt_str = m.get("sentDateTime") or m.get("receivedDateTime")
            if not dt_str:
                return ""
            return dt_str

        msgs_sorted = sorted(msgs, key=sort_key)

        conversations.append(
            {
                "conversationId": conv_id,
                "messages": msgs_sorted,
            }
        )

    return conversations

def extract_structured_items_gpt(
    conversations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Use GPT to extract structured insights from conversation threads.

    For each conversation, we want:
    - high level topic
    - main participants
    - status: open or closed
    - follow_up_needed: true/false
    - who_owes_next: "company", "external", or "none"
    - urgency 1 to 5
    - short summary

    GPT sees both inbound and outbound messages in each thread.
    """
    prompt = f"""
You are an AI operations analyst.

You are given JSON-like data representing email conversation threads.
Each thread contains messages with:
- from (email)
- to (list of emails)
- subject
- bodyPreview
- folder ("inbox" or "sent")
- timestamps
- conversationId

For each conversation, do the following:

1. Identify the main topic or purpose of the conversation.
2. Identify main external parties (subcontractors, customers, vendors).
3. Decide if the conversation is effectively "open" or "closed".
   - "open" means there is likely an outstanding issue, question, or task.
   - "closed" means the matter appears resolved or no further action is needed.
4. Decide if a follow up from the company is appropriate:
   - follow_up_needed = true only if it is reasonable that the company should respond again.
   - follow_up_needed = false if the last message closed the loop, or if silence is acceptable.
5. Determine who, if anyone, "owes" the next reply:
   - "company" if the company should respond next.
   - "external" if the subcontractor, customer, or vendor should respond next.
   - "none" if the thread is closed.
6. Rate urgency from 1 (low) to 5 (critical).
7. Provide a short operational summary of the conversation.

Return a single JSON-style Python dict with:
- conversations: list of items, each with:
  - conversationId
  - topic
  - main_parties
  - status  ("open" or "closed")
  - follow_up_needed  (true/false)
  - who_owes_next  ("company", "external", "none")
  - urgency  (1 to 5)
  - summary  (2 to 4 sentences)
- overall_insights: brief list of general observations across all conversations
- follow_ups_needed: list of the conversationIds where follow_up_needed is true

Here is the conversation data:
{conversations}
    """

    resp = openai_client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    try:
        return eval(resp.choices[0].message.content)
    except Exception:
        return {
            "conversations": [],
            "overall_insights": [],
            "follow_ups_needed": [],
        }

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
    1. Fetch last 7 days of emails (Inbox + Sent)
    2. Group them into conversation threads
    3. Extract structured items with GPT, including follow up needs
    4. Generate executive summary with Claude
    """
    emails = fetch_emails_last_7_days()
    conversations = group_emails_into_conversations(emails)
    structured = extract_structured_items_gpt(conversations)
    final_report = generate_weekly_report_claude(structured)

    return {
        "email_count": len(emails),
        "conversation_count": len(conversations),
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