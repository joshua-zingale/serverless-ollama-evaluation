from config import OLLAMA_URL, MODEL_NAME
from ollama import AsyncClient
import random
import time
import asyncio

client = AsyncClient(
  host=OLLAMA_URL,
)

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
    def __init__(self, generator, clock, pacing_function, initial_wait = 0):
        self.generator = generator
        self.pacing_function = pacing_function
        self.clock = clock
        self.initial_wait = initial_wait

    async def __aiter__(self):

        extra_wait = self.clock.time()
        if self.initial_wait > 0:
            await asyncio.sleep(self.initial_wait)
            
        for e in self.generator:
            yield e
            wait_time = self.pacing_function(self.clock.time())
            if not wait_time:
                break
            wait_time -= extra_wait
            
            before_wait = self.clock.time()
            await asyncio.sleep(max(wait_time, 0))
            actual_wait = self.clock.time() - before_wait
            extra_wait = actual_wait - max(wait_time, 0)
            
        



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


async def ask(question: str, start_time, clock: Clock) -> dict:
    '''
    Streams responses from a language model for a question

    Returns statistics within a dictionary about the generation:
     - request_time: time in seconds since the countdown's start that the first request was sent to the LLM
     - num_chars: number of characters generated from the language model before finishing, i.e. before either the generation or countdown ended
     - ttft: time in seconds since the request that the first token was received
     - finish_time: time in seconds since the countdown's start that the last token was received form the LLM
    '''
    stats = {'request_time': start_time, 'num_chars': 0, 'finished': False, 'ttft': None}
    first = True

    try:
        async for chunk in await client.generate(model=MODEL_NAME, prompt = question, stream = True):
            if first and len(chunk['response']) > 0:
                first = False
                stats['ttft'] = clock.time() - start_time

            stats['num_chars'] += len(chunk['response'])

        stats['finish_time'] = clock.time()
        stats['finished'] = True
    except asyncio.CancelledError:
       return stats
    return stats


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