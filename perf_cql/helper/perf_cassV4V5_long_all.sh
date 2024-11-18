#!/bin/sh

# Loaded data for test
#  - ~90 mil items in each table
####################################

# test Cassandra V4
python3.11 perf_cql/perf_cql.py run -e _cassV4_write.env -d perf_cql -fp "CONSISTENCY_LEVEL = ALL;NUMERIC_SCOPE = 7500;"
python3.11 perf_cql/perf_cql.py run -e _cassV4_read.env -d perf_cql -fp "CONSISTENCY_LEVEL = ALL;NUMERIC_SCOPE = 7500;"
python3.11 perf_cql/perf_cql.py run -e _cassV4_readwrite.env -d perf_cql -fp "CONSISTENCY_LEVEL = ALL;NUMERIC_SCOPE = 7500;"

# test Cassandra V5
python3.11 perf_cql/perf_cql.py run -e _cassV5_write.env -d perf_cql -fp "CONSISTENCY_LEVEL = ALL;NUMERIC_SCOPE = 7500;"
python3.11 perf_cql/perf_cql.py run -e _cassV5_read.env -d perf_cql -fp "CONSISTENCY_LEVEL = ALL;NUMERIC_SCOPE = 7500;"
python3.11 perf_cql/perf_cql.py run -e _cassV5_readwrite.env -d perf_cql -fp "CONSISTENCY_LEVEL = ALL;NUMERIC_SCOPE = 7500;"
