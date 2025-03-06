from config import OLLAMA_URL, MODEL_NAME
from ollama import AsyncClient
import random
import time
import asyncio

client = AsyncClient(
  host=OLLAMA_URL,
)

def answer(prompt: str):
    '''
    Send a prompt to Ollama to get an asynchronous streaming response from the language model.
    '''
    return client.generate(model=MODEL_NAME, prompt = prompt, stream = True)

class QuestionSet():
    '''An iterable set of natural langauge questions that yields questions'''
    def __init__(self, n: int = 1000, seed = None):
        self.seed = seed
        self.questions = []
        with open("data/questions") as f:
            for i, line in enumerate(f):
                if i == n:
                    break
                self.questions.append(line[:-1])

    def get(self):
        return self.questions[random.randint(0, len(self.questions) - 1)]
    
    def __iter__(self):
        random.seed(self.seed)

        while True:
            yield self.questions[random.randint(0, len(self.questions) - 1)]


class AsyncPacer():
    """
    Wraps around any generator to make a rate-limited asyncronous iterator.

    The iterator will continue to provide a next element until
    either the generator runs out of elements or until the pacing
    function returns None.

    The pacing function determines how much time is artificially placed
    between each iteration with a non-blocking sleep.
    """
    def __init__(self, generator, clock, pacing_function):
        self.generator = generator
        self.pacing_function = pacing_function
        self.clock = clock

    async def __aiter__(self):
       
       before_gen = self.clock.time()
       for e in self.generator:
            yield e
            wait_time = self.pacing_function(self.clock.time())
            if not wait_time:
                break
            
            generation_time = self.clock.time() - before_gen
            await asyncio.sleep(max(wait_time - generation_time, 0))
            before_gen = self.clock.time()
            
        



class Clock():
        def __init__(self):
            self.start_time = time.time()
            self.running = True
        def time(self):
            return time.time() - self.start_time
        def stop(self):
            self.running = False
        def running(self):
            return self.running


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