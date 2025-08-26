import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")   # <-- ye chahiye
ALLOWED_USERS = list(map(int, os.getenv("ALLOWED_USERS", "").split()))
HIDDEN_OWNER_ID = int(os.getenv("HIDDEN_OWNER_ID", "0"))
