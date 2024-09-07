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
   - The list of ENV files e.g. "A.env, b.env, C.env, ..."

## 2. Single ENV setting

 - **TEST_TYPE**
   - The type of operation can be 'R' read, 'W' write (as default) 
 - **BULK_LIST**
   - The size of data bulk in format [[rows, columns], ...] (default is "[[200, 10]]")
 - **KEYSPACE**
   - The name of keyspace for test (default is 'jist')
 - **CLUSTER_CHECK**
   - The run cluster check, can be 'On' (as default) or 'Off' 
 - **REPLICATION_CLASS**
   - The replication class can be 'SimpleStrategy' or 'NetworkTopologyStrategy'
     (as default)
 - **CONSISTENCY_LEVEL**
   - The consistency level can be 
     - 'ANY', 'ONE', 'TWO', 'THREE', 'QUORUM', 'ALL', 
     'LOCAL_QUORUM', 'EACH_QUORUM', 'SERIAL', 'LOCAL_SERIAL', 'LOCAL_ONE'
