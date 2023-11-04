# qgate-examples

The project about usage of QGate suite.

## Performance tests
- [Cassandra & ScyllaDB & AstraDB](./perf/perf_nosql_cql.py)
  - Performance tests for Cassandra, ScyllaDB and AstraDB via CQL (Cassandra Query Language)
  - Expected future extension will be about add Azure Cosmos DB
  - Note: You need to tailor configuration values for your environment
    - **'ip'** and **'port'** (optional are **'username'** and **'password'**) for Cassandra and ScyllaBD
    - **'secure_connect_bundle'**, **'username'**, **'password'** for AstraDB
