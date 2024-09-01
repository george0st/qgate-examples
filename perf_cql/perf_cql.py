import datetime, time
import cassandra.query
import numpy
from cassandra.query import BatchStatement, BoundStatement
from qgate_perf.parallel_executor import ParallelExecutor
from qgate_perf.parallel_probe import ParallelProbe
from qgate_perf.run_setup import RunSetup
from dotenv import load_dotenv, dotenv_values
from cql_config import CQLConfig, CQLType
from cql_access import CQLAccess, Setting
from colorama import Fore, Style
import cql_helper
from cql_status import CQLStatus

def prf_readwrite(run_setup: RunSetup) -> ParallelProbe:
    pass

def prf_read(run_setup: RunSetup) -> ParallelProbe:
    generator = cql_helper.get_rng_generator()
    columns, items="", ""
    cql = None
    session = None

    if run_setup.is_init:
        # cluster check
        if run_setup['cluster_check']:
            try:
                cql = CQLAccess(run_setup)
                cql.open()
                status=CQLStatus(cql.cluster)
                status.diagnose(True)
            finally:
                if cql:
                    cql.close()
        return None

    try:
        cql = CQLAccess(run_setup)
        cql.open()
        session = cql.create_session()

        # INIT - contains executor synchronization, if needed
        probe = ParallelProbe(run_setup)

        # prepare select statement
        for i in range(0, run_setup.bulk_col):
            columns+=f"fn{i},"

        for i in range(0, run_setup.bulk_row):
            items+="?,"

        select_statement = session.prepare(f"SELECT {columns[:-1]} FROM {run_setup['keyspace']}.{Setting.TABLE_NAME} WHERE fn0 IN ({items[:-1]}) and fn1 IN ({items[:-1]})")
        bound = cassandra.query.BoundStatement(select_statement, consistency_level=run_setup['consistency_level'])

        while True:

            # generate synthetic data
            #  NOTE: It will generate only values for two columns (as primary keys), not for all columns
            synthetic_data = generator.integers(Setting.MAX_GNR_VALUE, size=run_setup.bulk_row*2)

            # prepare data
            bound.bind(synthetic_data)

            # START - probe, only for this specific code part
            probe.start()

            rows = session.execute(bound)

            # STOP - probe
            if probe.stop():
                break
    finally:
        if session:
            session.shutdown()
        if cql:
            cql.close()
    return probe

def prf_write(run_setup: RunSetup) -> ParallelProbe:
    generator = cql_helper.get_rng_generator()
    columns, items = "", ""
    cql = None
    session = None

    if run_setup.is_init:
        # create schema for write data
        try:
            cql = CQLAccess(run_setup)
            cql.open()
            cql.create_model()

            if run_setup['cluster_check']:
                status=CQLStatus(cql.cluster)
                status.diagnose(True)
        finally:
            if cql:
                cql.close()
        return None

    try:
        cql = CQLAccess(run_setup)
        cql.open()
        session = cql.create_session()

        # INIT - contains executor synchronization, if needed
        probe = ParallelProbe(run_setup)

        # prepare insert statement for batch
        for i in range(0, run_setup.bulk_col):
            columns+=f"fn{i},"
            items+="?,"
        insert_statement = session.prepare(f"INSERT INTO {run_setup['keyspace']}.{Setting.TABLE_NAME} ({columns[:-1]}) VALUES ({items[:-1]})")
        batch = BatchStatement(consistency_level=run_setup['consistency_level'])

        while True:
            batch.clear()

            # generate synthetic data
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
        if session:
            session.shutdown()
        if cql:
            cql.close()

    return probe

def perf_test(cql: CQLType, parameters: dict, duration=5, bulk_list=None, executor_list=None):

    lbl = str(cql).split('.')[1]
    lbl_suffix = f"-{parameters['label']}" if parameters.get('label', None) else ""

    generator = None
    if parameters['test_type']=='w':    # WRITE perf test
        generator = ParallelExecutor(prf_write,
                                     label=f"{lbl}-write{lbl_suffix}",
                                     detail_output=True,
                                     output_file=f"../output/prf_{lbl.lower()}-write{lbl_suffix.lower()}-{datetime.date.today()}.txt",
                                     init_each_bulk=True)
    elif parameters['test_type']=='r':    # READ perf test
        generator = ParallelExecutor(prf_read,
                                     label=f"{lbl}-read{lbl_suffix}",
                                     detail_output=True,
                                     output_file=f"../output/prf_{lbl.lower()}-read{lbl_suffix.lower()}-{datetime.date.today()}.txt",
                                     init_each_bulk=True)
    # TODO: Add read & write
    # elif parameters['test_type']=='rw' or parameters['test_type']=='wr':    # READ & WRITE perf test
    #     generator = ParallelExecutor(prf_cql_readwrite(),
    #                                  label=f"{lbl}-read{lbl_suffix}",
    #                                  detail_output=True,
    #                                  output_file=f"../output/prf_{lbl.lower()}-write{lbl_suffix.lower()}-{datetime.date.today()}.txt",
    #                                  init_each_bulk=True)


    parameters["cql"] = cql

    # run tests & generate graphs
    setup = RunSetup(duration_second=duration, start_delay=0, parameters=parameters)
    generator.run_bulk_executor(bulk_list, executor_list, run_setup=setup)
    generator.create_graph_perf("../output", suppress_error = True)

def exec_config(config, bulks, duration_seconds, executors):

    param = CQLConfig(config, 'COSMOSDB').get_params()
    if param:
        perf_test(CQLType.CosmosDB,
                  param,
                  bulk_list=bulks,
                  duration=duration_seconds,
                  executor_list=executors)

    param = CQLConfig(config, 'SCYLLADB').get_params()
    if param:
        perf_test(CQLType.ScyllaDB,
                  param,
                  duration=duration_seconds,
                  bulk_list=bulks,
                  executor_list=executors)

    param = CQLConfig(config, 'CASSANDRA').get_params()
    if param:
        perf_test(CQLType.Cassandra,
                  param,
                  duration=duration_seconds,
                  bulk_list=bulks,
                  executor_list=executors)

    param = CQLConfig(config, 'ASTRADB').get_params()
    if param:
        perf_test(CQLType.AstraDB,
                  param,
                  bulk_list=bulks,
                  duration=duration_seconds,
                  executor_list=executors)

if __name__ == '__main__':

    # size of data bulks, requested format [[rows, columns], ...]
    bulks = [[10, 10]]

    # list of executors (for application to all bulks)
    # executors = [[2, 1, '1x threads'], [4, 1, '1x threads'], [8, 1, '1x threads'],
    #              [2, 2, '2x threads'], [4, 2, '2x threads'], [8, 2, '2x threads']]
    #
    # executors = [[8, 1, '1x threads'], [16, 1, '1x threads'], [32, 1, '1x threads'],
    #              [8, 2, '2x threads'], [16, 2, '2x threads'], [32, 2, '2x threads'],
    #              [8, 3, '3x threads'], [16, 3, '3x threads'], [32, 3, '3x threads']]

    executors = [[2, 2, '1x threads'], [4, 2, '1x threads']]

    #executors = [[1, 1, '1x threads']]

    # performance test duration
    duration_seconds=5

    config = dotenv_values("config/cass.env")
    multiple_env = config.get('MULTIPLE_ENV', None)
    if multiple_env:
        # multiple configurations
        multiple_env_delay = config.get('MULTIPLE_ENV_DELAY', 0)
        envs=[env.strip() for env in multiple_env.split(",")]
        env_count=0
        for env in envs:
            env_count+=1
            print(Fore.BLUE + f"Environment switch {env_count}/{len(envs)}: '{env}' ..." + Style.RESET_ALL)
            if env_count>1:
                time.sleep(int(multiple_env_delay))
            exec_config(dotenv_values(env), bulks, duration_seconds, executors)
    else:
        # single configuration
        exec_config(config, bulks, duration_seconds, executors)
