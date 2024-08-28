from qgate_perf.run_setup import RunSetup

from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from cassandra.cluster import ExecutionProfile
from cassandra.cluster import EXEC_PROFILE_DEFAULT

from cql_config import CQLType


class Setting:
    TABLE_NAME = "t02"
    MAX_GNR_VALUE = 999999

class CQLAccess:

    def __init__(self, run_setup: RunSetup):
        self._run_setup = run_setup
        self._cluster = None
        self._session = None

    @property
    def cluster(self):
        return self._cluster

    @property
    def session(self):
        return self._session

    def open(self):
        """Create cluster for connection"""
        authProvider = None

        # connection setting
        if self._run_setup['username']:
            authProvider = PlainTextAuthProvider(username=self._run_setup["username"],
                                                 password=self._read_file(self._run_setup["password"]))

        if self._run_setup["secure_connect_bundle"]:
            # connection with 'secure_connect_bundle' to the cloud
            cloud_config = {
                "secure_connect_bundle": self._run_setup["secure_connect_bundle"],
                'use_default_tempdir': True
            }
            self._cluster = Cluster(cloud=cloud_config,
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
            self._cluster = Cluster(contact_points=self._run_setup['ip'],
                              port=self._run_setup['port'],
                              auth_provider=authProvider,
                              execution_profiles={EXEC_PROFILE_DEFAULT: ExecutionProfile(request_timeout=30)},
                              control_connection_timeout=30,
                              idle_heartbeat_interval=30,
                              connect_timeout=30)

        self._session = self._cluster.connect()

    def create_model(self):

        try:
            #session = self._cluster.connect()
            columns = ""

            if self._run_setup["cql"] != CQLType.AstraDB:

                if self._run_setup['replication_factor']:
                    # Drop key space
                    self._session.execute(f"DROP KEYSPACE IF EXISTS {self._run_setup['keyspace']}")

                    # Create key space
                    self._session.execute(f"CREATE KEYSPACE IF NOT EXISTS {self._run_setup['keyspace']}" +
                                    " WITH replication = {" +
                                    f"'class':'{self._run_setup['replication_class']}', 'replication_factor' : {self._run_setup['replication_factor']}" +
                                    "};")

            # use LTW atomic command with IF
            self._session.execute(f"DROP TABLE IF EXISTS {self._run_setup['keyspace']}.{Setting.TABLE_NAME}")

            # prepare insert statement for batch
            for i in range(0, self._run_setup.bulk_col):
                columns += f"fn{i} int,"

            # complex primary key (partition key 'fn0' and cluster key 'fn1')
            self._session.execute(
                f"CREATE TABLE IF NOT EXISTS {self._run_setup['keyspace']}.{Setting.TABLE_NAME} ({columns[:-1]}, PRIMARY KEY (fn0, fn1))")

        finally:
            self.close()
            # if self._cluster:
            #     self._cluster.shutdown()

    def close(self):
        if self._cluster:
            self._cluster.shutdown()

    def _read_file(self, file) -> str:
        with open(file) as f:
            return f.readline()