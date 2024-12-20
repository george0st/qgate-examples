from cassandra import ConsistencyLevel
from ast import literal_eval
from os import path
from dotenv import dotenv_values
import cql_helper


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
    BULK_LIST_RW = "[[5, 10]]"
    EXECUTORS = "[[1, 1, '1x threads'], [2, 1, '1x threads']]"

    # The other tuning
    EXECUTOR_START_DELAY = "0"
    DETAIL_OUTPUT = "True"
    GENERATE_GRAPH = "Perf"
    CLUSTER_DIAGNOSE = "Short"
    MULTIPLE_ENV_DELAY = "0"

    TABLE = "t01"
    KEYSPACE = "prftest"
    TEST_TYPE = "W"
    REPLICATION_CLASS = "NetworkTopologyStrategy"
    REPLICATION_FACTOR = "3"
    CONSISTENCY_LEVEL = "LOCAL_QUORUM"
    USERNAME = "cassandra"
    PASSWORD = "cassandra"
    PORT = "9042"
    IP = "localhost"
    LABEL = "local"
    NUMERIC_SCOPE = "99999"

    MODEL_REBUILD = "True"
    KEYSPACE_REBUILD = "True"

class CQLConfig:
    """The configuration of CQL, based on ENV files."""

    def __init__(self, perf_dir = ".", force_param: str = None):
        """Processing/Parsing of dictionary parameters from config/ENV files"""
        self._perf_dir = perf_dir
        self._force_params= self._get_force_params(force_param)
        self._config = {}

    def _inherit_param_eval(self, param_name, global_param, global_param_name, param_name_default = None):
        """Get item from single or from global ENV"""

        if self._force_params:
            if self._force_params.get(param_name, None):
                return literal_eval(self._force_params[param_name])

        if self._config.get(param_name, None):
            return literal_eval(self._config[param_name])
        else:
            # inheritance of param from global_param
            if global_param:
                if global_param.get(global_param_name, None) is not None:
                    return global_param[global_param_name]
            return param_name_default

    def _inherit_param(self, param_name, global_param, global_param_name, param_name_default = None):
        """Get item from single or from global ENV"""

        if self._force_params:
            if self._force_params.get(param_name, None):
                return self._force_params[param_name]

#        if param_name:
        if self._config.get(param_name, None):
            return self._config[param_name]

        # inheritance of param from global_param
        if global_param:
            if global_param.get(global_param_name, None) is not None:
                return global_param[global_param_name]
        return param_name_default

    def get_global_params(self, env_file, only_cluster_diagnose = False, level = "short") -> dict:

        global_param = {}

        env_file_path = path.join(self._perf_dir, "config", env_file)
        if not path.exists(env_file_path):
            raise Exception(f"Invalid path to ENV file '{env_file_path}'.")

        self._config = dotenv_values(env_file_path)

        # shared params for all providers
        global_param['multiple_env'] = self._config.get('MULTIPLE_ENV', None)
        if global_param['multiple_env']:
            # multiple configurations

            global_param['perf_dir'] = self._perf_dir
            global_param['adapter'] = self._config.get("ADAPTER", None)
            global_param['executors'] = literal_eval(self._config.get("EXECUTORS", CQLConfigSetting.EXECUTORS))
            global_param['detail_output'] = cql_helper.str2bool(self._config.get('DETAIL_OUTPUT', CQLConfigSetting.DETAIL_OUTPUT))
            global_param['generate_graph'] = self._config.get('GENERATE_GRAPH', CQLConfigSetting.GENERATE_GRAPH)
            global_param['executor_duration'] = int(self._config.get('EXECUTOR_DURATION', CQLConfigSetting.EXECUTOR_DURATION))
            global_param['executor_start_delay'] = int(self._config.get('EXECUTOR_START_DELAY', CQLConfigSetting.EXECUTOR_START_DELAY))
            if only_cluster_diagnose:
                global_param['cluster_diagnose'] = level
                global_param['cluster_diagnose_only'] = True
            else:
                global_param['cluster_diagnose'] = self._config.get("CLUSTER_DIAGNOSE", CQLConfigSetting.CLUSTER_DIAGNOSE)
                global_param['cluster_diagnose_only'] = False
            global_param['model_rebuild'] = self._config.get("MODEL_REBUILD", CQLConfigSetting.MODEL_REBUILD)
            global_param['table'] = self._config.get("TABLE", CQLConfigSetting.TABLE)
            global_param['keyspace'] = self._config.get("KEYSPACE", CQLConfigSetting.KEYSPACE)
            global_param['bulk_list_r'] = literal_eval(self._config.get("BULK_LIST_R", CQLConfigSetting.BULK_LIST_R))
            global_param['bulk_list_w'] = literal_eval(self._config.get("BULK_LIST_W", CQLConfigSetting.BULK_LIST_W))
            global_param['bulk_list_rw'] = literal_eval(self._config.get("BULK_LIST_RW", CQLConfigSetting.BULK_LIST_RW))
            global_param['multiple_env_delay'] = int(self._config.get('MULTIPLE_ENV_DELAY', CQLConfigSetting.MULTIPLE_ENV_DELAY))

            if self._config.get("PERCENTILE", None):
                global_param['percentile'] = float(self._config['PERCENTILE'])

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
            if self._config.get("CONSISTENCY_LEVEL", None):
                global_param['consistency_level'] = self._config["CONSISTENCY_LEVEL"]

            # network global setting
            if self._config.get("LB_LOCAL_DC", None):
                global_param['local_dc'] = self._config["LB_LOCAL_DC"]

            # numeric scope
            if self._config.get("NUMERIC_SCOPE", None):
                global_param['numeric_scope'] = self._config["NUMERIC_SCOPE"]

            return global_param
        else:
            return None

    def _get_force_params(self, force_param: str) -> dict:
        if force_param:
            if len(force_param) > 0:
                force_params = {}
                parse_params = force_param.split(";");
                for parse_item in parse_params:
                    force_items = parse_item.split("=",2)
                    if len(force_items) == 2:
                        key=force_items[0].strip(" ;\r\n")
                        item=force_items[1].strip(" ;\r\n")
                        if len(key) > 0:
                            force_params[key]=item
                return force_params
        return None

    def get_params(self, env_file, global_param: dict) -> (dict, dict):
        """"""
        executor_params = {}
        manage_params = {}

        # load ENV file
        env_file_path=path.join(self._perf_dir, "config", env_file)
        if not path.exists(env_file_path):
            raise Exception(f"Invalid path to ENV file '{env_file_path}'.")
        self._config = dotenv_values(env_file_path)

        manage_params = self._create_manage_param(global_param)
        executor_params = self._create_executor_param(global_param)

        return executor_params, manage_params

    def _create_manage_param(self, global_param: dict) -> dict:
        """Create params for management/setting of executors"""
        manage_params = {}
        manage_params = global_param.copy()

        manage_params['executor_duration'] = int(self._inherit_param("EXECUTOR_DURATION", global_param, 'executor_duration'))
        manage_params['executors'] = self._inherit_param_eval("EXECUTORS", global_param, 'executors', CQLConfigSetting.EXECUTORS)
        manage_params['adapter'] = self._inherit_param("ADAPTER", global_param, 'adapter', CQLConfigSetting.ADAPTER).lower()
        manage_params['test_type'] = self._config.get("TEST_TYPE", CQLConfigSetting.TEST_TYPE).lower()
        if manage_params['test_type'] == "r":
            manage_params['bulk_list'] = self._inherit_param_eval("BULK_LIST", global_param, 'bulk_list_r', CQLConfigSetting.BULK_LIST_R)
        elif manage_params['test_type'] == "w":
            manage_params['bulk_list'] = self._inherit_param_eval("BULK_LIST", global_param, 'bulk_list_w', CQLConfigSetting.BULK_LIST_W)
        elif manage_params['test_type'] == "rw" or manage_params['test_type'] == "wr":
            manage_params['bulk_list'] = self._inherit_param_eval("BULK_LIST", global_param, 'bulk_list_rw', CQLConfigSetting.BULK_LIST_RW)
        manage_params['generate_graph'] = self._inherit_param('GENERATE_GRAPH', global_param, 'generate_graph', CQLConfigSetting.GENERATE_GRAPH)
        # label
        manage_params['label'] = self._config.get("LABEL", CQLConfigSetting.LABEL)
        return manage_params

    def _create_executor_param(self, global_param: dict) -> dict:
        """Create params for usage in executors (in processes and threads)"""

        executor_params = {}

        executor_params['model_rebuild'] = cql_helper.str2bool(self._inherit_param("MODEL_REBUILD", global_param, "model_rebuild", CQLConfigSetting.MODEL_REBUILD))

        executor_params['table'] = self._inherit_param("TABLE", global_param, "table", CQLConfigSetting.TABLE)
        executor_params['keyspace'] = self._inherit_param("KEYSPACE", global_param, "keyspace", CQLConfigSetting.KEYSPACE)

        # percentile setting
        percentile = self._inherit_param("PERCENTILE", global_param, "percentile")
        if percentile:
            executor_params['percentile'] = float(percentile)

        # connection setting (relation to global_param)
        executor_params["ip"] = self._inherit_param("IP", global_param, 'ip', CQLConfigSetting.IP).split(",")
        executor_params["ip"] = [ip.strip() for ip in executor_params["ip"]]    # cleaning IP addresses
        executor_params["port"] = self._inherit_param("PORT", global_param, 'port', CQLConfigSetting.PORT)

        # login setting (relation to global_param)
        secure_connect_bundle = self._inherit_param("SECURE_CONNECT_BUNDLE", global_param,'secure_connect_bundle')
        if secure_connect_bundle:
            executor_params['secure_connect_bundle'] = secure_connect_bundle
        username = self._inherit_param("USERNAME", global_param, 'username', CQLConfigSetting.USERNAME)
        if username:
            executor_params['username'] = username
        password_path = self._inherit_param("PASSWORD", global_param, 'password')
        executor_params['password'] = cql_helper.read_file(path.join(global_param['perf_dir'], password_path)) if password_path else CQLConfigSetting.PASSWORD

        # keyspace rebuild & # replication setting
        executor_params['keyspace_rebuild'] = cql_helper.str2bool(self._config.get("KEYSPACE_REBUILD", CQLConfigSetting.KEYSPACE_REBUILD))
        executor_params['keyspace_replication_class'] = self._config.get("KEYSPACE_REPLICATION_CLASS", CQLConfigSetting.REPLICATION_CLASS)
        executor_params['keyspace_replication_factor'] = self._config.get("KEYSPACE_REPLICATION_FACTOR", CQLConfigSetting.REPLICATION_FACTOR)

        # table compaction & compaction params
        if self._config.get("COMPACTION", None):
            executor_params['compaction'] = self._config["COMPACTION"]
        if self._config.get("COMPACTION_PARAMS", None):
            executor_params['compaction_params'] = self._config["COMPACTION_PARAMS"]

        # consistency level
        executor_params['consistency_level'] = ConsistencyHelper.name_to_value[self._inherit_param("CONSISTENCY_LEVEL",
                                                                                                   global_param,
                                                                                                   'consistency_level',
                                                                                                   CQLConfigSetting.CONSISTENCY_LEVEL).upper()]

        # network balancing, local data center for correct setting of balancing (RoundRobinPolicy or DCAwareRoundRobinPolicy)
        local_dc = self._inherit_param("LB_LOCAL_DC", global_param, 'local_dc')
        if local_dc:
            executor_params['local_dc'] = local_dc

        # numeric scope
        executor_params['numeric_scope'] = int(self._inherit_param("NUMERIC_SCOPE", global_param, 'numeric_scope', CQLConfigSetting.NUMERIC_SCOPE))
        return executor_params
