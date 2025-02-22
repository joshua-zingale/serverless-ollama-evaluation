import os

OLLAMA_URL = os.environ.get("OLLAMA_URL", "https://localhost:11434") + f"{os.sep}api{os.sep}generate"
MODEL_NAME = "deepseek-r1:1.5b"