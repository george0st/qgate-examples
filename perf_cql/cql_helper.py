import time
import numpy

def init_rng_generator():
    """Init generator of random values"""

    # now
    now = time.time()
    now_ms = (now - int(now)) * 1000000000

    # random value, based on CPU
    ns_start = time.perf_counter_ns()
    time.sleep(0.01)
    ns_stop = time.perf_counter_ns()

    return numpy.random.default_rng([int(now), int(now_ms), ns_stop - ns_start, ns_stop])