from config import OLLAMA_URL, MODEL_NAME
from ollama import AsyncClient
import numpy as np
import random
import time


client = AsyncClient(
  host=OLLAMA_URL,
)

def answer(prompt: str):
    '''
    Send a prompt to Ollama to get a streaming response from the language model.
    '''
    return client.generate(model=MODEL_NAME, prompt = prompt, stream = True)

class QuestionSet():
    '''An iterable set of natural langauge questions that yields questions'''
    def __init__(self, seed = None):
        self.seed = seed
        self.questions = []
        with open("data/questions") as f:
            for line in f:
                self.questions.append(line[:-1])

    def __iter__(self):
        random.seed(self.seed)

        while True:
            yield self.questions[random.randint(0, len(self.questions) - 1)]

    
class Countdown():
    def __init__(self, length: float):
        self.start_time = time.time()

        self.length = length
        self.end_time = self.start_time + length

    def get_length(self):
        return self.length
    
    def bind(self, iter):
        '''Bind an iterator to continue only while the Countdown is ongoing.'''

        for item in iter:
            if self.finished():
                break
            yield item
            
    def ongoing(self):
        return time.time() < self.end_time

    def finished(self):
        return time.time() >= self.end_time

    def time_left(self):
        return max(self.end_time - time.time(), 0)
    
    def time_elasped(self):
        return time.time() - self.start_time