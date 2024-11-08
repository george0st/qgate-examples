import datetime, time
from os import path
from cassandra.query import BatchStatement, BoundStatement
from qgate_perf.parallel_executor import ParallelExecutor
from qgate_perf.parallel_probe import ParallelProbe
from qgate_perf.helper import GraphScope
from qgate_perf.run_setup import RunSetup
from cql_config import CQLConfig
from cql_access import CQLAccess, Setting
from colorama import Fore, Style
from cql_helper import get_rng_generator
from cql_health import CQLHealth, CQLDiagnosePrint
from glob import glob
import click


def prf_readwrite(run_setup: RunSetup) -> ParallelProbe:
    numeric_scope = run_setup['numeric_scope']
    generator = get_rng_generator()
    columns, items = "", ""
    cql = None
    session = None

    if run_setup.is_init:
        # create schema for write data
        try:
            cql = CQLAccess(run_setup)
            cql.open()
            cql.create_model()
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
            columns += f"fn{i},"
            items += "?,"

        # insert one value
        insert_statement = session.prepare(f"INSERT INTO {run_setup['keyspace']}.{Setting.TABLE_NAME} "
                                           f"({columns[:-1]}) VALUES ({items[:-1]});")
        insert_bound = BoundStatement(insert_statement,
                                      consistency_level = run_setup['consistency_level'])

        # select one value
        select_statement = session.prepare(f"SELECT {columns[:-1]} FROM {run_setup['keyspace']}.{Setting.TABLE_NAME} "
                                           f"WHERE fn0 = ? and fn1 = ?;")
        select_bound = BoundStatement(select_statement,
                                      consistency_level = run_setup['consistency_level'])

        while 1:
            # partly INIT
            probe.partly_init()

            # generate synthetic data for one cycle
            synthetic_insert_data = generator.integers(numeric_scope, size=(run_setup.bulk_row, run_setup.bulk_col))
            synthetic_select_data = generator.integers(numeric_scope, size=(run_setup.bulk_row, 2))

            # one cycle (with amount of call based on bulk_row)
            for index in range(run_setup.bulk_row):

                # prepare data
                insert_bound.bind(synthetic_insert_data[index])
                select_bound.bind(synthetic_select_data[index])

                # partly START
                probe.partly_start()

                # execute
                session.execute(insert_bound)
                session.execute(select_bound)

                # partly STOP
                probe.partly_stop()

            # partly FINISH - check time for performance test END
            if probe.partly_finish():
                break
    finally:
        if session:
            session.shutdown()
        if cql:
            cql.close()

    return probe

def prf_read(run_setup: RunSetup) -> ParallelProbe:
    numeric_scope = run_setup['numeric_scope']
    generator = get_rng_generator()
    columns, items="", ""
    cql = None
    session = None

    if run_setup.is_init:
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

        select_statement = session.prepare(f"SELECT {columns[:-1]} FROM {run_setup['keyspace']}.{Setting.TABLE_NAME} "
                                           f"WHERE fn0 IN ({items[:-1]}) and fn1 IN ({items[:-1]});")
        bound = BoundStatement(select_statement, consistency_level=run_setup['consistency_level'])

        while 1:

            # generate synthetic data
            #  NOTE: It will generate only values for two columns (as primary keys), not for all columns
            synthetic_data = generator.integers(numeric_scope, size=run_setup.bulk_row*2)

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
    numeric_scope = run_setup['numeric_scope']
    generator = get_rng_generator()
    columns, items = "", ""
    cql = None
    session = None

    if run_setup.is_init:
        # create schema for write data
        try:
            cql = CQLAccess(run_setup)
            cql.open()
            cql.create_model()
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
        insert_statement = session.prepare(f"INSERT INTO {run_setup['keyspace']}.{Setting.TABLE_NAME} ({columns[:-1]}) "
                                           f"VALUES ({items[:-1]});")
        batch = BatchStatement(consistency_level=run_setup['consistency_level'])

        while 1:
            batch.clear()

            # generate synthetic data
            synthetic_data = generator.integers(numeric_scope, size=(run_setup.bulk_row, run_setup.bulk_col))

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

def cluster_diagnose(run_setup, level):

    cql = None
    try:
        level = CQLDiagnosePrint[level.lower()]
        if level == CQLDiagnosePrint.off:
            return

        cql = CQLAccess(run_setup)
        cql.open()
        status = CQLHealth(cql.cluster)
        status.diagnose(level)
    finally:
        if cql:
            cql.close()

def generate_graphs(generator: ParallelExecutor, generate_graph_scope, output_dir):
    """Generate graph based on setting"""

    graph_scope = GraphScope[generate_graph_scope.lower()]
    if GraphScope.off not in graph_scope:
        print(f"Generate graph(s): '{generate_graph_scope}'...")
        generator.create_graph(output_dir,
                               scope = graph_scope,
                               suppress_error = True,
                               only_new=True)           # generate only new files (not regenerate all)

def perf_test(unique_id, global_param, parameters: dict):

    lbl = parameters['adapter']#.name
    lbl_suffix = f"{parameters['label']}" if parameters.get('label', None) else ""

    generator = None
    if parameters['test_type']=='w':    # WRITE perf test
        generator = ParallelExecutor(prf_write,
                                     label=f"{lbl}{unique_id}-W{lbl_suffix}",
                                     detail_output=global_param['detail_output'],
                                     output_file=path.join(global_param['perf_dir'], "..", "output", f"prf_{lbl.lower()}-W{lbl_suffix.lower()}-{datetime.date.today()}.txt"),
                                     init_each_bulk=True)
    elif parameters['test_type']=='r':  # READ perf test
        generator = ParallelExecutor(prf_read,
                                     label=f"{lbl}{unique_id}-R{lbl_suffix}",
                                     detail_output=global_param['detail_output'],
                                     output_file=path.join(global_param['perf_dir'], "..", "output", f"prf_{lbl.lower()}-R{lbl_suffix.lower()}-{datetime.date.today()}.txt"),
                                     init_each_bulk=True)
    elif parameters['test_type']=='rw' or parameters['test_type']=='wr':    # READ & WRITE perf test
        generator = ParallelExecutor(prf_readwrite,
                                     label=f"{lbl}{unique_id}-RW{lbl_suffix}",
                                     detail_output=global_param['detail_output'],
                                     output_file=path.join(global_param['perf_dir'], "..", "output", f"prf_{lbl.lower()}-RW{lbl_suffix.lower()}-{datetime.date.today()}.txt"),
                                     init_each_bulk=True)

    # define setup
    setup = RunSetup(duration_second = global_param['executor_duration'],
                     start_delay = global_param['executor_start_delay'],
                     parameters = parameters)

    # run diagnose
    cluster_diagnose(setup, global_param['cluster_diagnose'])
    if global_param['cluster_diagnose_only']:
        return

    # performance execution
    generator.run_bulk_executor(parameters['bulk_list'],
                                global_param['executors'],
                                run_setup = setup)

    # generate graphs
    generate_graphs(generator,
                    global_param['generate_graph'],
                    path.join(global_param['perf_dir'], "..", "output"))

def main_execute(multi_env="cass.env", perf_dir = ".", only_cluster_diagnose = False, level = "short"):

    global_param = CQLConfig(perf_dir).get_global_params(multi_env, only_cluster_diagnose, level)
    if global_param:
        env_count = 0
        unique_id = "-" + datetime.datetime.now().strftime("%H%M%S")
        envs = [env.strip() for env in global_param['multiple_env'].split(",")]
        for env in envs:
            if not env.lower().endswith(".env"):
                env += ".env"
            env_count += 1
            print(Fore.LIGHTGREEN_EX + f"Environment switch {env_count}/{len(envs)}: '{env}' ..." + Style.RESET_ALL)

            # delay before other processing
            if not only_cluster_diagnose:
                if env_count > 1 :
                    time.sleep(global_param['multiple_env_delay'])

            perf_test(unique_id,
                      global_param,
                      CQLConfig(perf_dir).get_params(env, global_param))
    else:
        print("!!! Missing 'MULTIPLE_ENV' configuration !!!")

def test_cluster(env, perf_dir):

    global_param = CQLConfig(perf_dir).get_global_params(env)
    if global_param:
        env_count = 0
        multi_env = [env.strip() for env in global_param['multiple_env'].split(",")]
        for single_env in multi_env:
            if not single_env.lower().endswith(".env"):
                single_env += ".env"
            env_count += 1
            print(Fore.LIGHTGREEN_EX + f"Environment switch {env_count}/{len(multi_env)}: '{single_env}' ..." + Style.RESET_ALL)

            setup = RunSetup(parameters=CQLConfig(perf_dir).get_params(single_env, global_param))
            session = None
            cql = None

            try:
                # Cluster connection
                cql = CQLAccess(setup)
                cql.open()
                session = cql.create_session()
                rows = session.execute("SELECT cluster_name, cql_version, data_center, rack, release_version FROM system.local;")
                for row in rows:
                    print("  ", row)
            except Exception as ex:
                print(Fore.LIGHTRED_EX, "Exception: ", str(ex), Style.RESET_ALL)
            finally:
                if session:
                    session.shutdown()
                if cql:
                    cql.close()

@click.group()
def graph_group():
    pass

@graph_group.command()
@click.option("-s", "--scope", help="scope of generation, can be 'Perf' (as default), 'Exe' or 'All'", default="perf")
@click.option("-d", "--perf_dir", help="directory with perf_cql (default '.')", default=".")
@click.option("-i", "--input_files", help="filter for performance files in '--perf_dir' (default 'prf_*.txt')", default="prf_*.txt")
def graph(scope, perf_dir, input_files):
    """Generate graphs based on performance file(s)."""
    for file in glob(path.join(perf_dir, "..", "output", input_files)):
        print(file)
        for output in ParallelExecutor.create_graph_static(file,
                                                           path.join(perf_dir, "..", "output"),
                                                           GraphScope[scope.lower()],
                                                           suppress_error=True,
                                                           only_new=False):
            print(" ", output)

@click.group()
def test_group():
    pass

@test_group.command()
@click.option("-e", "--env", help="name of ENV file (default 'cass.env')", default="cass.env")
@click.option("-d", "--perf_dir", help="directory with perf_cql (default '.')", default=".")
def test(env, perf_dir):
    """Test connection to Cluster and access to a few system tables"""
    test_cluster(env, perf_dir)

@click.group()
def version_group():
    pass

@version_group.command()
def version():
    """Versions of key components."""
    from qgate_perf import __version__ as perf_version
    from qgate_graph import __version__ as graph_version
    from numpy import __version__ as numpy_version
    from cassandra import __version__ as cassandra_version
    from matplotlib import __version__ as matplotlibe_version
    from prettytable import PrettyTable
    from colorama import Fore, Style
    import version
    import sys

    table = PrettyTable()
    table.border = True
    table.header = True
    table.padding_width = 1
    table.max_table_width = 75

    table.field_names = ["Component", "Version"]
    table.align = "l"

    table.add_row([Fore.LIGHTRED_EX + "perf_cql"+ Style.RESET_ALL, Fore.LIGHTRED_EX + version.__version__+Style.RESET_ALL])
    table.add_row(["qgate_perf", perf_version])
    table.add_row(["qgate_graph", graph_version])
    table.add_row(["numpy", numpy_version])
    table.add_row(["cassandra-driver", cassandra_version])
    table.add_row(["matplotlib", matplotlibe_version])
    table.add_row(["python", sys.version])
    print(table)

@click.group()
def diagnose_group():
    pass

@diagnose_group.command()
@click.option("-e", "--env", help="name of ENV file (default 'cass.env')", default="cass.env")
@click.option("-d", "--perf_dir", help="directory with perf_cql (default '.')", default=".")
@click.option("-l", "--level", help="level of diagnose, acceptable values 'short', 'full', 'extra' (default 'short')", default="short")
def diagnose(env, perf_dir, level):
    """Diagnostic for cluster based on ENV file(s)."""
    main_execute(env, perf_dir, True, level)

@click.group()
def run_group():
    pass

@run_group.command()
@click.option("-e", "--env", help="name of ENV file (default 'cass.env')", default="cass.env")
@click.option("-d", "--perf_dir", help="directory with perf_cql (default '.')", default=".")
def run(env, perf_dir):
    """Run performance tests based on ENV file(s)."""
    main_execute(env, perf_dir)

cli = click.CommandCollection(sources=[run_group, diagnose_group, graph_group, version_group, test_group])

if __name__ == '__main__':
    cli()
