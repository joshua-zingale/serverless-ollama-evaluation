from argparse import ArgumentParser
from load_functions import get_load
from helpers import *
import asyncio
import json
import time

async def main():
    start_time = time.time()

    parser = ArgumentParser()

    parser.add_argument("--load", type=str, default="constant")
    parser.add_argument("--load_params",nargs="*", type=str, default=[0.2])
    parser.add_argument("--initial_wait",type=float,default=0,help='time in seconds to be waited before the first request is sent')


    args = parser.parse_args()

    load = get_load(args.load, *args.load_params)
    
    questions = QuestionSet()
    clock = Clock()
    tasks = []
    async for question in AsyncPacer(questions, clock, load, initial_wait=args.initial_wait):
        task = asyncio.create_task(ask(question, clock.time(), clock))
        tasks.append(task)

    pending_tasks = asyncio.all_tasks()
    for task in pending_tasks:
        if task is not asyncio.current_task():
            task.cancel()

    results = sorted(
        filter(lambda x: not isinstance(x, BaseException),
               await asyncio.gather(*tasks, return_exceptions=True)),
                    key=lambda x: x['request_time'])
    
    filename = str(time.time()).replace(".","-")
    with open(f"data/results/{filename}.json", "w") as f:
        json.dump({'start_time': start_time, 'data': results}, f)

if __name__ == "__main__":
    asyncio.run(main())