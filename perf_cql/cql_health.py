from cassandra.cluster import Cluster
from prettytable import PrettyTable
from colorama import Fore, Style
from enum import Enum
from cql_helper import generate_id, get_rng_generator, bool2str


class CQLDiagnosePrint(Enum):
    off = 1
    short = 2
    full = 3
    extra = 4

class CQLHealth:

    def __init__(self, cluster: Cluster):
        self._cluster = cluster
        self._nodes = None
        self._hosts = None

    def diagnose(self, level = CQLDiagnosePrint.short) -> dict:
        status=self._get_status()

        if level==CQLDiagnosePrint.short:
            self.print_status_short(status)
        elif level==CQLDiagnosePrint.full:
            self.print_status_full(status)
        elif level==CQLDiagnosePrint.extra:
            self.print_status_short(status)
            self.print_status_full(status)
        return status

    def get_version(self):
        """Return runtime version (4.0, 5.0.0, etc.) for platform such as Cassandra, Scylla, etc."""

        session = None
        try:
            session = self._cluster.connect()
            session.default_timeout = 20

            row = session.execute("SELECT release_version FROM system.local;").one()
            return str(row.release_version) if row else ""
        finally:
            if session:
                session.shutdown()

    def get_size(self, keyspace_name) -> int:
        """Return size of keyspace in Mb. The error indicate value -1."""

        session = None
        try:
            session = self._cluster.connect()
            session.default_timeout = 20

            row = session.execute("SELECT SUM(mean_partition_size * partitions_count) / 1048576 AS size_mb "
                                   "FROM system.size_estimates "
                                   f"WHERE keyspace_name = '{keyspace_name}' "
                                   "GROUP BY keyspace_name;").one()
            return int(row.size_mb) if row else -1

        finally:
            if session:
                session.shutdown()

    #region DIAGNOSE private functions

    def print_status_short(self, status, prefix_output = " "):

        node_down = []
        node_unclear = []
        node_peer_down = []
        schemas = {}
        root_schema = None
        release_versions = {}

        for ip in status.keys():
            node = status[ip]

            # info from metadata
            if node['status'] == "DOWN":
                node_down.append(ip)
            elif node['status'] == "?":
                node_unclear.append(ip)

            # info from system.peers
            if node['peer_status'] == "DOWN":
                node_peer_down.append(ip)

            # schema of local/root node
            if node['root'] == "x":
                root_schema=node['schema_version']

            # count of different schemas
            if schemas.get(node['schema_version'], None):
                schemas[node['schema_version']] += 1
            else:
                schemas[node['schema_version']] = 1

            # count of different release version
            if release_versions.get(node['release_version'], None):
                release_versions[node['release_version']] += 1
            else:
                release_versions[node['release_version']] = 1

        missing_schemas = len(status)-schemas.get(root_schema,0)
        release_versions = str([key for key in release_versions.keys()])
        down_info = unclear_info = node_info = ""
        if len(node_down) > 0:
            node_info = f"{len(node_down)}x Down{'' if len(node_down)==0 else ' '+ Fore.LIGHTRED_EX + str(node_down)+Style.RESET_ALL}"
        if len(node_unclear) > 0:
            if len(node_info) > 0:
                node_info+=", "
            node_info += f"{len(node_unclear)}x ?{'' if len(node_unclear)==0 else ' '+ Fore.CYAN + str(node_unclear)+Style.RESET_ALL}"
        if len(node_info)>0:
            node_info = f"({node_info})"
        print(f"{prefix_output}Nodes: {len(status)}x {node_info},"
              f" Gossip: {'0x' if len(node_peer_down) == 0 else Fore.CYAN + str(len(node_peer_down)) + 'x' + Style.RESET_ALL}"
              f"{'' if len(node_peer_down) == 0 else ' ' + Fore.CYAN + str(node_peer_down) + Style.RESET_ALL},"             
              f" Not-synch: {'0x' if missing_schemas == 0 else Fore.CYAN + str(missing_schemas) + 'x' + Style.RESET_ALL},"
              f" Ver: {release_versions}")

    def print_status_full(self, status):
        table = PrettyTable()

        table.border = False
        table.header = True
        table.padding_width = 1

        table.field_names = ["State", "Gossip", "IP", "Location", "Ver", "Synch", "Root"]
        table.align = "l"
        table.align["Root"] = "c"

        # use short schema version
        shorter_schema = self._build_shorter_schema_version(status)

        # create output
        for ip in status.keys():
            node = status[ip]
            color_prefix = ""
            color_peer_prefix = ""
            color_status_prefix = ""
            color_status_suffix = ""
            color_suffix = ""
            color_peer_suffix = ""

            if node['root'] == "x":
                color_prefix = Fore.CYAN
                color_suffix = Style.RESET_ALL

            if node['status'] == "DOWN":
                color_status_prefix = Fore.LIGHTRED_EX
                color_status_suffix = Style.RESET_ALL
            elif node['status'] == "?":
                color_status_prefix = Fore.CYAN
                color_status_suffix = Style.RESET_ALL

            if node['peer_status'] == "DOWN":
                color_peer_prefix = Fore.CYAN
                color_peer_suffix = Style.RESET_ALL

            row = [f"{color_status_prefix}{node['status']}{color_status_suffix}",
                   f"{color_peer_prefix}{node['peer_status']}{color_peer_suffix}",
                   f"{ip}",
                   node['location'],
                   f"{node['release_version']}",
                   f"{color_prefix}{shorter_schema[node['schema_version']]}{color_suffix}",
                   f"{color_prefix}{node['root']}{color_suffix}"]
            table.add_row(row)
        table.sortby = "Location"
        print(table)

    def _build_shorter_schema_version(self, status):
        """Generate shorter schema version for better visualization
        (in terminal 80 columns and 40 rows)"""

        generator = get_rng_generator(False)
        short_schema = {}

        for ip in status.keys():
            node = status[ip]
            if node.get('schema_version', None):
                if not node['schema_version'] == 'n/a':
                    if not short_schema.get(node['schema_version'], None):
                        short_schema[node['schema_version']] = generate_id(5, generator)
                    continue
            short_schema[node['schema_version']] = "n/a"
        return short_schema

    def _get_status(self) -> dict:
        final_status = {}
        session = None

        try:
            session = self._cluster.connect()
            session.default_timeout = 20

            nodes = self._get_nodes(session)
            node_status = self._get_node_status(session)

            for key in nodes.keys():
                node = nodes[key]
                state = node_status.get(key, None)

                final_status_info = {
                    'status': bool2str(node['is_up'], "UP", "DOWN", "?"),
                    'peer_status': state['status'] if state else "DOWN",
                    'location': f"{node['data_center']}/{node['rack']}",
                    'schema_version': state["schema_version"] if state else "n/a",
                    'release_version': node["release_version"],
                    'root': state['root'] if state else "",
                }
                final_status[key] = final_status_info

        finally:
            if session:
                session.shutdown()
        return final_status

    def _get_nodes(self, session) -> dict:
        """Return all nodes in cluster"""
        metadata = self._cluster.metadata
        hosts = {}

        for host in metadata.all_hosts():
            host_info = {
                'address': host.address,
                'data_center':host.datacenter,
                'rack': host.rack,
                'release_version': host.release_version,
                'is_up': host.is_up,
            }
            hosts[host.address]=host_info
        return hosts

    def _get_node_status(self, session) -> dict:
        """Return states of all live nodes"""
        nodes = {}

        # Execute a query to get node status information from system.peers
        query = "SELECT peer, schema_version, release_version, rpc_address FROM system.peers;"
        rows = session.execute(query)

        # Process the results
        for row in rows:
            node_info = {
                'status': 'UP' if row.rpc_address else 'DOWN',
                #'status': 'UP' if row.peer else 'DOWN',
                'schema_version': row.schema_version,
                'release_version': row.release_version,
                'peer': row.peer,
                'rpc_address': row.rpc_address,
                'root': "",
            }
            nodes[node_info['peer']]=node_info

        # Include the local node information
        local_query = "SELECT schema_version, rpc_address, release_version FROM system.local;"
        local_row = session.execute(local_query).one()
        local_node_info = {
            'status': 'UP' if local_row.rpc_address else 'DOWN',
            'schema_version': local_row.schema_version,
            'release_version' : local_row.release_version,
            'peer': '127.0.0.1',  # Local node IP
            'rpc_address': local_row.rpc_address,
            'root': "x",
        }
        nodes[local_node_info['rpc_address']] = local_node_info
        return nodes

    #endregion