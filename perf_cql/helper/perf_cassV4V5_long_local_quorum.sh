#!/bin/sh

echo "LONG LOCAL QUORUM"
# test Cassandra V4
python3.11 perf_cql/perf_cql.py run -e _cassV4_init.env -d perf_cql -fp "CONSISTENCY_LEVEL = LOCAL_ONE;NUMERIC_SCOPE = 5000;"
python3.11 perf_cql/perf_cql.py run -e _cassV4_write_long.env -d perf_cql -fp "CONSISTENCY_LEVEL = LOCAL_ONE;NUMERIC_SCOPE = 5000;"
python3.11 perf_cql/perf_cql.py run -e _cassV4_write.env -d perf_cql -fp "CONSISTENCY_LEVEL = LOCAL_QUORUM;NUMERIC_SCOPE = 5000;"
python3.11 perf_cql/perf_cql.py run -e _cassV4_read.env -d perf_cql -fp "CONSISTENCY_LEVEL = LOCAL_QUORUM;NUMERIC_SCOPE = 5000;"
python3.11 perf_cql/perf_cql.py run -e _cassV4_readwrite.env -d perf_cql -fp "CONSISTENCY_LEVEL = LOCAL_QUORUM;NUMERIC_SCOPE = 5000;"

# test Cassandra V5
python3.11 perf_cql/perf_cql.py run -e _cassV5_init.env -d perf_cql -fp "CONSISTENCY_LEVEL = LOCAL_ONE;NUMERIC_SCOPE = 5000;"
python3.11 perf_cql/perf_cql.py run -e _cassV5_write_long.env -d perf_cql -fp "CONSISTENCY_LEVEL = LOCAL_ONE;NUMERIC_SCOPE = 5000;"
python3.11 perf_cql/perf_cql.py run -e _cassV5_write.env -d perf_cql -fp "CONSISTENCY_LEVEL = LOCAL_QUORUM;NUMERIC_SCOPE = 5000;"
python3.11 perf_cql/perf_cql.py run -e _cassV5_read.env -d perf_cql -fp "CONSISTENCY_LEVEL = LOCAL_QUORUM;NUMERIC_SCOPE = 5000;"
python3.11 perf_cql/perf_cql.py run -e _cassV5_readwrite.env -d perf_cql -fp "CONSISTENCY_LEVEL = LOCAL_QUORUM;NUMERIC_SCOPE = 5000;"
