# Description for ENV Configuration

## 1. Multi ENV setting

The configuration define global setting and relation to the many 
single ENV settings (single ENV setting will rewrite global setting).

 - **DETAIL_OUTPUT** (opt)
   - The detail output can be '_On_' (as default) or '_Off_'. 
     The detail output is useful for execution graph.
 - **EXECUTOR_DURATION** (opt)
   - The test duration for run EACH PERFORMANCE TEST (value in seconds, 
     default is _5_)
 - **EXECUTOR_START_DELAY** (opt)
   - The synch time for run EACH PERFORMANCE TEST (value in seconds, 
     default is _0_). The value define time for waiting to all executors, 
     before real start of performance test execution. Use this setting, 
     when you need ASAP high performance of executors in the same time
     (it will generate perf peek). Use zero value, when you need slightly
     increase number of executors (it is without synchronization)
 - **CLUSTER_DIAGNOSE** (opt)
   - The run cluster diagnose, can be '_Off_', '_Short_' (as default),
     '_Full_' or '_Extra_' 
 - **KEYSPACE** (opt)
   - The name of keyspace for test (default is '_prftest_') 
 - **BULK_LIST** (opt)
   - The size of data bulk in format '_[[rows, columns], ...]_' 
     (default is '_[[200, 10]]_')
   - NOTE: _[[200, 10]]_ means, that table will have 10 columns and will do
     - 200 insert/upsert operation during the test type Write
     - 200 select operation during the test type Read
 - **MULTIPLE_ENV_DELAY** (opt)
   - The delay before switch to different config file (value in seconds,
     default is _0_)
 - **MULTIPLE_ENV**
   - The list of single ENV files e.g. '_A.env, B.env, C.env, ..._'
   - Expected content, see next chapter '_2. Single ENV setting_'

## 2. Single ENV setting

The configuration for connection to the specific CQL solution such as
ScyllaDB, Cassandra, AstraDB, CosmosDB.

 - **TEST_TYPE** (opt)
   - The type of operation can be '_R_' read, '_W_' write (as default) 
 - **BULK_LIST** (opt, inherit)
   - The size of data bulk in format '_[[rows, columns], ...]_' 
     (default is '_[[200, 10]]_')
   - NOTE: _[[200, 10]]_ means, that table will have 10 columns and will do
     - 200 insert/upsert operation during the test type Write
     - 200 select operation during the test type Read
 - **KEYSPACE** (opt, inherit)
   - The name of keyspace for test (default is '_prftest_')
 - **EXECUTOR_DURATION** (opt, inherit)
   - The test duration for run EACH PERFORMANCE TEST (value in seconds, 
     default is _5_)
 - **XXX** is the value based on system '_SCYLLADB_', 
   '_CASSANDRA_', '_ASTRADB_', '_COSMOSDB_'
   - **XXX_LABEL** (opt)
     - The label used in output file name (default is '_local_')
   - **XXX_IP** (opt)
     - The list of IP addresses separated by a comma, 
       e.g. '_10.129.53.159, 10.129.53.153, ..._' (default is '_localhost_')
   - **XXX_PORT** (opt)
     - The port name (default is _9042_)
   - **XXX_USERNAME** (opt)
      - The username for login (default is '_cassandra_')
   - **XXX_PASSWORD** (opt)
      - The path to the file with password for login 
        (default is password value '_cassandra_')
   - **XXX_REPLICATION_CLASS** (opt)
     - The replication class can be '_SimpleStrategy_' or 
       '_NetworkTopologyStrategy_' (as default)
     - NOTE: 
       - detailed description see [DataStax Replication](https://docs.datastax.com/en/cassandra-oss/3.x/cassandra/architecture/archDataDistributeReplication.html)
       - relevant setting for Write TEST_TYPE
   - **XXX_REPLICATION_FACTOR** (opt)
     - The amount of replicas (default is _3_)
     - NOTE:
       - relevant setting for Write TEST_TYPE
       - replication factor is applied for each data center under the cluster
         (e.g. if replication factor is 3 in 2 data centers, it means, that we
         have totally 6 copies of data in cluster)
   - **XXX_CONSISTENCY_LEVEL** (opt)
     - The consistency level can be cross
       - Only local data center: '_LOCAL_ONE_', '_LOCAL_QUORUM_' (as default), '_LOCAL_SERIAL_' 
       - All data centers: '_EACH_QUORUM_', '_QUORUM_', '_SERIAL_', '_ALL_'
       - Some data center:  '_ONE_', '_TWO_', '_THREE_', '_ANY_'
     - NOTE: detailed description see [DataStax Consistency](https://docs.datastax.com/en/cassandra-oss/3.0/cassandra/dml/dmlConfigConsistency.html)
   - **XXX_LB_LOCAL_DC** (opt)
     - The name of local data center for correct balancing 
       (default is '_datacenter1_')
   - **XXX_COMPACTION** (opt)
     - The type of compaction (without default as optional), expected values
       '_UnifiedCompactionStrategy_', '_SizeTieredCompactionStrategy_',
       '_LeveledCompactionStrategy_', '_TimeWindowCompactionStrategy_'
     - NOTE: 
       - detailed description see [Apache Compaction](https://cassandra.apache.org/doc/5.0/cassandra/managing/operating/compaction/index.html),
         [DataStax Compaction](https://docs.datastax.com/en/cassandra-oss/3.0/cassandra/operations/opsConfigureCompaction.html)
       - relevant setting for Write TEST_TYPE
   - **XXX_COMPACTION_PARAMS** (opt)
     - The parameters for the compaction (without default as optional), value must be 
       in **quotation marks** e.g _"'max_threshold': 32, 'min_threshold': 4"_ for
       COMPACTION '_SizeTieredCompactionStrategy_' 
     - NOTE: 
       - detailed description see params
         [UCS](https://cassandra.apache.org/doc/5.0/cassandra/managing/operating/compaction/ucs.html#ucs_options), 
         [STCS](https://cassandra.apache.org/doc/5.0/cassandra/managing/operating/compaction/stcs.html#stcs_options),
         [LCS](https://cassandra.apache.org/doc/5.0/cassandra/managing/operating/compaction/lcs.html#lcs_options),
         [TWCS](https://cassandra.apache.org/doc/5.0/cassandra/managing/operating/compaction/twcs.html#twcs_options)
       - relevant setting for Write TEST_TYPE

 
## NOTEs

 - The **network routing** will be used based on setting of 
   replication factor 
   - _RoundRobinPolicy_ (for REPLICATION_FACTOR = 1)
   - _DCAwareRoundRobinPolicy_ (for CASSANDRA_REPLICATION_FACTOR > 1) 
     with local data center based on value XXX_LB_LOCAL_DC