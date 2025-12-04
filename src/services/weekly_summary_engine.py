import json
from services.openai_client import OpenAIClient
from services.anthropic_client import AnthropicClient
from services.graph_client import GraphClient

class WeeklySummaryEngine:
    def __init__(self):
        self.openai = OpenAIClient()
        self.claude = AnthropicClient()
        self.graph = GraphClient()

    def generate_weekly_report(self):
        # Get last week's emails
        emails = self.graph.get_last_week_emails()

        # Combine email subjects + bodies
        compiled_text = "\n\n".join([
            f"Subject: {e.get('subject')}\nBody: {e.get('bodyPreview')}"
            for e in emails
        ])

        prompt = f"""
You are an operations and construction analysis system.

Here is last week's raw communication extracted from Outlook:

{compiled_text}

Your tasks:
1. Identify project delays, risks, or blind spots.
2. Identify subcontractor problems or strengths.
3. Identify miscommunication or missing information.
4. Identify cost-saving opportunities the company may not realize.
5. Provide a short executive summary.
6. Provide recommended next steps.

Format output as:

EXECUTIVE SUMMARY:
...

ISSUES & RISKS:
...

SUBCONTRACTOR ANALYSIS:
...

COST SAVINGS:
...

RECOMMENDED ACTIONS:
...
"""

        response = self.claude.ask_claude(prompt)
        return response
