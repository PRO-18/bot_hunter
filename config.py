import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

# 🔹 Multiple session strings (comma separated in ENV)
SESSION_STRINGS = os.getenv("SESSION_STRINGS", "").split(",")

# 🔹 Allowed users (space separated IDs in ENV)
ALLOWED_USERS = list(map(int, os.getenv("ALLOWED_USERS", "").split()))
