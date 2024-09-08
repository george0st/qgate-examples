# Description for ENV Configuration

## 1. Multi ENV setting

 - **DETAIL_OUTPUT**
   - The detail output can be '_On_' (as default) or '_Off_'. 
     The detail output is useful for execution graph.
 - **EXECUTOR_DURATION**
   - The test duration for run EACH PERFORMANCE TEST (value in seconds, 
     default is _5_)
 - **EXECUTOR_START_DELAY**
   - The synch time for run EACH PERFORMANCE TEST (value in seconds, 
     default is _0_). The value define time for waiting to all executors, 
     before real start of performance test execution. Use this setting, 
     when you need ASAP high performance of executors in the same time
     (it will generate perf peek). Use zero value, when you need slightly
     increase number of executors (it is without synchronization)
 - **MULTIPLE_ENV_DELAY**
   - The delay before switch to different config file (value in seconds,
     default is _0_)
 - **MULTIPLE_ENV**
   - The list of ENV files e.g. '_A.env, B.env, C.env, ..._'

## 2. Single ENV setting

 - **TEST_TYPE**
   - The type of operation can be '_R_' read, '_W_' write (as default) 
 - **BULK_LIST**
   - The size of data bulk in format '_[[rows, columns], ...]_' 
     (default is '_[[200, 10]]_')
   - NOTE: _[[200, 10]]_ means, that table will have 10 columns and will do
     - 200 insert/upsert operation during the test type Write
     - 200 select operation during the test type Read
 - **KEYSPACE**
   - The name of keyspace for test (default is '_jist_')
 - **CLUSTER_CHECK**
   - The run cluster check, can be '_On_' (as default) or '_Off_' 
 - **XXX** is the value based on system '_SCYLLADB_', 
   '_CASSANDRA_', '_ASTRADB_', '_COSMOSDB_'
   - **XXX_LABEL**
     - The label used in output file name (default is '_local_')
   - **XXX_IP**
     - The list of IP addresses separated by a comma, 
       e.g. '_10.129.53.159, 10.129.53.153, ..._' (default is '_localhost_')
   - **XXX_PORT**
     - The port name (default is _9042_)
   - **XXX_USERNAME**
      - The username for login (default is '_cassandra_')
   - **XXX_PASSWORD**
      - The path to the file with password for login 
        (default is password value '_cassandra_')
   - **XXX_REPLICATION_CLASS**
     - The replication class can be '_SimpleStrategy_' or 
       '_NetworkTopologyStrategy_' (as default)
     - NOTE: detailed description see [DataStax Replication](https://docs.datastax.com/en/cassandra-oss/3.x/cassandra/architecture/archDataDistributeReplication.html)
   - **XXX_REPLICATION_FACTOR**
     - The amount of replicas (default is _3_)
   - **XXX_CONSISTENCY_LEVEL**
     - The consistency level can be cross
       - Only local data center: '_LOCAL_ONE_', '_LOCAL_QUORUM_' (as default), '_LOCAL_SERIAL_' 
       - All data centers: '_EACH_QUORUM_', '_QUORUM_', '_SERIAL_', '_ALL_'
       - Some data center:  '_ONE_', '_TWO_', '_THREE_', '_ANY_'
     - NOTE: detailed description see [DataStax Consistency](https://docs.datastax.com/en/cassandra-oss/3.0/cassandra/dml/dmlConfigConsistency.html)
   - **XXX_LB_LOCAL_DC**
     - The name of local data center for correct balancing 
       (default is '_datacenter1_')
 
## NOTEs

 - The **network routing** will be used based on setting of 
   replication factor 
   - _RoundRobinPolicy_ (for REPLICATION_FACTOR = 1)
   - _DCAwareRoundRobinPolicy_ (for CASSANDRA_REPLICATION_FACTOR > 1) 
     with local data center based on value XXX_LB_LOCAL_DC