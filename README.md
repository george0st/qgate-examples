# qgate-examples

The project about usage of QGate suite.

## Performance tests 
- [Cassandra & ScyllaDB & AstraDB & CosmosDB](perf_cql/perf_nosql_cql.py)
  - Performance tests for Cassandra, ScyllaDB, AstraDB and CosmosDB via CQL (Cassandra Query Language)
  - Full configuration in **perf_nosql_cql.env**
  - Note: You need to tailor configuration values for your environment, typically
    - **'ip'** and **'port'** (optional are **'username'** and **'password'**) for Cassandra and ScyllaBD
    - **'secure_connect_bundle'**, **'username'**, **'password'** for AstraDB
