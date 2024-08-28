from qgate_perf.run_setup import RunSetup

from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from cassandra.cluster import ExecutionProfile
from cassandra.cluster import EXEC_PROFILE_DEFAULT

from cql_type import CQLType

class Setting:
    TABLE_NAME = "t02"
    MAX_GNR_VALUE = 999999


class CQLAccess:

    def __init__(self):
        pass

    def create_cluster(self, run_setup: RunSetup):
        """Create cluster for connection"""
        authProvider = None

        # connection setting
        if run_setup['username']:
            authProvider = PlainTextAuthProvider(username=run_setup["username"],
                                                 password=self._read_file(run_setup["password"]))

        if run_setup["secure_connect_bundle"]:
            # connection with 'secure_connect_bundle' to the cloud
            cloud_config = {
                "secure_connect_bundle": run_setup["secure_connect_bundle"],
                'use_default_tempdir': True
            }
            cluster = Cluster(cloud=cloud_config,
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

    def prepare_model(self, cluster, run_setup: RunSetup):

        try:
            session = cluster.connect()
            columns = ""

            if run_setup["cql"] != CQLType.AstraDB:

                if run_setup['replication_factor']:
                    # Drop key space
                    session.execute(f"DROP KEYSPACE IF EXISTS {run_setup['keyspace']}")

                    # Create key space
                    session.execute(f"CREATE KEYSPACE IF NOT EXISTS {run_setup['keyspace']}" +
                                    " WITH replication = {" +
                                    f"'class':'{run_setup['replication_class']}', 'replication_factor' : {run_setup['replication_factor']}" +
                                    "};")

            # use LTW atomic command with IF
            session.execute(f"DROP TABLE IF EXISTS {run_setup['keyspace']}.{Setting.TABLE_NAME}")

            # prepare insert statement for batch
            for i in range(0, run_setup.bulk_col):
                columns += f"fn{i} int,"

            # complex primary key (partition key 'fn0' and cluster key 'fn1')
            session.execute(
                f"CREATE TABLE IF NOT EXISTS {run_setup['keyspace']}.{Setting.TABLE_NAME} ({columns[:-1]}, PRIMARY KEY (fn0, fn1))")

        finally:
            if cluster:
                cluster.shutdown()

    def _read_file(self, file) -> str:
        with open(file) as f:
            return f.readline()