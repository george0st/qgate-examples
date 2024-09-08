# Description for ENV Configuration

## 1. Multi ENV setting

 - **DETAIL_OUTPUT**
   - The detail output can be 'On' (as default) or 'Off'. The detail output is
     useful for execution graph.
 - **EXECUTOR_DURATION**
   - The test duration for run EACH PERFORMANCE TEST (value in seconds, default is 5)
 - **EXECUTOR_START_DELAY**
   - The synch time for run EACH PERFORMANCE TEST (value in seconds, default is 0). The value
     define time for waiting to all executors, before real start of performance test execution. 
     Use this setting, when you need ASAP high performance of executors in the same time 
     (it will generate perf peek). Use zero value, when you need slightly increase number of
     executors (it is without synchronization)
 - **MULTIPLE_ENV_DELAY**
   - The delay before switch to different config file (value in seconds, default is 0)
 - **MULTIPLE_ENV**
   - The list of ENV files e.g. "A.env, B.env, C.env, ..."

## 2. Single ENV setting

 - **TEST_TYPE**
   - The type of operation can be 'R' read, 'W' write (as default) 
 - **BULK_LIST**
   - The size of data bulk in format [[rows, columns], ...] (default is "[[200, 10]]")
 - **KEYSPACE**
   - The name of keyspace for test (default is 'jist')
 - **CLUSTER_CHECK**
   - The run cluster check, can be 'On' (as default) or 'Off' 
 - **XXX** is the value based on system 'SCYLLADB', 'CASSANDRA', 'ASTRADB', 'COSMOSDB'
   - **XXX_LABEL**
     - The label used in output file name (default is 'local')
   - **XXX_IP**
     - The list of IP addresses separated by a comma, e.g. '10.129.53.159, 10.129.53.153' 
       (default is 'localhost')
   - **XXX_PORT**
     - The port name (default is 9042)
   - **XXX_USERNAME**
      - The username for login (default is 'cassandra')
   - **XXX_PASSWORD**
      - The path to the file with password for login (default is password 'cassandra')
   - **XXX_REPLICATION_CLASS**
     - The replication class can be 'SimpleStrategy' or 
       'NetworkTopologyStrategy' (as default)
     - NOTE: detailed description see [DataStax](https://docs.datastax.com/en/cassandra-oss/3.x/cassandra/architecture/archDataDistributeReplication.html)
   - **XXX_REPLICATION_FACTOR**
     - The amount of replicas (default is 3)
   - **XXX_CONSISTENCY_LEVEL**
     - The consistency level can be cross
       - Only local data center: 'LOCAL_ONE', 'LOCAL_QUORUM' (as default), 'LOCAL_SERIAL' 
       - All data centers: 'EACH_QUORUM', 'QUORUM', 'SERIAL', 'ALL'
       - Some data center:  'ONE', 'TWO', 'THREE', 'ANY'
     - NOTE: detailed description see [DataStax](https://docs.datastax.com/en/cassandra-oss/3.0/cassandra/dml/dmlConfigConsistency.html)
   - **XXX_LB_LOCAL_DC**
     - The name of local data center for correct balancing (default is 'datacenter1'')


## NOTEs
 - The **network routing** will be used based on setting of replication factor 
   - RoundRobinPolicy (for REPLICATION_FACTOR = 1)
   - DCAwareRoundRobinPolicy (for CASSANDRA_REPLICATION_FACTOR > 1)