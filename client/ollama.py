import requests
from .config import OLLAMA_URL, MODEL_NAME


def get(prompt: str) -> requests.Response:
    return requests.post(OLLAMA_URL, data={"model": MODEL_NAME, "prompt": prompt})