# Description for ENV Configuration

## Multi ENV setting
TBD.

## Single ENV setting
TBD.

## Output description
 - **PRF...min...** it means:
   - CASSANDRA_REPLICATION_CLASS = **SimpleStrategy** 
   - CASSANDRA_REPLICATION_FACTOR = **1** 
   - CASSANDRA_CONSISTENCY_LEVEL = **ONE**

 - **PRF...opt...**
   - CASSANDRA_REPLICATION_CLASS = **NetworkTopologyStrategy** 
   - CASSANDRA_REPLICATION_FACTOR = **3** 
   - CASSANDRA_CONSISTENCY_LEVEL = **EACH_QUORUM**

 - **PRF...max..**
   - CASSANDRA_REPLICATION_CLASS = **NetworkTopologyStrategy** 
   - CASSANDRA_REPLICATION_FACTOR = **3** 
   - CASSANDRA_CONSISTENCY_LEVEL = **ALL**