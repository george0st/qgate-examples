# Knowledge base for performance tuning

## 1. Increase performance

### 1.1 Without HW increase

#### 1.1.1 Balance to all nodes
  - Please, comment the parameter '_LB_LOCAL_DC_', than RoundRobinPolicy will be
    used (instead of '_DCAwareRoundRobinPolicy_'), it means routing will be
    to the all nodes in cluster (not only nodes in local data center)
  - NOTE: 
    - It is valid recommendation in case, that all data centers have the same
      network availabilities

#### 1.1.2 Increase replication factor for keyspace
  - It will increase parallel/concurrent access to the data 
  - NOTE: 
    - The recommendation is to keep replication factor <= amount of nodes in
      cluster (e.g. 2x data center, each with 3 nodes, the recommendation is
      replication factor max 3 for each data center)
    - The increase of replication factor will consume more disk space

#### 1.1.3 Tune compaction strategy for table
   - The recommendation is to use '_UnifiedCompactionStrategy_' and tune relevant
     parameters based on preference for tuning of READ/WRITE operationS 
   - The detail setting has relation of density, timing of compaction, etc.
   - NOTE:
     - The setting will be visible in case, that node/cluster has enough data (it
       is not visible in case of small data amount) 
  
### 1.2 With HW increase

#### 1.2.1 Increase amount of nodes
  - NOTE:
    - if you use the parameter '_LB_LOCAL_DC_', the main is scaling for local 
      data center

