from config import OLLAMA_URL, MODEL_NAME
from ollama import Client


client = Client(
  host=OLLAMA_URL,
)

def request(prompt: str , stream = False):
    return client.generate(model=MODEL_NAME, prompt = prompt, stream = stream)

def main():
    for i in request("What is two plus two minus seventeen?", stream = True):
        print(i)


if __name__ == "__main__":
    main()