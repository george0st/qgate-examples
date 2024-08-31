import cassandra.policies
from qgate_perf.run_setup import RunSetup

from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from cassandra.cluster import ExecutionProfile
from cassandra.cluster import EXEC_PROFILE_DEFAULT
from cassandra import ProtocolVersion
from cassandra.policies import DCAwareRoundRobinPolicy, RoundRobinPolicy, DefaultLoadBalancingPolicy
from cql_config import CQLType


class Setting:
    TABLE_NAME = "t01"
    MAX_GNR_VALUE = 99999
    TIMEOUT = 30
    TIMEOUT_CREATE_MODEL = 180

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
        auth_provider = None

        # authentication provider
        if self._run_setup['username']:
            auth_provider = PlainTextAuthProvider(username=self._run_setup["username"],
                                                 password=self._read_file(self._run_setup["password"]))

        # load balancing policy
        if int(self._run_setup['replication_factor'])==1:
            load_balancing_policy=RoundRobinPolicy()
        else:
            load_balancing_policy = DCAwareRoundRobinPolicy(local_dc = self._run_setup["local_dc"])

        if self._run_setup["secure_connect_bundle"]:
            # connection with 'secure_connect_bundle' to the cloud
            cloud_config = {
                "secure_connect_bundle": self._run_setup["secure_connect_bundle"],
                'use_default_tempdir': True
            }
            self._cluster = Cluster(cloud = cloud_config,
                                    auth_provider = auth_provider,
                                    load_balancing_policy = load_balancing_policy,
                                    control_connection_timeout = Setting.TIMEOUT,
                                    idle_heartbeat_interval = Setting.TIMEOUT,
                                    connect_timeout = Setting.TIMEOUT,
                                    protocol_version = ProtocolVersion.V4)
        else:
            # connection with 'ip' and 'port'
            self._cluster = Cluster(contact_points = self._run_setup['ip'],
                                    port = self._run_setup['port'],
                                    auth_provider = auth_provider,
                                    load_balancing_policy = load_balancing_policy,
                                    control_connection_timeout = Setting.TIMEOUT,
                                    idle_heartbeat_interval = Setting.TIMEOUT,
                                    connect_timeout = Setting.TIMEOUT,
                                    protocol_version = ProtocolVersion.V4)

        self._session = self._cluster.connect()
        self._session.default_timeout = Setting.TIMEOUT

    def create_model(self):

        self._session.default_timeout = Setting.TIMEOUT_CREATE_MODEL
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
        columns = ""
        for i in range(0, self._run_setup.bulk_col):
            columns += f"fn{i} int,"

        # complex primary key (partition key 'fn0' and cluster key 'fn1')
        self._session.execute(
            f"CREATE TABLE IF NOT EXISTS {self._run_setup['keyspace']}.{Setting.TABLE_NAME} ({columns[:-1]}, PRIMARY KEY (fn0, fn1))")

    def close(self):
        if self._cluster:
            self._cluster.shutdown()
            self._cluster = None


    def _read_file(self, file) -> str:
        with open(file) as f:
            return f.readline()