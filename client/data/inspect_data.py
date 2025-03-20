import json
import os


for file in filter(lambda x: "prometheus" not in x, os.listdir("presentation")):
    with open(f'presentation/{file}') as f:
        data = json.load(f)

    start_time, data = data['start_time'], data['data']

    end_time = data[-1]['request_time']
    not_finished = list(filter(lambda x: not x['finished'], data))
    finished = list(filter(lambda x: x['finished'], data))
    no_char = list(filter(lambda x: x['num_chars'] == 0, data))

    


    num_finished = len(finished)

    print(f"{file}\n {num_finished}/{len(data)} {[x['request_time']/end_time for x in no_char]}\n")
