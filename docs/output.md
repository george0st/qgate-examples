# Output description
 

## 1. Performance graphs

The sample outputs:
   - Performance graphs
     ![Read](outputs/PRF-Cassandra-092409-R1-min-2024-09-04_07-36-33-bulk-1x10.png)
     ![Write](outputs/PRF-Cassandra-092409-W1-min-2024-09-04_07-24-28-bulk-200x10.png)
     ![Read](outputs/PRF-Cassandra-223759-R1-low-2024-09-21_20-50-00-bulk-1x10.png)
   - ![Write](outputs/PRF-Cassandra-223759-W1-low-2024-09-21_20-38-07-bulk-200x10.png)
  - Executors graphs
    ![W1](outputs/EXE-Cassandra-154324-W1-low-2024-09-16_13-43-41-bulk-200x10-plan-32x3.png)
    ![R1](outputs/EXE-Cassandra-154324-R1-low-2024-09-16_13-54-33-bulk-1x10-plan-8x3.png)

### 1.1 Relation of ENV file vs name of graphs (in PNG format)

 - **PRF-\*1-low-\*.png**
   - CASSANDRA_LABEL = 1-low
   - CASSANDRA_REPLICATION_CLASS = **NetworkTopologyStrategy** 
   - CASSANDRA_REPLICATION_FACTOR = **2** 
   - CASSANDRA_CONSISTENCY_LEVEL = **LOCAL_ONE**

 - **PRF-\*2-med-\*.png**
   - CASSANDRA_LABEL = 2-med
   - CASSANDRA_REPLICATION_CLASS = **NetworkTopologyStrategy** 
   - CASSANDRA_REPLICATION_FACTOR = **3** 
   - CASSANDRA_CONSISTENCY_LEVEL = **EACH_QUORUM**

 - **PRF-\*3-hgh-\*.png**
   - CASSANDRA_LABEL = 3-hgh
   - CASSANDRA_REPLICATION_CLASS = **NetworkTopologyStrategy** 
   - CASSANDRA_REPLICATION_FACTOR = **3** 
   - CASSANDRA_CONSISTENCY_LEVEL = **ALL**