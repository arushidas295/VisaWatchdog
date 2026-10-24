import os

from dotenv import load_dotenv

print("Python folder:", os.getcwd())
print(".env file milti hai:", os.path.exists(".env"))

load_dotenv()
k = os.getenv("TINYFISH_API_KEY", "")

print("length:", len(k))
print("starts ok:", k.startswith("sk-tinyfish-"))
print("has space or quote:", any(c in k for c in " \"'"))