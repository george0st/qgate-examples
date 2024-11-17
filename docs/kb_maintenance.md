# Knowledge base for maintenance

## Maintenance tasks

### 1. Environment cleanup

#### 1.1 Total cleanup

 - ./nodetool compact
 - ./nodetool cleanup
 - ./nodetool garbagecollect

#### 1.2 Compaction

The compact data for better efficiency (and remove tombstone). The usage: 
 - nodetool compact `<keyspace>` `<table>`
 - nodetool compact
 - nodetool compact prftest
 - nodetool compact prftest t01

NOTE: 
 - The tombstones are generated in case of delete data (via DELETE FROM, in case of TTL usage, etc.)
 - The cql command `DROP TABLE` will not create tombstones 

#### 1.3 Cleanup

The cleanup of obsolete, not used data (valid data will be without touch/impact). The usage:
 - nodetool cleanup `<keyspace>` `<table>`
 - nodetool cleanup 
 - nodetool cleanup prftest 
 - nodetool cleanup prftest t01

#### 1.4 Garbagecollect

The remove unused data for better performance. The usage 
 - nodetool garbagecollect `<keyspace>` `<table>`
 - nodetool garbagecollect 
 - nodetool garbagecollect prftest 
 - nodetool garbagecollect prftest t01

### 2. Get state of environment

#### 2.1 Status

The information about cluster state, the usage:
 - nodetool status

#### 2.2 Compaction

The information about compaction, the usage:
 - nodetool compactionstats

#### 2.3 Tablestats

The information about tables, the usage:
 - nodetool tablestats `<keyspace>.<table>`
 - nodetool tablestats
 - nodetool tablestats prftest
 - nodetool tablestats prftest.t01
