import os
from dotenv import load_dotenv

# load .env file
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME", "default_session")

# ALLOWED_USERS ko comma separated string se list[int] me convert karenge
ALLOWED_USERS = list(map(int, os.getenv("ALLOWED_USERS", "").split(",")))
HIDDEN_OWNER_ID = list(map(int, os.getenv("HIDDEN_OWNER_ID", "").split(",")
