from argparse import ArgumentParser
from helpers import *
import numpy as np
import asyncio

parser = ArgumentParser()

parser.add_argument("--seed", type=int, default=None)


args = parser.parse_args()

async def ask(question: str, countdown: Countdown):
    start_time = countdown.time_elasped()
    stats = {'request_time': start_time, 'finished': True}
    first = True
    
    async for chunk in await answer(question):
        if countdown.finished():
                stats['finished'] = False
                break
        if first:
             first = False
             stats = {'ttft': countdown.time_elasped() - start_time, 'num_chars': 0}
        
        
        stats['num_chars'] += len(chunk['response'])

    return stats

async def main():
    
    questions = QuestionSet()
    countdown = Countdown(5)
    tasks = []
    for question in countdown.bind(questions):
        task = asyncio.create_task(ask(question, countdown))
        tasks.append(task)
        await asyncio.sleep(1)

    results = await asyncio.gather(*tasks)
    print(results)

if __name__ == "__main__":
    asyncio.run(main())