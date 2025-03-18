import json

with open('data/results/tmp4.json' , 'r') as f:
    data = json.load(f)['data']


max_concurrent = 0
ongoing = []
for datum in filter(lambda x: x['finished'], data):
    rt = datum['request_time'] + datum['ttft']
    
    ongoing = list(filter(lambda ft: ft > rt, ongoing))

    ongoing.append(datum['finish_time'])

    max_concurrent = max(max_concurrent, len(ongoing))

print(max_concurrent)
