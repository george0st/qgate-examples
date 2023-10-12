from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster
from cassandra.cluster import ExecutionProfile
from cassandra.cluster import EXEC_PROFILE_DEFAULT
from cassandra.query import BatchStatement

from qgate_perf.parallel_executor import ParallelExecutor
from qgate_perf.parallel_probe import ParallelProbe
from qgate_perf.run_setup import RunSetup
import pandas, numpy

def prf_cql(run_setup: RunSetup) -> ParallelProbe:
    """ Function for performance testing"""
    generator = numpy.random.default_rng()

    # INIT - contain executor synchonization, if needed
    probe=ParallelProbe(run_setup)

    profile = ExecutionProfile(request_timeout=60)

    cluster = Cluster(contact_points=[run_setup.param('ip')],
                      port=run_setup.param('port'),
                      execution_profiles={EXEC_PROFILE_DEFAULT: profile},
                      control_connection_timeout=60,
                      idle_heartbeat_interval=60,
                      connect_timeout=60)
#    session = cluster.connect(keyspace="jist")
    session = cluster.connect()

    columns="fn0"
    items="?"
    for i in range(1, run_setup.bulk_col):
        columns+=f", fn{i}"
        items+=", ?"

    insert_user = session.prepare(f"INSERT INTO jist.t01 ({columns}) VALUES ({items})")
    batch = BatchStatement(consistency_level=ConsistencyLevel.ONE)

    while (True):
        batch.clear()

        # insert, update only 1 mil. value, default limit for killing Cassandra solution
        data_frm = pandas.DataFrame(generator.integers(999999, size=(run_setup.bulk_row, run_setup.bulk_col)),
            columns=[f"fn{i}" for i in range(run_setup.bulk_col)])

        # prepare data
        for row in data_frm.values:
            batch.add(insert_user, row)

        # START - probe, only for this specific code part
        probe.start()

        session.execute(batch)

        # STOP - probe
        if probe.stop():
            break

    # RETURN - data from probe
    return probe

def prf_Scylla(run_setup: RunSetup) -> ParallelProbe:
    """ Function for performance testing"""
    generator = numpy.random.default_rng()

    # INIT - contain executor synchonization, if needed
    probe=ParallelProbe(run_setup)

    profile = ExecutionProfile(request_timeout=60)

    cluster = Cluster(contact_points=[run_setup.param('ip')],
                      port=run_setup.param('port'),
                      execution_profiles={EXEC_PROFILE_DEFAULT: profile},
                      control_connection_timeout=60,
                      idle_heartbeat_interval=60,
                      connect_timeout=60)
    session = cluster.connect(keyspace="catalog")


    columns="fn0"
    items="?"
    for i in range(1, run_setup.bulk_col):
        columns+=f", fn{i}"
        items+=", ?"

    insert_user = session.prepare(f"INSERT INTO jist.t01 ({columns}) VALUES ({items})")
    batch = BatchStatement(consistency_level=ConsistencyLevel.ONE)

    while (True):
        batch.clear()

        # insert, update only 1 mil. value, default limit for killing Cassandra solution
        data_frm = pandas.DataFrame(generator.integers(999999, size=(run_setup.bulk_row, run_setup.bulk_col)),
            columns=[f"fn{i}" for i in range(run_setup.bulk_col)])

        # prepare data
        for row in data_frm.values:
            batch.add(insert_user, row)

        # START - probe, only for this specific code part
        probe.start()

        session.execute(batch)

        # STOP - probe
        if probe.stop():
            break

    # RETURN - data from probe
    return probe


def prf_Cassandra(run_setup: RunSetup) -> ParallelProbe:
    """ Function for performance testing"""
    generator = numpy.random.default_rng()

    # INIT - contain executor synchonization, if needed
    probe=ParallelProbe(run_setup)



    profile = ExecutionProfile(request_timeout=60)
    cluster = Cluster([run_setup.param('ip')],
                      execution_profiles={EXEC_PROFILE_DEFAULT: profile},
                      port=run_setup.param('port'),
                      control_connection_timeout=20,
                      idle_heartbeat_interval=60,
                      connect_timeout=20)
    session = cluster.connect()

    columns="fn0"
    items="?"
    for i in range(1, run_setup.bulk_col):
        columns+=f", fn{i}"
        items+=", ?"

    insert_user = session.prepare(f"INSERT INTO jist.t01 ({columns}) VALUES ({items})")
    batch = BatchStatement(consistency_level=ConsistencyLevel.ONE)

    while (True):
        batch.clear()

        # insert, update only 1 mil. value, default limit for killing Cassandra solution
        data_frm = pandas.DataFrame(generator.integers(999999, size=(run_setup.bulk_row, run_setup.bulk_col)),
            columns=[f"fn{i}" for i in range(run_setup.bulk_col)])

        # prepare data
        for row in data_frm.values:
            batch.add(insert_user, row)

        # START - probe, only for this specific code part
        probe.start()

        session.execute(batch)

        # STOP - probe
        if probe.stop():
            break

    # RETURN - data from probe
    return probe

def prepare_model():
    #jdbc:cassandra://redis-fs-test.vn.infra:9042

    profile = ExecutionProfile(request_timeout=60)
    cluster = Cluster(['10.19.135.161'],
                      execution_profiles={EXEC_PROFILE_DEFAULT: profile},
                      port=9042,
                      control_connection_timeout=20,
                      idle_heartbeat_interval=60,
                      connect_timeout=20)
    try:
        session = cluster.connect()

        session.execute("CREATE KEYSPACE IF NOT EXISTS jist WITH replication = {'class':'SimpleStrategy', 'replication_factor' : 3};")
        session.execute("DROP TABLE jist.t01")

        session.execute("CREATE TABLE IF NOT EXISTS jist.t01 (fn0 int PRIMARY KEY, fn1 int, fn2 int, fn3 int"
                        ", fn4 int, fn5 int, fn6 int, fn7 int, fn8 int, fn9 int)")

        # init insert for basic tests
        for i in range(10):
            session.execute(f"INSERT INTO jist.t01 (fn0, fn1, fn2, fn3, fn4, fn5, fn6, fn7, fn8, fn9) "
                            f"VALUES({i},0, 0,0,0,0,0,0,0,0)")
            print(i)

    finally:
        cluster.shutdown()


def perf_test(scylla: bool = False):

    if scylla:
        generator = ParallelExecutor(prf_cql,
                                     label="Scylla",
                                     detail_output=True,
                                     output_file="../output/prf_Scylla.txt")
        setting={"ip":   "localhost",
                 "port": 9042}
    else:
        generator = ParallelExecutor(prf_cql,
                                     label="Cassandra",
                                     detail_output=True,
                                     output_file="../output/prf_cassandara.txt")
        setting={"ip":   "10.19.135.161",
                 "port": 9042}

    setup = RunSetup(duration_second=30, start_delay=2, parameters=setting)
    generator.run_bulk_executor(bulk_list=[[200, 10]],
                                executor_list=[[1, 2, '2x threads'],
                                               [4, 2, '2x threads'],
                                               [8, 2, '2x threads'],
                                               [16, 2, '2x threads']],
                                run_setup=setup)

if __name__ == '__main__':
    # prepare_model()
    perf_test(True)
