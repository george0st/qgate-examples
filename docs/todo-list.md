 # TODO list
 

1. Add CLI for check size of all or specific keyspaces

2. Identify Cassandra, Scylla, AstraDB based on CQL
   - it will be little tricky based on system tables
   - see stackoverflow discussion
   
3. Add rebuild keyspace
  
    KEYSPACE_REBUILD = True
    KEYSPACE_COMPACTION = UnifiedCompactionStrategy
    KEYSPACE_COMPACTION_PARAMS = "'scaling_parameters': 'L4, L10'"



