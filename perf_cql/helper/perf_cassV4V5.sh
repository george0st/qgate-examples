#!/bin/sh

python3.11 perf_cql/perf_cql.py run -e _cassV4_init.env -d perf_cql
python3.11 perf_cql/perf_cql.py run -e _cassV4_write.env -d perf_cql
python3.11 perf_cql/perf_cql.py run -e _cassV4_read.env -d perf_cql
python3.11 perf_cql/perf_cql.py run -e _cassV4_readwrite.env -d perf_cql

python3.11 perf_cql/perf_cql.py run -e _cassV5_init.env -d perf_cql
python3.11 perf_cql/perf_cql.py run -e _cassV5_write.env -d perf_cql
python3.11 perf_cql/perf_cql.py run -e _cassV5_read.env -d perf_cql
python3.11 perf_cql/perf_cql.py run -e _cassV5_readwrite.env -d perf_cql
