import os
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def format_report(email_summary, meeting_summary, insights):
    return f"""
🚧 Weekly Report – {datetime.today().strftime('%Y-%m-%d')}

📩 Email Summary:
{email_summary}

📝 Meeting Summary:
{meeting_summary}

🔍 Observations:
{insights}
"""
