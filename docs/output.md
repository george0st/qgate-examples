# Output description
 

 - **PRF...min/low...**
   - CASSANDRA_REPLICATION_CLASS = **SimpleStrategy** 
   - CASSANDRA_REPLICATION_FACTOR = **1** 
   - CASSANDRA_CONSISTENCY_LEVEL = **ONE**

 - **PRF...opt/med...**
   - CASSANDRA_REPLICATION_CLASS = **NetworkTopologyStrategy** 
   - CASSANDRA_REPLICATION_FACTOR = **3** 
   - CASSANDRA_CONSISTENCY_LEVEL = **EACH_QUORUM**

 - **PRF...max/hgh..**
   - CASSANDRA_REPLICATION_CLASS = **NetworkTopologyStrategy** 
   - CASSANDRA_REPLICATION_FACTOR = **3** 
   - CASSANDRA_CONSISTENCY_LEVEL = **ALL**