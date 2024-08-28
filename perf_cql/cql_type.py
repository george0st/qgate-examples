from enum import Enum


class CQLType(Enum):
    ScyllaDB = 1
    Cassandra = 2
    AstraDB = 3
    CosmosDB = 4