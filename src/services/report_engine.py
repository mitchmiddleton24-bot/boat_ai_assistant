import os

DATA_DIR = os.path.join("src", "data", "reports")
os.makedirs(DATA_DIR, exist_ok=True)

def generate_dummy_weekly_report():
    file_path = os.path.join(DATA_DIR, "weekly_report.txt")
    with open(file_path, "w") as f:
        f.write("This is a dummy weekly report. Replace with real logic soon.")
    return file_path
