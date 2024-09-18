# qgate-examples

The project about usage of QGate suite.

## Performance tests 
- [Cassandra & ScyllaDB & AstraDB & CosmosDB](perf_cql/perf_cql.py)
  - The performance tests for Cassandra, ScyllaDB, AstraDB and CosmosDB via
    CQL (Cassandra Query Language)
  - The description of configuration, see [ENV configuration](/docs/env_configuration.md)
    - The samples of configurations
      - [Multi ENV configuration](perf_cql/config/cass.env)
      - [Single ENV configuration](perf_cql/config/cass-W1-low.env)
  - Expected outputs
    - Performance graphs
      - ![Read](docs/outputs/PRF-Cassandra-092409-R1-min-2024-09-04_07-36-33-bulk-1x10.png)
      - ![Write](docs/outputs/PRF-Cassandra-092409-W1-min-2024-09-04_07-24-28-bulk-200x10.png)
    - Executors graphs
      - ![W1]
