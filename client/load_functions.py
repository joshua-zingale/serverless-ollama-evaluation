from inspect import signature, _empty
from math import sin, cos
from math import pi as PI
import numpy as np
import random

def coerce_arguments(f):
    def new_f(*args):
        new_args = []
        for arg, (_, t) in zip(args, signature(f).parameters.items()):
            try:
                if t.annotation != _empty:
                    new_args.append(t.annotation(arg))
                else:
                    new_args.append()
            except (TypeError, ValueError):
                raise ValueError((f"Cannot coerce {type(arg)} to {t.annotation}"))
        return f(*new_args)
    return new_f

    

@coerce_arguments
def constant(requests_per_second: float, max_time: float = 10):
    assert requests_per_second > 0, f"The requests per second must be greater than 0, but it is {requests_per_second}"
    def load(time):
        if time > max_time:
            return None
        return 1 / requests_per_second
    return load

@coerce_arguments
def sinusoidal(min_freq: float, max_freq: float, period: float, max_time: float = 10):
    def load(time):
        if time > max_time:
            return None
        
        factor =  2*PI / period
        t0 = time * factor - PI/2 /period

        # Since x + sin(x) = k has no analytic solution, we use Newton's method to approximate
        # the zero of x + sin(x) - k = 0
        f = lambda t: t*(max_freq + min_freq)/2 + (min_freq - max_freq)*sin(t) / 2
        fp = lambda t: (max_freq + min_freq)/2 + (min_freq - max_freq)*cos(t) / 2

        g = lambda t: f(t) - f(t0) - 1
        gp = fp

        t = random.random() * (factor/min_freq-factor/max_freq) + 1/max_freq + t0
        for _ in range(10):
            t = t - g(t)/max(gp(t), 1e-4)

        # print(f"D {fp(t0)}")
        #print(t)
        return (t - t0)
    
    return load

@coerce_arguments
def spikes(requests_per_second: float, time_between_spikes: float, spike_length: float, spike_rps: float, max_time: float = 10):
    def load(time):
        if time > max_time:
            return None
        
        period = time_between_spikes + spike_length
        # If spiking
        if time % period >= -spike_length % period:
            return 1/spike_rps
        
        time_till_next_spike = (-spike_length % period) - time % period
        
        return min(1/requests_per_second, time_till_next_spike)
    
    return load
        
@coerce_arguments
def normal(mean: float, std: float, reevaluation_interval: float, max_time: float = 10):
    def load(time):
        if time > max_time:
            return None
        
        random_seed = random.randint(0,1e6)
        np.random.seed(int(time // reevaluation_interval) + random_seed)
        rps = max(np.random.normal(mean, std), 1/reevaluation_interval)

        return 1/rps
    
    return load        

def get_load(name: str, *args):
    function_map = {
        "constant": constant,
        "sinusoidal": sinusoidal,
        "spikes": spikes,
        "normal": normal,
        }
    load = function_map[name](*args)
    return load


def main():
    # Testing code
    load = get_load("sinusoidal", 1, 10, 300, 9999)


    print(load(0))
    print(load(75))
    print(load(150))
    print(load(200))
    print(load(225))
    print(load(300))


    from matplotlib import pyplot as plt

    x = []
    y = []
    ys = []

    f = lambda x: 11/2 - cos(x * 2* PI / 300) * (10 - 1) / 2

    n = 8
    for t in range(n* 600):
        t /= n
        x.append(t)
        y.append(1/load(t))
        ys.append(f(t))

    yp = [(y1 - y0)*n * 300 / (2 * PI) for y1, y0 in zip(y[1:], y[:-1])]


    plt.plot(x, y)
    plt.plot(x, ys)
    plt.show()


    

if __name__ == "__main__":
    main()