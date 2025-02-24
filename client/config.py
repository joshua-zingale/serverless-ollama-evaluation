import os

# Data is from https://www.kaggle.com/datasets/frankossai/natural-questions-dataset?resource=download
# "Natural Questions Dataset"

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODEL_NAME = "deepseek-r1:1.5b"