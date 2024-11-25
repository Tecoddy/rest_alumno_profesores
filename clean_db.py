import requests
import sys
from main import db

def clean_database(base_url):
    """
    Sends a POST request to the clean database endpoint.
    """
    try:
        response = requests.post(f"{base_url}/clean_database")
        if response.status_code == 200:
            print("Database cleaned successfully:", response.json())
        else:
            print("Failed to clean database:", response.json())
    except Exception as e:
        print(f"Error cleaning database: {e}")

def reset_database():
    """
    Sends a POST request to the reset database.
    """
    try:
        response = requests.post(f"{base_url}/reset_database")
        if response.status_code == 200:
            print("Database reset successfully:", response.json())
        else:
            print("Failed to reset database:", response.json())
    except Exception as e:
        print(f"Error resetting database: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python clean_db.py <base_url> <action>")
        print("Actions: clean or reset")
        sys.exit(1)

    base_url = sys.argv[1]
    action = sys.argv[2].lower()

    if action == "clean":
        clean_database(base_url)
    elif action == "reset":
        reset_database()
    else:
        print("Invalid action. Use 'clean' or 'reset'.")