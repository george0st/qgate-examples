# Run from terminal
###########################

# Run without terminal
###########################
nohup python3.11 perf_cql/perf_cql.py run -e _fin_nonprod.env -d perf_cql
nohup python3.11 perf_cql/perf_cql.py run -e _fin_nonprod_peek.env -d perf_cql
nohup python3.11 perf_cql/perf_cql.py run -e _fin_nonprod_long.env -d perf_cql
