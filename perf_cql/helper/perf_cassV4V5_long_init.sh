#!/bin/sh

# Loaded data for test
#  - ~56 mil items in each table
####################################

# test Cassandra V4
python3.11 perf_cql/perf_cql.py run -e _cassV4_init.env -d perf_cql -fp "CONSISTENCY_LEVEL = LOCAL_ONE;NUMERIC_SCOPE = 7500;"
python3.11 perf_cql/perf_cql.py run -e _cassV4_write_long.env -d perf_cql -fp "CONSISTENCY_LEVEL = LOCAL_ONE;NUMERIC_SCOPE = 7500;"

# test Cassandra V5
python3.11 perf_cql/perf_cql.py run -e _cassV5_init.env -d perf_cql -fp "CONSISTENCY_LEVEL = LOCAL_ONE;NUMERIC_SCOPE = 7500;"
python3.11 perf_cql/perf_cql.py run -e _cassV5_write_long.env -d perf_cql -fp "CONSISTENCY_LEVEL = LOCAL_ONE;NUMERIC_SCOPE = 7500;"
