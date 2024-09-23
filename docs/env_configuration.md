# Description for ENV Configuration

## 1. Multi ENV setting

The configuration define global setting and relation to the many 
single ENV settings (single ENV setting can rewrite global setting).

### 1.1 The main parameters for test execution

 - **EXECUTOR_DURATION** (opt)
   - The test duration for run EACH PERFORMANCE TEST (value in seconds, 
     default is _5_)
 - **BULK_LIST_R** (opt) and
 - **BULK_LIST_W** (opt)
   - The size of data bulk/bundle for READ and WRITE in format
     '_[[rows, columns], ...]_' (default for READ '_[[200, 10]]_',
     for WRITE '_[[1,10]]_')
   - NOTE: _[[200, 10]]_ means, that table will have 10 columns and will do
     - 200 insert/upsert operation during the test type Write
     - 200 select operation during the test type Read 
       (it is better to use bulk e.g. [1, 10] for read operations)
 - **EXECUTORS** (opt)
   - The set of executors in format '_[[processes, threads, label], ...]_' 
     (default is '_"[[1, 1, '1x threads'], [2, 1, '1x threads']]"_')
   - NOTE:
     - The amount of executors is based on formula '_processes * threads_'
     - The same '_label_' define items visualization as one line in chart 
 - **MULTIPLE_ENV**
   - The list of ENV files e.g. '_A.env, B.env, C.env, ..._' for processing
   - Expected content, see next chapter '_2. Single ENV setting_'

### 1.2 Global setting about connection 

It is possible to specify these settings as global (and it will
be applied to each single ENV file):

   - **IP** (opt)
     - The list of IP addresses separated by a comma, 
       e.g. '_10.129.53.159, 10.129.53.153, ..._' (default is '_localhost_')
   - **PORT** (opt)
     - The port name (default is _9042_)
   - **USERNAME** (opt)
      - The username for login (default is '_cassandra_')
   - **PASSWORD** (opt)
      - The path to the file with password for login 
        (default is password value '_cassandra_')

### 1.3 The other parameters with smaller importance

 - **DETAIL_OUTPUT** (opt)
   - The detail output can be '_On_' (as default) or '_Off_'. 
     The detail output is useful for visualization of execution graph 
     (but it is without usage for performance graph)
 - **GENERATE_GRAPH** (opt)
   - The setting for graph generator can be '_Off_', '_Perf_' (as default),
     '_Exe_' or '_All_'
   - Note:
     - '_Off_' it is without generation of graphs
     - '_Perf_' generates graph about performances (operations/second and response times) 
     - '_Exe_' generates graph about change of executors in time (it is useful 
       visualization for tuning of value for parameter '_EXECUTOR_START_DELAY_')
     - '_All_' generates performance and executor graphs
 - **EXECUTOR_START_DELAY** (opt)
   - The synch time for run EACH PERFORMANCE TEST (value in seconds, 
     default is _0_). 
   - The value define time for waiting to all executors, before real start
     of performance test execution. Use this setting, 
     when you need ASAP high performance of executors in the same time
     (it will generate performance peek).
   - Use zero value (default), when you need slightly increase number of
     executors (it is without synchronization)
 - **CLUSTER_DIAGNOSE** (opt)
   - The run cluster diagnose, can be '_Off_', '_Short_' (as default),
     '_Full_' or '_Extra_'
   - It is only diagnostic information about the cluster, before 
     processing each ENV file
 - **KEYSPACE** (opt)
   - The name of keyspace for tests (default is '_prftest_') 
 - **MULTIPLE_ENV_DELAY** (opt)
   - The delay before switch to different config file (value in seconds,
     default is _0_)

### 1.1 Examples

The example with full setting:
```
EXECUTOR_DURATION = 5
BULK_LIST_W = [[200, 10]]
BULK_LIST_R = [[1, 10]]
EXECUTORS = "[[8, 1, '1x threads'], [16, 1, '1x threads'], [32, 1, '1x threads'],
              [8, 2, '2x threads'], [16, 2, '2x threads'], [32, 2, '2x threads'],
              [8, 3, '3x threads'], [16, 3, '3x threads'], [32, 3, '3x threads']]"

DETAIL_OUTPUT = True
GENERATE_GRAPH = all
EXECUTOR_START_DELAY = 0
CLUSTER_DIAGNOSE = extra
KEYSPACE = perftest

MULTIPLE_ENV = cass-W1-low, cass-R1-low
```

The minimalistic example (other values use default values):

```
MULTIPLE_ENV = cass-W1-low, cass-R1-low
```

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
   - NOTE:
     - if the value is not defined, the value will be used from multi ENV
       (as global setting), from setting '_BULK_LIST_R_' for
       '_TEST_TYPE = R_' or '_BULK_LIST_W_' for '_TEST_TYPE = W_' 
 - **KEYSPACE** (opt, inherit)
   - The name of keyspace for test (default is '_prftest_')
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
     - The consistency level for application (valid for Read/Write operations) can be:
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
       in **quotation marks** 
     - Sample:
       - The parameters for COMPACTION '_SizeTieredCompactionStrategy_'
         - _"'max_threshold': 32, 'min_threshold': 4"_ for
           COMPACTION '_SizeTieredCompactionStrategy_'
       - The parameters for COMPACTION '_UnifiedCompactionStrategy_'
         - _"'scaling_parameters': 'L4, L10'"_ or _"'scaling_parameters': 'T8, T4, N, L4'"_
     - NOTE: 
       - detailed description see params
         [UCS](https://cassandra.apache.org/doc/5.0/cassandra/managing/operating/compaction/ucs.html#ucs_options), 
         [STCS](https://cassandra.apache.org/doc/5.0/cassandra/managing/operating/compaction/stcs.html#stcs_options),
         [LCS](https://cassandra.apache.org/doc/5.0/cassandra/managing/operating/compaction/lcs.html#lcs_options),
         [TWCS](https://cassandra.apache.org/doc/5.0/cassandra/managing/operating/compaction/twcs.html#twcs_options)
       - relevant setting for Write TEST_TYPE

### 2.1 Examples

The example with two providers, Cassandra (is On) and ScyllaDB (is On):
```
TEST_TYPE = W
BULK_LIST = [[100, 20]]

# Cassandra
CASSANDRA = On
CASSANDRA_LABEL = local-1-low
CASSANDRA_IP = localhost
CASSANDRA_PORT = 9042
CASSANDRA_USERNAME = cassandra
CASSANDRA_PASSWORD = ../secrets/cassandra.txt
CASSANDRA_REPLICATION_CLASS = SimpleStrategy
CASSANDRA_REPLICATION_FACTOR = 1
CASSANDRA_CONSISTENCY_LEVEL = ONE
CASSANDRA_LB_LOCAL_DC = datacenter1
CASSANDRA_COMPACTION = UnifiedCompactionStrategy
#CASSANDRA_COMPACTION = SizeTieredCompactionStrategy
#CASSANDRA_COMPACTION_PARAMS = "'max_threshold': 32, 'min_threshold': 4"

# ScyllaDB
SCYLLADB = On
SCYLLADB_IP = 10.124.0.18
SCYLLADB_PORT= 9042
SCYLLADB_REPLICATION_CLASS = SimpleStrategy
SCYLLADB_REPLICATION_FACTOR = 1
SCYLLADB_CONSISTENCY_LEVEL = ONE
```
The shorter example with one provider:

```
TEST_TYPE = W

# Cassandra
CASSANDRA = On
CASSANDRA_LABEL = local-1-low
CASSANDRA_IP = localhost
CASSANDRA_REPLICATION_CLASS = SimpleStrategy
CASSANDRA_REPLICATION_FACTOR = 1
CASSANDRA_CONSISTENCY_LEVEL = ONE
```

## NOTEs

 - The **network routing** will be used based on setting of 
   replication factor 
   - _RoundRobinPolicy_ (for REPLICATION_FACTOR = 1)
   - _DCAwareRoundRobinPolicy_ (for CASSANDRA_REPLICATION_FACTOR > 1) 
     with local data center based on value XXX_LB_LOCAL_DC