# Description for ENV Configuration

## 1. Multi ENV setting

 - DETAIL_OUTPUT 
 - EXECUTOR_DURATION 
 - EXECUTOR_START_DELAY 
 - MULTIPLE_ENV_DELAY 
 - MULTIPLE_ENV

## 2. Single ENV setting

 - **TEST_TYPE**
   - Type of operation, can be 'R' read, 'W' write (as default) 
 - **BULK_LIST**
   - Definition the data bulk size in format [[rows, columns], ...] (default "[[200, 10]]")
 - **KEYSPACE**
   - Name of keyspace for test (default is 'jist')
 - **CLUSTER_CHECK**
   - Run cluster check, can be 'On' (as default) or 'Off' 
 - **REPLICATION_CLASS**
   - can be 'SimpleStrategy' or 'NetworkTopologyStrategy' (as default)
 - **CONSISTENCY_LEVEL**
   - can be 'ANY', 'ONE', 'TWO', 'THREE', 'QUORUM', 'ALL'
      'LOCAL_QUORUM', 'EACH_QUORUM', 'SERIAL', 'LOCAL_SERIAL', 'LOCAL_ONE'
