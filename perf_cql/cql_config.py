from cassandra import ConsistencyLevel
from enum import Enum


class CQLType(Enum):
    ScyllaDB = 1
    Cassandra = 2
    AstraDB = 3
    CosmosDB = 4

class ConsistencyHelper:
    name_to_value = {
    'ANY': ConsistencyLevel.ANY,
    'ONE': ConsistencyLevel.ONE,
    'TWO': ConsistencyLevel.TWO,
    'THREE': ConsistencyLevel.THREE,
    'QUORUM': ConsistencyLevel.QUORUM,
    'ALL': ConsistencyLevel.ALL,
    'LOCAL_QUORUM': ConsistencyLevel.LOCAL_QUORUM,
    'LOCAL_ONE': ConsistencyLevel.LOCAL_ONE,
    'LOCAL_SERIAL': ConsistencyLevel.LOCAL_SERIAL,
    'EACH_QUORUM': ConsistencyLevel.EACH_QUORUM,
    'SERIAL': ConsistencyLevel.SERIAL,
    }

class CQLConfig:

    def __init__(self, config, adapter):
        self._config = config
        self._adapter = adapter

    def get_params(self):
        param={}

        # shared params for all providers
        param['keyspace'] = self._config.get("KEYSPACE", "tst")
        param['test_type'] = self._config.get("TEST_TYPE", "W")

        if self._config.get(self._adapter,"off").lower() == "on":
            # connection setting
            if self._config.get(f"{self._adapter}_IP", None):
                param["ip"] = self._config[f"{self._adapter}_IP"].split(",")
            if self._config.get(f"{self._adapter}_PORT", None):
                param["port"] = self._config[f"{self._adapter}_PORT"]
            if self._config.get(f"{self._adapter}_SECURE_CONNECT_BUNDLE", None):
                param["secure_connect_bundle"] = self._config[f"{self._adapter}_SECURE_CONNECT_BUNDLE"]

            # login setting
            if self._config.get(f"{self._adapter}_USERNAME", None) or self._config.get(f"{self._adapter}_PASSWORD", None):
                param['username'] = self._config.get(f"{self._adapter}_USERNAME", None)
                param['password'] = self._config.get(f"{self._adapter}_PASSWORD", None)

            # replication setting
            if self._config.get(f"{self._adapter}_REPLICATION_CLASS", None) or self._config.get(f"{self._adapter}_REPLICATION_FACTOR", None):
                param['replication_class'] = self._config.get(f"{self._adapter}_REPLICATION_CLASS", None)
                param['replication_factor'] = self._config.get(f"{self._adapter}_REPLICATION_FACTOR", None)

            # consistency level (default is "LOCAL_QUORUM")
            param['consistency_level'] = ConsistencyHelper.name_to_value[self._config.get(f"{self._adapter}_CONSISTENCY_LEVEL", "LOCAL_QUORUM")]

            # label
            param['label'] = self._config.get(f"{self._adapter}_LABEL", None)

            return param
        else:
            return None