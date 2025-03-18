from matplotlib import pyplot as plt
from argparse import ArgumentParser
import numpy as np
import json


def main():

    parser = ArgumentParser()

    parser.add_argument('filename',help='data file to be loaded and visualized')
    parser.add_argument('-g', action="store_true")

    args = parser.parse_args()

    with open(args.filename) as f:
        data = json.load(f)
    
    # Done to account for legacy format where all data were stored directly instead
    # of in data['data']
    if 'data' in data:
        data, start_time = data['data'], data['start_time']

    finished = list(filter(lambda x: x['finished'] == True, data))
    print(f"Requests sent: {len(data)}, Requests finished: {len(finished)}")
    num_chars = sum(map(lambda x: x["num_chars"], data))
    print(f"Total characters received: {num_chars}")

    ttfts = np.array(list(map(lambda x: x['ttft'], finished)))

    print(f"Average ttft: {ttfts.mean()}")

    print()

    request_times = list(map(lambda x: x['request_time'], data))

    rt_deltas = [(rt1 - rt0) for rt0,rt1 in zip(request_times[:-1],request_times[1:])]

    if args.g:
        plt.plot(request_times[:-1], rt_deltas)
        plt.show()


if __name__ == "__main__":
    main()