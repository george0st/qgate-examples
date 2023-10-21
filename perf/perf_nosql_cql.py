import datetime

from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster
from cassandra.cluster import ExecutionProfile
from cassandra.cluster import EXEC_PROFILE_DEFAULT
from cassandra.query import BatchStatement

from qgate_perf.parallel_executor import ParallelExecutor
from qgate_perf.parallel_probe import ParallelProbe
from qgate_perf.run_setup import RunSetup
import numpy

#
# class CqlTest:
#
#     def __init__(self):
#         pass


def prf_cql(run_setup: RunSetup) -> ParallelProbe:

    generator = numpy.random.default_rng()
    columns, items="", ""

    # INIT - contain executor synchonization, if needed
    probe=ParallelProbe(run_setup)

    # connect
    cluster = Cluster(contact_points=[run_setup.param('ip')],
                      port=run_setup.param('port'),
                      execution_profiles={EXEC_PROFILE_DEFAULT: ExecutionProfile(request_timeout=30)},
                      control_connection_timeout=30,
                      idle_heartbeat_interval=30,
                      connect_timeout=30)

    if run_setup.is_init:
        # create NoSQL schema
        prepare_model(cluster)
        return None

    try:
        session = cluster.connect()

        # prepare insert statement for batch
        for i in range(0, run_setup.bulk_col):
            columns+=f"fn{i},"
            items+="?,"
        insert_statement = session.prepare(f"INSERT INTO jist.t02 ({columns[:-1]}) VALUES ({items[:-1]})")
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

def prepare_model(cluster):

    try:
        session = cluster.connect()

        session.execute("CREATE KEYSPACE IF NOT EXISTS jist WITH replication = {'class':'SimpleStrategy', 'replication_factor' : 1};")
        session.execute("DROP TABLE IF EXISTS jist.t02")

        session.execute("CREATE TABLE IF NOT EXISTS jist.t02 (fn0 int PRIMARY KEY, fn1 int, fn2 int, fn3 int"
                        ", fn4 int, fn5 int, fn6 int, fn7 int, fn8 int, fn9 int)")

        # one insert for basic tests (if everything is ready)
        session.execute(f"INSERT INTO jist.t02 (fn0, fn1, fn2, fn3, fn4, fn5, fn6, fn7, fn8, fn9) "
                        f"VALUES(0,0,0,0,0,0,0,0,0,0)")

    finally:
        if cluster:
            cluster.shutdown()

def perf_test(scylla: bool = False, ip="localhost", port=9042, bulk_list=None, executor_list=None):

    if scylla:
        generator = ParallelExecutor(prf_cql,
                                     label="Scylla",
                                     detail_output=True,
                                     output_file=f"../output/prf_scylla-{datetime.date.today()}.txt",
                                     init_each_bulk=True)
    else:
        generator = ParallelExecutor(prf_cql,
                                     label="Cassandra",
                                     detail_output=True,
                                     output_file=f"../output/prf_cassandara-{datetime.date.today()}.txt",
                                     init_each_bulk=True)

    setup = RunSetup(duration_second=10, start_delay=0, parameters={"ip": ip,"port": port})
    generator.run_bulk_executor(bulk_list, executor_list, run_setup=setup)
    generator.create_graph_perf(f"..\output")

if __name__ == '__main__':

    # size of data builks
    bulks = [[200, 10]]
    # list of executors
    executors = [[8, 2, '2x threads'],
                     [16, 2, '2x threads'],
                     [32, 2, '2x threads']]

    # ScyllaDB performnace tests
#    perf_test(scylla=True, ip="localhost", port=9042, bulk_list=bulks, executor_list=executors)
    # Cassandra performance tests
    perf_test(scylla=False, ip="10.19.135.161", port=9042, bulk_list=bulks, executor_list=executors)
