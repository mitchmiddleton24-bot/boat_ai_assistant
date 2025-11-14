# src/report_generator.py
import json
from datetime import datetime
from claude_formatter import rewrite_with_claude

def generate_ops_report(transcripts, emails, subs):
    report = []
    report.append(f"Operations Report - {datetime.now().strftime('%Y-%m-%d')}")
    report.append("=" * 60)

    # Transcripts
    report.append("Meeting Summary:")
    for t in transcripts:
        report.append(f"- {t}")

    # Emails
    report.append("\nEmail Highlights:")
    for e in emails:
        report.append(f"- {e}")

    # Subcontractors
    report.append("\nSubcontractor Performance:")
    for s in subs:
        report.append(f"- {s}")

    return "\n".join(report)

def generate_exec_report(stats, transcripts):
    report = []
    report.append(f"Executive Report - {datetime.now().strftime('%Y-%m-%d')}")
    report.append("="*60)

    # Stats summary
    report.append("\nTeam Metrics:")
    for metric, value in stats.items():
        report.append(f"- {metric}: {value}")

    # Blind spots
    report.append("\nUnobserved Blind Spots:")
    for t in transcripts:
        for b in t.get("blind_spots", []):
            report.append(f"- {b}")

    # Recommendations
    report.append("\nRecommendations:")
    for t in transcripts:
        for r in t.get("recommendations", []):
            report.append(f"- {r}")

    return "\n".join(report)

# Local test (optional):
if __name__ == "__main__":
    with open("data/mock_transcripts.json") as f:
        transcripts = json.load(f)
    with open("data/test_email_data.json") as f:
        emails = json.load(f)
    with open("data/mock_subs.json") as f:
        subs = json.load(f)
    with open("data/mock_stats.json") as f:
        stats = json.load(f)

    ops_report = generate_ops_report(transcripts, emails, subs)
    with open("weekly_ops_report.txt", "w") as f:
        f.write(ops_report)

    exec_report = generate_exec_report(stats, transcripts)
    with open("weekly_exec_report.txt", "w") as f:
        f.write(exec_report)

# Auto-polish with Claude
with open("weekly_exec_report.txt", "r") as f:
    raw_exec = f.read()
polished_exec = rewrite_with_claude(raw_exec)
with open("weekly_exec_report_claude.txt", "w") as f:
    f.write(polished_exec)

with open("weekly_ops_report.txt", "r") as f:
    raw_ops = f.read()
polished_ops = rewrite_with_claude(raw_ops)
with open("weekly_ops_report_claude.txt", "w") as f:
    f.write(polished_ops)

print("✅ Polished reports written to weekly_exec_report_claude.txt and weekly_ops_report_claude.txt")
