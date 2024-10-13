#!/bin/sh

# PERFORMANCE volatility, run _cass.env (1 minute execution time, focus on performance volatility)
#python3.11 perf_cql/perf_cql.py run -e _cass.env -d perf_cql
#python3.11 perf_cql/perf_cql.py run -e _cass2.env -d perf_cql

# PERFORMANCE peek, run _cass-peek.env (1 minute execution time, focus on performance peek)
python3.11 perf_cql/perf_cql.py run -e _cass-peek.env -d perf_cql
python3.11 perf_cql/perf_cql.py run -e _cass-peek2.env -d perf_cql
