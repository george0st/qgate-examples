# Run from terminal
###########################

# Run without terminal
###########################
nohup python3.11 perf_cql/perf_cql.py run -e _fin_nonprod_ts01_init.env -d perf_cql
nohup python3.11 perf_cql/perf_cql.py run -e _fin_nonprod_ts01_write.env -d perf_cql
nohup python3.11 perf_cql/perf_cql.py run -e _fin_nonprod_ts01_read.env -d perf_cql
