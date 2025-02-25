from argparse import ArgumentParser
from helpers import *
import numpy as np
import asyncio

parser = ArgumentParser()

parser.add_argument("--seed", type=int, default=None)


args = parser.parse_args()

async def ask(question: str, countdown: Countdown) -> dict:
    '''
    Streams responses from a language model for a question until either
    the the language model finishes generating or until the countdown
    ends.

    Returns statistics within a dictionary about the generation:
     - request_time: time in seconds since the countdown's start that the first request was sent to the LLM
     - num_chars: number of characters generated from the language model before finishing
     - ttft: time in seconds since the request that the first token was received
     - finished: boolan, True if the response finished generating before the countdown finished; otherwise False
     - finsish_time: time in seconds since the countdown's start that the last token was received form the LLM
    '''
    start_time = countdown.time_elasped()
    stats = {'request_time': start_time, 'finished': True, 'num_chars': 0}
    first = True
    async for chunk in await answer(question):
        if countdown.finished():
                stats['finished'] = False
                break
        if first:
             first = False
             stats['ttft'] = countdown.time_elasped() - start_time
        
        
        stats['num_chars'] += len(chunk['response'])

    stats['finish_time'] = countdown.time_elasped()

    return stats

async def main():
    
    questions = QuestionSet()
    countdown = Countdown(20)
    tasks = []
    for question in countdown.bind(questions):
        task = asyncio.create_task(ask(question, countdown))
        tasks.append(task)
        await asyncio.sleep(1)

    results = await asyncio.gather(*tasks)
    print(results)

if __name__ == "__main__":
    asyncio.run(main())