#!/bin/sh
# useful command for cassandra clean

nodetool compact
nodetool cleanup
nodetool garbagecollect
