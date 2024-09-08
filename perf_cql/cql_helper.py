import time
import numpy as np
import string


def get_rng_generator(complex_init = True) -> np.random._generator.Generator:
    """Create generator of random values with initiation"""

    # now and now_ms (as detail about miliseconds)
    now = time.time()
    now_ms = (now - int(now)) * 1000000000

    # calc based on CPU speed
    ns_start = time.perf_counter_ns()
    if complex_init:
        time.sleep(0.01)
        ns_stop = time.perf_counter_ns()

        # create generator with more random seed (now, now_ms, cpu speed)
        return np.random.default_rng([int(now), int(now_ms), ns_stop - ns_start, ns_stop])
    else:
        return np.random.default_rng([int(now), int(now_ms), ns_start])


def generate_id(id_size = 4):
    """Generate random text sequence"""
    generator = get_rng_generator(False)

    sequence = list(string.ascii_lowercase + string.digits)
    return ''.join(generator.choice(sequence) for _ in range(id_size))

def str2bool(value) -> bool:
    """Conversion of text value ("True", "1", "Yes", "On") to Bool value"""
    return value.lower() in ['true', '1', 'yes', 'on']

def read_file(file) -> str:
    with open(file) as f:
        return f.readline()