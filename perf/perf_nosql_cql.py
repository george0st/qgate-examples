from enum import Enum
import datetime
import numpy

from cassandra import ConsistencyLevel
from cassandra.cluster import ExecutionProfile
from cassandra.cluster import EXEC_PROFILE_DEFAULT
from cassandra.query import BatchStatement

from qgate_perf.parallel_executor import ParallelExecutor
from qgate_perf.parallel_probe import ParallelProbe
from qgate_perf.run_setup import RunSetup
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster

class CQLType(Enum):
    ScyllaDB = 1
    Cassandra = 2
    AstraDB = 3

def read_file(file) -> str:
    with open(file) as f:
        return f.readline()

def prf_cql(run_setup: RunSetup) -> ParallelProbe:
    generator = numpy.random.default_rng()  #seed=int(time.time())
    columns, items="", ""
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
        # connection with 'ip' and 'port'
        cluster = Cluster(contact_points=run_setup['ip'],
                          port=run_setup['port'],
                          auth_provider=authProvider,
                          execution_profiles={EXEC_PROFILE_DEFAULT: ExecutionProfile(request_timeout=30)},
                          control_connection_timeout=30,
                          idle_heartbeat_interval=30,
                          connect_timeout=30)

    if run_setup.is_init:
        # create NoSQL schema
        prepare_model(cluster, run_setup)
        return None

    try:
        session = cluster.connect()

        # INIT - contain executor synchonization, if needed
        probe = ParallelProbe(run_setup)

        # prepare insert statement for batch
        for i in range(0, run_setup.bulk_col):
            columns+=f"fn{i},"
            items+="?,"
        insert_statement = session.prepare(f"INSERT INTO jist.t02 ({columns[:-1]}) VALUES ({items[:-1]})")
        if run_setup['cql']==CQLType.AstraDB:
            # not support CL.ONE see error "Provided value ONE is not allowed for Write Consistency Level (disallowed values are: [ANY, ONE, LOCAL_ONE]"
            batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
        else:
            batch = BatchStatement(consistency_level=ConsistencyLevel.ONE)

        while True:
            batch.clear()

            # generate synthetic data (only 1 mil. values for insert or update)
            synthetic_data = generator.integers(999999, size=(run_setup.bulk_row, run_setup.bulk_col))

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
            # Create new key space if not exist
            # use different replication strategy 'class':'NetworkTopologyStrategy' for production HA mode
            session.execute("CREATE KEYSPACE IF NOT EXISTS jist WITH replication = {'class':'SimpleStrategy', 'replication_factor' : 1};")

        # use LTW atomic command with IF
        session.execute("DROP TABLE IF EXISTS jist.t02")

        # prepare insert statement for batch
        for i in range(0, run_setup.bulk_col):
            columns+=f"fn{i} int,"

        # complex primary key (partition key 'fn0' and cluster key 'fn1')
        session.execute(f"CREATE TABLE IF NOT EXISTS jist.t02 ({columns[:-1]}, PRIMARY KEY (fn0, fn1))")

    finally:
        if cluster:
            cluster.shutdown()

def perf_test(cql: CQLType, parameters: dict, duration=5, bulk_list=None, executor_list=None):

    if cql==CQLType.ScyllaDB:
        generator = ParallelExecutor(prf_cql,
                                     label="Scylla",
                                     detail_output=True,
                                     output_file=f"../output/prf_scylla-{datetime.date.today()}.txt",
                                     init_each_bulk=True)
    elif cql==CQLType.Cassandra:
        generator = ParallelExecutor(prf_cql,
                                     label="Cassandra",
                                     detail_output=True,
                                     output_file=f"../output/prf_cassandara-{datetime.date.today()}.txt",
                                     init_each_bulk=True)
    elif cql==CQLType.AstraDB:
        generator = ParallelExecutor(prf_cql,
                                     label="AstraDB",
                                     detail_output=True,
                                     output_file=f"../output/prf_astradb-{datetime.date.today()}.txt",
                                     init_each_bulk=True)

    parameters["cql"]=cql
    setup = RunSetup(duration_second=duration, start_delay=0, parameters=parameters)
    generator.run_bulk_executor(bulk_list, executor_list, run_setup=setup)
    generator.create_graph_perf(f"..\output")

if __name__ == '__main__':

    # size of data bulks
    bulks = [[200, 10]]

    # list of executors (for application to all bulks)
    executors = [[2, 2, '2x threads'],
                 [4, 2, '2x threads'],
                 [16, 2, '2x threads']]

    # performance test duration
    duration_seconds=5

    # ScyllaDB performnace tests
    # Note:
    #   - please, change 'ip' and 'port' based on your needs
    # perf_test(CQLType.ScyllaDB,
    #           {"ip": ["localhost"], "port": 9042},
    #           duration=duration_seconds,
    #           bulk_list=bulks,
    #           executor_list=executors)

    # Cassandra performance tests
    # Note:
    #   - please, change 'ip' and 'port' based on your needs
    # perf_test(CQLType.Cassandra,
    #           {"ip": ["10.19.135.161"], "port": 9042},
    #           duration=duration_seconds,
    #           bulk_list=bulks,
    #           executor_list=executors)

    # AstraDB performance tests
    # Note:
    #   - please, change 'secure_connect_bundle', 'username', 'password' based on your needs
    #   - typicaly you have to switch off VPN
    # perf_test(CQLType.AstraDB,
    #           {"secure_connect_bundle": "c:/Python/secure-connect-astrajist.zip",
    #            "username": "UpBqQJwTWGUUKdZQTcZaoglA",
    #            "password": "c:/Python/client-secret.txt"},
    #           bulk_list=bulks,
    #           duration=duration_seconds,
    #           executor_list=executors)
