from matplotlib import pyplot as plt
import numpy as np
import json
import os


def main():
    for file in filter(lambda x: "prometheus" not in x, sorted(os.listdir("data/presentation"))):
        with open(f'data/presentation/{file}') as f:
            c_data = json.load(f)
        with open(f'data/presentation/prometheus-{file}') as f:
            p_data = json.load(f)


        c_data, client_start_time = list(filter(lambda x: x['finished'],c_data['data'])), p_data['start_time']
        p_data, prometheus_start_time = p_data['data'], p_data['start_time']

        assert client_start_time == prometheus_start_time, "The two files must have the same start time"

        c_data = clean_client_data(c_data)
        p_data = clean_server_data(p_data)

        fig, axes = plt.subplots(3)

        for ax in axes:
            ax.set_xlabel('Times (s)')

        title = ''
        if 'constant' in file:
            title += 'Slow Constant'
        elif 'sinusoidal' in file:
            title += 'Sinusoidal'
        elif 'spikes' in file:
            title += 'Spiking'

        title += ' Load with '

        if '12-pods' in file:
            title += 'Twelve Pods Provisioned'
        elif '8-pods' in file:
            title += 'Eight Pods Provisioned'
        elif 'autoscaling':
            title += 'Autoscaling'



        
        axes[0].set_title(title)
        axes[0].set_ylabel('Requests/Second', color = 'blue')
        axes[0].plot(c_data['time'], c_data['rps'], label='RPS', color = 'blue')
        axes[0].tick_params(axis='y', labelcolor='blue')



        ax01 = axes[0].twinx()
        ax01.set_ylabel('# Active Pods', color = 'green')
        ax01.plot(p_data['time'], p_data['num_pods'], label='# Active Pods', color = 'green')
        ax01.tick_params(axis='y', labelcolor='green')
        

        axes[1].set_ylabel('Memory (GB)', color='red')
        axes[1].plot(p_data['time'], p_data['memory_gb'], label='Memory', color = 'red')
        axes[1].tick_params(axis='y', labelcolor='red')


        ax11 = axes[1].twinx()
        ax11.set_ylabel('CPU Seconds', color='purple')
        ax11.plot(p_data['time'], p_data['cpu_seconds'], label='CPU Seconds', color='purple')
        ax11.tick_params(axis='y', labelcolor='purple')



        axes[2].set_ylabel('Characters/Second/Request', color='orange')
        axes[2].plot(c_data['time'], c_data['cpspr'], color='orange')
        axes[2].scatter(*get_cpspr_dots(c_data), color='orange')
        axes[2].tick_params(axis='y', labelcolor='orange')


        non_none_cpspr = list(filter(lambda x: x, c_data['cpspr']))
        non_none_ttft = list(filter(lambda x: x, c_data['ttft']))
        ax21 = axes[2].twinx()
        ax21.set_ylabel('Time Till First Token', color='brown')
        ax21.plot(np.array(c_data['time']), c_data['ttft'], label=f'TTFT: m={np.mean(non_none_ttft):0.2}, s={np.std(non_none_ttft):0.2}\nCPSPR: m={int(np.mean(non_none_cpspr))}, s={int(np.std(non_none_cpspr))}', color='brown')
        ax21.scatter(*get_ttft_dots(c_data), color='brown')
        ax21.tick_params(axis='y', labelcolor='brown')

        ax21.legend()

        fig.tight_layout()
        fig.figure(figsize=(8,5))
        plt.savefig(f'images/{title.lower().replace(" ", "-")}.png', dpi=300)


def dict_to_vec(dict, key):
    return [d[key] for d in dict]



def clean_server_data(data):
    new_data = {
        'time': [],
        'num_pods': [],
        'cpu_seconds': [],
        'memory_gb': []
    }

    for time, num_pods, cpu_seconds, memory_bytes in data:
        new_data['time'].append(time)
        new_data['num_pods'].append(num_pods)
        new_data['cpu_seconds'].append(cpu_seconds)
        new_data['memory_gb'].append(memory_bytes/2**30)

    new_data['num_pods'] = new_data['num_pods'][2:-18]

    for field in new_data:
        if field == 'num_pods':
            continue
        new_data[field] = new_data[field][:-20]

    return new_data




def clean_client_data(data, dt = 10):
    start = data[0]['request_time']
    end = data[-1]['request_time']

    new_data = {
        'time': [],
        'rps': [],
        'cps': [],
        'ttft': [],
        'time_to_finish': [],
        'cpspr': []
    }
    i = 0
    for s in np.arange(start, end, dt):
        e = s + dt

        num_requests = 0
        num_chars = 0
        sum_ttft = 0
        sum_time_to_finish = 0
        sum_chars_per_second = 0
        while (i < len(data) and data[i]['request_time'] < e):
            num_requests += 1
            num_chars += data[i]['num_chars']
            sum_ttft += data[i]['ttft']
            sum_time_to_finish += data[i]['finish_time'] - data[i]['request_time']
            sum_chars_per_second += data[i]['num_chars'] / (data[i]['finish_time'] - data[i]['request_time'] - data[i]['ttft'])
            i += 1

        new_data['time'].append(s)
        new_data['rps'].append(num_requests/dt)
        new_data['cps'].append(num_chars/dt)
        new_data['ttft'].append(sum_ttft/num_requests if num_requests != 0 else None)
        new_data['time_to_finish'].append(sum_time_to_finish/num_requests if num_requests != 0 else None)
        new_data['cpspr'].append(sum_chars_per_second/num_requests if num_requests != 0 else None)

    return new_data



def get_ttft_dots(clean_data):
    times = []
    ttfts = []
    for time, pre_ttft, ttft, post_ttft in zip(clean_data['time'], clean_data['ttft'][0:], clean_data['ttft'][1:], clean_data['ttft'][2:]):
        if (not pre_ttft) and ttft and not post_ttft:
            times.append(time)
            ttfts.append(ttft)
    return times, ttfts

def get_cpspr_dots(clean_data):
    # Variable names should all be cpspr and not ttft but I am lazy
    # or should be refactored to one common function
    times = []
    ttfts = []
    for time, pre_ttft, ttft, post_ttft in zip(clean_data['time'], clean_data['cpspr'][0:], clean_data['cpspr'][1:], clean_data['cpspr'][2:]):
        if (not pre_ttft) and ttft and not post_ttft:
            times.append(time + 5)
            ttfts.append(ttft) 
    return times, ttfts

def convolve_median(arr, n=3):
    new_arr = np.ndarray(shape=len(arr))
    for i in range(len(arr)):

        start = max(i-n//2, 0)
        end = min(start + n, len(arr))
        new_arr[i] = np.median(arr[start:end])

    return new_arr




if __name__ == "__main__":
    main()