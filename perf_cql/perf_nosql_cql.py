from enum import Enum
import datetime, time
import numpy

from cassandra import ConsistencyLevel
from cassandra.cluster import ExecutionProfile
from cassandra.cluster import EXEC_PROFILE_DEFAULT
from cassandra.policies import DCAwareRoundRobinPolicy
from cassandra.query import BatchStatement

from qgate_perf.parallel_executor import ParallelExecutor
from qgate_perf.parallel_probe import ParallelProbe
from qgate_perf.run_setup import RunSetup
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster

from dotenv import load_dotenv, dotenv_values
from ssl import PROTOCOL_TLSv1_2, PROTOCOL_TLSv1, SSLContext, CERT_NONE, CERT_REQUIRED


class Setting:
    TABLE_NAME = "t02"
    MAX_GNR_VALUE = 999999

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

def read_file(file) -> str:
    with open(file) as f:
        return f.readline()

def create_cluster(run_setup: RunSetup):
    """Create cluster for connection"""
    authProvider=None

    # connection setting
    if run_setup['username']:
        authProvider = PlainTextAuthProvider(username=run_setup["username"],
                                             password=read_file(run_setup["password"]))

    if run_setup["secure_connect_bundle"]:
        # connection with 'secure_connect_bundle' to the cloud
        cloud_config = {
            "secure_connect_bundle" : run_setup["secure_connect_bundle"],
            'use_default_tempdir': True
        }
        cluster = Cluster(cloud = cloud_config,
                          auth_provider=authProvider,
                          execution_profiles={EXEC_PROFILE_DEFAULT: ExecutionProfile(request_timeout=30)},
                          control_connection_timeout=30,
                          idle_heartbeat_interval=30,
                          connect_timeout=30)
    else:
        # ssl_opts = {
        #     'ca_certs': 'C:\Python\qgate-examples\secrets\public-key.pem',
        #     'ssl_version': PROTOCOL_TLSv1_2,
        #     'cert_reqs': CERT_REQUIRED  # Certificates are required and validated
        # }
        #
        # ssl_context = SSLContext(PROTOCOL_TLSv1_2)
        # ssl_context.verify_mode = CERT_NONE

        # connection with 'ip' and 'port'
        cluster = Cluster(contact_points=run_setup['ip'],
                          port=run_setup['port'],
                          auth_provider=authProvider,
                          execution_profiles={EXEC_PROFILE_DEFAULT: ExecutionProfile(request_timeout=30)},
                          control_connection_timeout=30,
                          idle_heartbeat_interval=30,
                          connect_timeout=30)
    return cluster

def init_rng_generator():
    """Init generator of random values"""

    # now
    now = time.time()
    now_ms = (now - int(now)) * 1000000000

    # random value, based on CPU
    ns_start = time.perf_counter_ns()
    time.sleep(0.01)
    ns_stop = time.perf_counter_ns()

    return numpy.random.default_rng([int(now), int(now_ms), ns_stop - ns_start, ns_stop])

def prf_cql_read(run_setup: RunSetup) -> ParallelProbe:
    generator = init_rng_generator()
    columns, items="", ""

    cluster = create_cluster(run_setup)
    try:
        session = cluster.connect()

        # INIT - contain executor synchronization, if needed
        probe = ParallelProbe(run_setup)

        # prepare select statement for batch
        for i in range(0, run_setup.bulk_col):
            columns+=f"fn{i},"
        select_statement = session.prepare(f"SELECT {columns[:-1]} FROM {run_setup['keyspace']}.{Setting.TABLE_NAME} WHERE fn0=? and fn1=?")

        while True:

            # generate synthetic data (only 1 mil. values for select)
            #  NOTE: I wll generate only values for two columns (as primary keys)
            synthetic_data = generator.integers(Setting.MAX_GNR_VALUE, size=(run_setup.bulk_row, 2))

            # START - probe, only for this specific code part
            probe.start()

            # prepare data
            for row in synthetic_data:
                session.execute(select_statement.bind(row))

            # STOP - probe
            if probe.stop():
                break
    finally:
        if cluster:
            cluster.shutdown()

    return probe

def prf_cql_write(run_setup: RunSetup) -> ParallelProbe:
    generator = init_rng_generator()
    columns, items="", ""

    cluster = create_cluster(run_setup)

    if run_setup.is_init:
        # create NoSQL schema for write perf tests
        prepare_model(cluster, run_setup)
        return None

    try:
        session = cluster.connect()

        # INIT - contain executor synchronization, if needed
        probe = ParallelProbe(run_setup)

        # prepare insert statement for batch
        for i in range(0, run_setup.bulk_col):
            columns+=f"fn{i},"
            items+="?,"
        insert_statement = session.prepare(f"INSERT INTO {run_setup['keyspace']}.{Setting.TABLE_NAME} ({columns[:-1]}) VALUES ({items[:-1]})")
        batch = BatchStatement(consistency_level=ConsistencyHelper.name_to_value[run_setup['consistency_level']])

        while True:
            batch.clear()

            # generate synthetic data (only 1 mil. values for insert or update)
            synthetic_data = generator.integers(Setting.MAX_GNR_VALUE, size=(run_setup.bulk_row, run_setup.bulk_col))

            # prepare data
            for row in synthetic_data:
                batch.add(insert_statement, row)

            # START - probe, only for this specific code part
            probe.start()

            session.execute(batch)

            # STOP - probe
            if probe.stop():
                break
    finally:
        if cluster:
            cluster.shutdown()

    return probe

def prepare_model(cluster, run_setup: RunSetup):

    try:
        session = cluster.connect()
        columns=""

        if run_setup["cql"]!=CQLType.AstraDB:

            if run_setup['replication_factor']:
                # Drop key space
                session.execute(f"DROP KEYSPACE IF EXISTS {run_setup['keyspace']}")

                # Create key space
                # use different replication strategy 'class':'NetworkTopologyStrategy' for production HA mode
                #            session.execute("CREATE KEYSPACE IF NOT EXISTS jist2 WITH replication = {'class':'NetworkTopologyStrategy', 'replication_factor' : 3};")
                session.execute(f"CREATE KEYSPACE IF NOT EXISTS {run_setup['keyspace']}" +
                                " WITH replication = {" +
                                f"'class':'{run_setup['replication_class']}', 'replication_factor' : {run_setup['replication_factor']}" +
                                "};")

        # use LTW atomic command with IF
        session.execute(f"DROP TABLE IF EXISTS {run_setup['keyspace']}.{Setting.TABLE_NAME}")

        # prepare insert statement for batch
        for i in range(0, run_setup.bulk_col):
            columns+=f"fn{i} int,"

        # complex primary key (partition key 'fn0' and cluster key 'fn1')
        session.execute(f"CREATE TABLE IF NOT EXISTS {run_setup['keyspace']}.{Setting.TABLE_NAME} ({columns[:-1]}, PRIMARY KEY (fn0, fn1))")

    finally:
        if cluster:
            cluster.shutdown()

def perf_test(cql: CQLType, parameters: dict, duration=5, bulk_list=None, executor_list=None):

    lbl = str(cql).split('.')[1]
    lbl_suffix = f"-{parameters['label']}" if parameters.get('label', None) else ""
    generator = ParallelExecutor(prf_cql_write,
                                 label=f"{lbl}-write{lbl_suffix}",
                                 detail_output=True,
                                 output_file=f"../output/prf_{lbl.lower()}-write{lbl_suffix.lower()}-{datetime.date.today()}.txt",
                                 init_each_bulk=True)

    parameters["cql"] = cql
    setup = RunSetup(duration_second=duration, start_delay=0, parameters=parameters)
    generator.run_bulk_executor(bulk_list, executor_list, run_setup=setup)
    generator.create_graph_perf("../output")

def get_config(config, adapter):
    param={}
    param['keyspace'] = config["KEYSPACE"]

    if config[adapter].lower() == "on":
        # connection setting
        if config.get(f"{adapter}_IP", None):
            param["ip"] = config[f"{adapter}_IP"].split(",")
        if config.get(f"{adapter}_PORT", None):
            param["port"] = config[f"{adapter}_PORT"]
        if config.get(f"{adapter}_SECURE_CONNECT_BUNDLE", None):
            param["secure_connect_bundle"] = config[f"{adapter}_SECURE_CONNECT_BUNDLE"]

        # login setting
        if config.get(f"{adapter}_USERNAME", None) or config.get(f"{adapter}_PASSWORD", None):
            param['username'] = config.get(f"{adapter}_USERNAME", None)
            param['password'] = config.get(f"{adapter}_PASSWORD", None)

        # replication setting
        if config.get(f"{adapter}_REPLICATION_CLASS", None) or config.get(f"{adapter}_REPLICATION_FACTOR", None):
            param['replication_class'] = config.get(f"{adapter}_REPLICATION_CLASS", None)
            param['replication_factor'] = config.get(f"{adapter}_REPLICATION_FACTOR", None)

        # consistency level
        param['consistency_level'] = config.get(f"{adapter}_CONSISTENCY_LEVEL", "ddd")

        # label
        param['label'] = config.get(f"{adapter}_LABEL", None)

        return param
    else:
        return None

def exec_config(config, bulks, duration_seconds, executors):
    param = get_config(config, 'COSMOSDB')
    if param:
        perf_test(CQLType.CosmosDB,
                  param,
                  bulk_list=bulks,
                  duration=duration_seconds,
                  executor_list=executors)

    param=get_config(config, 'SCYLLADB')
    if param:
        perf_test(CQLType.ScyllaDB,
                  param,
                  duration=duration_seconds,
                  bulk_list=bulks,
                  executor_list=executors)

    param=get_config(config, 'CASSANDRA')
    if param:
        perf_test(CQLType.Cassandra,
                  param,
                  duration=duration_seconds,
                  bulk_list=bulks,
                  executor_list=executors)

    param=get_config(config, 'ASTRADB')
    if param:
        perf_test(CQLType.AstraDB,
                  param,
                  bulk_list=bulks,
                  duration=duration_seconds,
                  executor_list=executors)

if __name__ == '__main__':

    # size of data bulks 
    bulks = [[200, 10]]

    # list of executors (for application to all bulks)
    # executors = [[2, 1, '1x threads'], [4, 1, '1x threads'], [8, 1, '1x threads'],
    #              [2, 2, '2x threads'], [4, 2, '2x threads'], [8, 2, '2x threads']]
    #
    executors = [[2, 1, '1x threads'], [4, 1, '1x threads'], [8, 1, '1x threads'], [16, 1, '1x threads'],
                 [2, 2, '2x threads'], [4, 2, '2x threads'], [8, 2, '2x threads'], [16, 2, '2x threads']]

    #executors = [[2, 1, '1x threads'], [4, 1, '1x threads']]

    # performance test duration
    duration_seconds=5

    config = dotenv_values("config/perf_nosql_cql.env")
    param=config.get('MULTIPLE_ENV', None)
    if param:
        # multiple configurations
        envs=config["MULTIPLE_ENV"].split(",")
        for env in envs:
            exec_config(dotenv_values(env.strip()), bulks, duration_seconds, executors)
    else:
        # single configuration
        exec_config(config, bulks, duration_seconds, executors)
