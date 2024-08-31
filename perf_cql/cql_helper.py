import time
import numpy as np

def get_rng_generator() -> np.random._generator.Generator:
    """Create generator of random values with initiation"""

    # now and now_ms (as detail about miliseconds)
    now = time.time()
    now_ms = (now - int(now)) * 1000000000

    # calc based on CPU speed
    ns_start = time.perf_counter_ns()
    time.sleep(0.01)
    ns_stop = time.perf_counter_ns()

    # create generator with more random seed (now, now_ms, cpu speed)
    return np.random.default_rng([int(now), int(now_ms), ns_stop - ns_start, ns_stop])