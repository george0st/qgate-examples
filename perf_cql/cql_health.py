from cassandra.cluster import Cluster
from prettytable import PrettyTable
from colorama import Fore, Style


class CQLHealth:

    def __init__(self, cluster: Cluster):
        self._cluster = cluster
        self._nodes = None
        self._hosts = None

    def diagnose(self, print = False, full_detail = False) -> dict:
        status=self._get_status()

        if print:
            if full_detail:
                self._print_status_full(status)
            else:
                self._print_status_short(status)
        return status

    def get_version(self):
        """Return Cassandra, Scylla, etc. runtime version e.g. 5.0.0 such as Cassandra v 5.0.0, etc."""

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
        """Return size of keyspace"""

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


        #   SELECT keyspace_name,
        #        SUM(mean_partition_size * partitions_count) / 1048576 AS total_size_mb
        # FROM system.size_estimates
        # WHERE keyspace_name = 'jist'
        # GROUP BY keyspace_name;



    #region DIAGNOSE private functions

    def _print_status_short(self, status, prefix_output ="  Cluster check>> "):

        node_down = []
        schemas = {}
        root_schema = None

        for ip in status.keys():
            node = status[ip]
            if node['status'] == "DOWN":
                node_down.append(ip)
            if node['root'] == "x":
                root_schema=node['schema_version']
            if schemas.get(node['schema_version'],None):
                schemas[node['schema_version']] += 1
            else:
                schemas[node['schema_version']] = 1

        missing_schemas=len(status)-schemas.get(root_schema,0)
        down_info=f"({len(node_down)}x Down{'' if len(node_down)==0 else ' '+Fore.RED+str(node_down)+Style.RESET_ALL})"
        print(f"{prefix_output}Nodes: {len(status)}x [Total] {down_info}, Synch: {'0x' if missing_schemas==0 else Fore.BLUE+str(missing_schemas)+'x'+Style.RESET_ALL} [Missing]")

    def _print_status_full(self, status):
        table = PrettyTable()

        table.border = False
        table.header = True
        table.padding_width = 1

        table.field_names = ["State", "IP", "Location", "Ver", "Synch", "Root"]
        table.align = "l"
        table.align["Root"] = "c"

        for ip in status.keys():
            node = status[ip]
            color_prefix = ""
            color_suffix = ""

            if node['root'] == "x":
                color_prefix = Fore.BLUE
                color_suffix = Style.RESET_ALL

            if node['status'] == "DOWN":
                color_prefix = Fore.RED
                color_suffix = Style.RESET_ALL

            row = [f"{color_prefix}{node['status']}{color_suffix}",
                   f"{color_prefix}{ip}{color_suffix}",
                   node['location'],
                   f"{color_prefix}{node['release_version']}{color_suffix}",
                   f"{color_prefix}{node['schema_version']}{color_suffix}",
                   f"{color_prefix}{node['root']}{color_suffix}"]
            table.add_row(row)
        table.sortby = "Location"
        print(table)

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
                    'status': state['status'] if state else "DOWN",
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
        query = "SELECT peer, schema_version, rpc_address FROM system.peers"
        rows = session.execute(query)

        # Process the results
        for row in rows:
            node_info = {
                'status': 'UP' if row.rpc_address else 'DOWN',
                'schema_version': row.schema_version,
                'peer': row.peer,
                'rpc_address': row.rpc_address,
                'root': "",
            }
            nodes[node_info['peer']]=node_info

        # Include the local node information
        local_query = "SELECT schema_version, rpc_address FROM system.local"
        local_row = session.execute(local_query).one()
        local_node_info = {
            'status': 'UP' if local_row.rpc_address else 'DOWN',
            'schema_version': local_row.schema_version,
            'peer': '127.0.0.1',  # Local node IP
            'rpc_address': local_row.rpc_address,
            'root': "x",
        }
        nodes[local_node_info['rpc_address']] = local_node_info
        return nodes

    #endregion