from cassandra.cluster import Cluster

class CQLStatus:

    def __init__(self, cluster: Cluster):
        self._cluster = cluster
        self._nodes = None
        self._hosts = None

    def diagnose(self):

        status = self.get_status()

        # print output Up/Down, Synch/Unsynch nodes (based on the root node)

    def get_status(self):
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
                    'schema_version': state["schema_version"],
                    'release_version': node["release_version"],
                    'root': state['root'] if state else False,
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
                'root': False,
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
            'root': True,
        }
        nodes[local_node_info['rpc_address']] = local_node_info
        return nodes
