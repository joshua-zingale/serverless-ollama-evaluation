from argparse import ArgumentParser
from helpers import *
import asyncio
import pprint
import json

parser = ArgumentParser()

parser.add_argument("--seed", type=int, default=None)


args = parser.parse_args()

async def ask(question: str, start_time, clock: Clock) -> dict:
    '''
    Streams responses from a language model for a question

    Returns statistics within a dictionary about the generation:
     - request_time: time in seconds since the countdown's start that the first request was sent to the LLM
     - num_chars: number of characters generated from the language model before finishing, i.e. before either the generation or countdown ended
     - ttft: time in seconds since the request that the first token was received
     - finish_time: time in seconds since the countdown's start that the last token was received form the LLM
    '''
    stats = {'request_time': start_time, 'num_chars': 0}
    first = True
    async for chunk in await answer(question):
        if first and len(chunk['response']) > 0:
            first = False
            stats['ttft'] = clock.time() - start_time

        stats['num_chars'] += len(chunk['response'])

    stats['finish_time'] = clock.time()

    return stats

async def main():
    
    questions = QuestionSet()
    clock = Clock()
    tasks = []
    async for question in AsyncPacer(questions, clock, lambda x: 1 if x < 15 else None):
        task = asyncio.create_task(ask(question, clock.time(), clock))
        tasks.append(task)

    pending_tasks = asyncio.all_tasks()
    for task in pending_tasks:
        if task is not asyncio.current_task():
            task.cancel()

    results = sorted(
        filter(lambda x: not isinstance(x, asyncio.CancelledError),
               await asyncio.gather(*tasks, return_exceptions=True)),
                    key=lambda x: x['request_time'])
    
    filename = str(time.time()).replace(".","-")
    with open(f"data/results/{filename}.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    asyncio.run(main())