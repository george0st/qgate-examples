from cassandra import ConsistencyLevel
from enum import Enum
from cql_access import Setting
import cql_helper



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

    def __init__(self, config):
        self._config = config

    def get_global_params(self):
        global_param={}

        # shared params for all providers
        global_param['multiple_env'] = self._config.get('MULTIPLE_ENV', None)
        if global_param['multiple_env']:
            # multiple configurations
            global_param['multiple_env_delay'] = int(self._config.get('MULTIPLE_ENV_DELAY', 0))
            global_param['executor_duration'] = int(self._config.get('EXECUTOR_DURATION', 5))
            global_param['executor_start_delay'] = int(self._config.get('EXECUTOR_START_DELAY', 0))
            global_param['detail_output'] = cql_helper.str2bool(self._config.get('DETAIL_OUTPUT', "True"))
            return global_param
        else:
            return None

    def get_params(self, adapter):
        import ast
        param={}

        # shared params for all providers
        param['keyspace'] = self._config.get("KEYSPACE", Setting.KEYSPACE)
        param['bulk_list'] = ast.literal_eval(self._config.get("BULK_LIST", "[[200, 10]]"))
        param['test_type'] = self._config.get("TEST_TYPE", "W").lower()
        param['cluster_check'] = cql_helper.str2bool(self._config.get("CLUSTER_CHECK", "Off"))

        if cql_helper.str2bool(self._config.get(adapter,"Off")):
            # connection setting
            if self._config.get(f"{adapter}_IP", None):
                param["ip"] = self._config[f"{adapter}_IP"].split(",")
            if self._config.get(f"{adapter}_PORT", None):
                param["port"] = self._config[f"{adapter}_PORT"]
            if self._config.get(f"{adapter}_SECURE_CONNECT_BUNDLE", None):
                param["secure_connect_bundle"] = self._config[f"{adapter}_SECURE_CONNECT_BUNDLE"]

            # login setting
            if self._config.get(f"{adapter}_USERNAME", None) or self._config.get(f"{adapter}_PASSWORD", None):
                param['username'] = self._config.get(f"{adapter}_USERNAME", None)
                param['password'] = self._config.get(f"{adapter}_PASSWORD", None)

            # replication setting
            if self._config.get(f"{adapter}_REPLICATION_CLASS", None) or self._config.get(f"{adapter}_REPLICATION_FACTOR", None):
                param['replication_class'] = self._config.get(f"{adapter}_REPLICATION_CLASS", None)
                param['replication_factor'] = self._config.get(f"{adapter}_REPLICATION_FACTOR", None)

            # consistency level (default is "LOCAL_QUORUM")
            param['consistency_level'] = ConsistencyHelper.name_to_value[self._config.get(f"{adapter}_CONSISTENCY_LEVEL", "LOCAL_QUORUM").upper()]

            # local data center for correct setting of balancing via DCAwareRoundRobinPolicy
            param['local_dc'] = self._config.get(f"{adapter}_LB_LOCAL_DC", "datacenter1")

            # label
            param['label'] = self._config.get(f"{adapter}_LABEL", None)

            return param
        else:
            return None