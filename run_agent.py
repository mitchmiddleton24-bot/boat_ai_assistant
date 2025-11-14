import os
from dotenv import load_dotenv

# Always load .env no matter what
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)

from outlook_reader import read_emails

emails = read_emails()
print("Emails read:", emails)
