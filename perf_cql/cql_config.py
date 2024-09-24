from cassandra import ConsistencyLevel
from ast import literal_eval
from enum import Enum, Flag
from os import path
from colorama import Fore, Style
import cql_helper


class CQLAdapter(Flag):
    scylladb = 1
    cassandra = 2
    astradb = 4
    cosmosdb = 8

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

class CQLConfigSetting:

    # The key parameters
    ADAPTER = "Cassandra"
    EXECUTOR_DURATION = "5"
    BULK_LIST = "[[200, 10]]"
    BULK_LIST_W = "[[200, 10]]"
    BULK_LIST_R = "[[1, 10]]"
    EXECUTORS = "[[1, 1, '1x threads'], [2, 1, '1x threads']]"

    # The other tuning
    EXECUTOR_START_DELAY = "0"
    DETAIL_OUTPUT = "True"
    GENERATE_GRAPH = "Perf"
    CLUSTER_DIAGNOSE = "Short"
    MULTIPLE_ENV_DELAY = "0"

    KEYSPACE = "prftest"
    TEST_TYPE = "W"
    REPLICATION_CLASS = "NetworkTopologyStrategy"
    REPLICATION_FACTOR = "3"
    CONSISTENCY_LEVEL = "LOCAL_QUORUM"
    LB_LOCAL_DC = "datacenter1"
    USERNAME = "cassandra"
    PASSWORD = "cassandra"
    PORT = "9042"
    IP = "localhost"
    LABEL = "local"

class CQLConfig:

    def __init__(self, config = {}):
        self._config = config

    def _inherit_param_eval(self, param_name, global_param, global_param_name, param_name_default = None, adapter = None):
        """Get adapter from single or from global ENV"""
        if adapter:
            param_name=f"{adapter}_{param_name}"

        if self._config.get(param_name, None):
            return literal_eval(self._config[param_name])
        else:
            # inheritance of param from global_param
            if global_param:
                if global_param.get(global_param_name, None):
                    return global_param[global_param_name]
            return param_name_default


    def _inherit_param(self, param_name, global_param, global_param_name, param_name_default = None, adapter = None):
        """Get adapter from single or from global ENV"""

        if adapter:
            param_name=f"{adapter}_{param_name}"

        if self._config.get(param_name, None):
            return self._config[param_name]
        else:
            # inheritance of param from global_param
            if global_param:
                if global_param.get(global_param_name, None):
                    return global_param[global_param_name]
            return param_name_default

    def get_global_params(self, force_default = False, perf_dir = None):

        global_param={}

        # shared params for all providers
        global_param['multiple_env'] = self._config.get('MULTIPLE_ENV', None)
        if global_param['multiple_env'] or force_default:
            # multiple configurations

            global_param['adapter'] = self._config.get("ADAPTER", None)
            global_param['executors'] = literal_eval(self._config.get("EXECUTORS", CQLConfigSetting.EXECUTORS))
            global_param['detail_output'] = cql_helper.str2bool(self._config.get('DETAIL_OUTPUT', CQLConfigSetting.DETAIL_OUTPUT))
            global_param['generate_graph'] = self._config.get('GENERATE_GRAPH', CQLConfigSetting.GENERATE_GRAPH)
            global_param['executor_duration'] = int(self._config.get('EXECUTOR_DURATION', CQLConfigSetting.EXECUTOR_DURATION))
            global_param['executor_start_delay'] = int(self._config.get('EXECUTOR_START_DELAY', CQLConfigSetting.EXECUTOR_START_DELAY))
            global_param['cluster_diagnose'] = self._config.get("CLUSTER_DIAGNOSE", CQLConfigSetting.CLUSTER_DIAGNOSE)
            global_param['cluster_diagnose_only'] = False
            global_param['keyspace'] = self._config.get("KEYSPACE", CQLConfigSetting.KEYSPACE)
            global_param['bulk_list_r'] = literal_eval(self._config.get("BULK_LIST_R", CQLConfigSetting.BULK_LIST_R))
            global_param['bulk_list_w'] = literal_eval(self._config.get("BULK_LIST_W", CQLConfigSetting.BULK_LIST_W))
            global_param['multiple_env_delay'] = int(self._config.get('MULTIPLE_ENV_DELAY', CQLConfigSetting.MULTIPLE_ENV_DELAY))

            # global connection & login
            if self._config.get("IP", None):
                global_param["ip"] = self._config["IP"]
            if self._config.get("PORT", None):
                global_param["port"] = self._config["PORT"]
            if self._config.get("SECURE_CONNECT_BUNDLE", None):
                global_param["secure_connect_bundle"] = self._config["SECURE_CONNECT_BUNDLE"]
            if self._config.get("USERNAME", None):
                global_param['username'] = self._config["USERNAME"]
            if self._config.get("PASSWORD", None):
                global_param['password'] = self._config["PASSWORD"]

            return global_param
        else:
            return None

    def _get_adapter(self, global_param) -> str:
        adapter = self._inherit_param("ADAPTER", global_param, 'adapter')
        if not adapter in CQLAdapter.__members__:
            print(Fore.LIGHTRED_EX, f"!!! Unsupported ADAPTER name '{adapter}', we switched to the default adapter 'Cassandra' !!!", Style.RESET_ALL)
            return CQLAdapter[CQLConfigSetting.ADAPTER.lower()]
        return CQLAdapter[adapter.lower()]

    def get_params(self, adapter, global_param) -> dict:
        param={}

        if cql_helper.str2bool(self._config.get(adapter, "Off")):
            # shared params for all providers

            param['adapter'] = self._get_adapter(global_param)
            param['test_type'] = self._config.get("TEST_TYPE", CQLConfigSetting.TEST_TYPE).lower()
            if param['test_type'] == "r":
                param['bulk_list'] = self._inherit_param_eval("BULK_LIST", global_param,'bulk_list_r', CQLConfigSetting.BULK_LIST_R)
            else:
                param['bulk_list'] = self._inherit_param_eval("BULK_LIST", global_param,'bulk_list_w', CQLConfigSetting.BULK_LIST_W)
            param['keyspace'] = self._inherit_param("KEYSPACE", global_param, "keyspace", CQLConfigSetting.KEYSPACE)

            # connection setting (relation to global_param)
            param["ip"] = self._inherit_param(f"{adapter}_IP", global_param, 'ip', CQLConfigSetting.IP).split(",")
            param["port"] = self._inherit_param(f"{adapter}_PORT", global_param, 'port', CQLConfigSetting.PORT)

            # login setting (relation to global_param)
            secure_connect_bundle = self._inherit_param(f"{adapter}_SECURE_CONNECT_BUNDLE", global_param, 'secure_connect_bundle')
            if secure_connect_bundle:
                param['secure_connect_bundle'] = secure_connect_bundle
            username = self._inherit_param(f"{adapter}_USERNAME", global_param,'username', CQLConfigSetting.USERNAME)
            if username:
                param['username'] = username
            password_path = self._inherit_param(f"{adapter}_PASSWORD", global_param, 'password')
            param['password'] = cql_helper.read_file(password_path) if password_path else CQLConfigSetting.PASSWORD

            # replication setting
            param['replication_class'] = self._config.get(f"{adapter}_REPLICATION_CLASS", CQLConfigSetting.REPLICATION_CLASS)
            param['replication_factor'] = self._config.get(f"{adapter}_REPLICATION_FACTOR", CQLConfigSetting.REPLICATION_FACTOR)

            # compaction
            if self._config.get(f"{adapter}_COMPACTION", None):
                param['compaction'] = self._config[f"{adapter}_COMPACTION"]
            if self._config.get(f"{adapter}_COMPACTION_PARAMS", None):
                param['compaction_params'] = self._config[f"{adapter}_COMPACTION_PARAMS"]

            # consistency level
            param['consistency_level'] = ConsistencyHelper.name_to_value[self._config.get(f"{adapter}_CONSISTENCY_LEVEL",
                                                                                          CQLConfigSetting.CONSISTENCY_LEVEL).upper()]

            # network balancing, local data center for correct setting of balancing (RoundRobinPolicy or DCAwareRoundRobinPolicy)
            param['local_dc'] = self._config.get(f"{adapter}_LB_LOCAL_DC", CQLConfigSetting.LB_LOCAL_DC)

            # label
            param['label'] = self._config.get(f"{adapter}_LABEL", CQLConfigSetting.LABEL)

            return param
        else:
            return None