 # TODO list
 
1. Add executors to multi ENV
4. Add CQL version (SELECT release_version FROM system.local;)
5. Move diagnostic out of perf procedure
6. Add to diagnostic, calculation of size
   
   SELECT keyspace_name, 
          SUM(mean_partition_size * partitions_count) / 1048576 AS total_size_mb 
   FROM system.size_estimates 
   WHERE keyspace_name = 'jist' 
   GROUP BY keyspace_name;

