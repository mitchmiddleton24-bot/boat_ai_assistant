import os
import sys

# Add inner src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Example usage (change as needed)
from stat_tracker import track_statistics

if __name__ == '__main__':
    stats = track_statistics()
    print("Weekly stats:", stats)
