import os
from dotenv import load_dotenv

print("folder:", os.getcwd())
print(".env exists:", os.path.exists(".env"))

load_dotenv()
k = os.getenv("TINYFISH_API_KEY", "")

print("length:", len(k))
print("starts ok:", k.startswith("sk-tinyfish-"))
print("has space:", " " in k)
