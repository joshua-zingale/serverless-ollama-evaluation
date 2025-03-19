from argparse import ArgumentParser
import requests
import json

def main():
    parser = ArgumentParser()

    parser.add_argument('url')
    parser.add_argument('start_time', type=float)
    parser.add_argument('length', type=float)

    args = parser.parse_args()

    args.end_time = args.start_time + args.length

    params = {
        'query': 'count(kube_pod_container_status_running{pod=~"ollama.*"})/2 or vector(0)',
        'step': '10s',
        'start': args.start_time,
        'end': args.end_time

    }
    with requests.get(f"{args.url}/api/v1/query_range", params=params) as resp:
        data = json.loads(resp.text)


    params = {
        'query': 'sum(rate(container_cpu_usage_seconds_total{pod=~"ollama.*"}[1m])) or vector(0)',
        'step': '10s',
        'start': args.start_time,
        'end': args.end_time

    }
    with requests.get(f"{args.url}/api/v1/query_range", params=params) as resp:
        data2 = json.loads(resp.text)


    params = {
        'query': 'sum(container_memory_usage_bytes{pod=~"ollama.*"}) or vector(0)',
        'step': '10s',
        'start': args.start_time,
        'end': args.end_time

    }
    with requests.get(f"{args.url}/api/v1/query_range", params=params) as resp:
        data3 = json.loads(resp.text)

    new_data = {'start_time': args.start_time, 'data': []}

    for (time, num_pods), (_, cpu_seconds_per_second), (_, memory_usage) in zip(data['data']['result'][0]['values'], data2['data']['result'][0]['values'], data3['data']['result'][0]['values']):
        new_data['data'].append([time - args.start_time, int(num_pods), float(cpu_seconds_per_second), int(memory_usage)])

    print(json.dumps(new_data))


if __name__ == "__main__":
    main()