# Knowledge base for issues

## Well known issues

 - **WARNING**: cassandra.connection:An authentication challenge was not sent, this is suspicious because the driver expects authentication (configured authenticator = PlainTextAuthenticator)
   - **Info**: Only info about low security access 
   - **Solution**: It is possible to change setting on Cassandra server side in cassandra.yaml
   

 - **ReadTimeout**: Error from server: code=1200 [Coordinator node timed out waiting for replica nodes' responses]
   - **Info**: Long execution time on server side is needed, typically complex CQL which expected more execution time or network issue between nodes
   - **Solution**: 
     - Change CQL or tune schema (tune where conditions, add indexes, etc.) 
     or focus on network quality


 - **OperationTimedOut**: errors={<Host: 10.117.19.5:9042 datacenter2>: ConnectionShutdown('Connection to 10.117.19.5:9042 was closed')}, last_host=10.117.19.6:9042
   - **Info**: Connection issue e.g. with VPN, Wifi, etc. 


 - **OperationTimedOut**: errors={'10.129.53.154:9042': 'Client request timeout. See Session.execute[_async](timeout)'}, last_host=10.129.53.154:9042
   - TBD.


 - **Unavailable**: Error from server: code=1000 [Unavailable exception] message=\"Cannot achieve consistency level ONE\" info={'consistency': 'ONE', 'required_replicas': 1, 'alive_replicas': 0}
   - **Info**: Issue with cluster consistency

    
 - **NoHostAvailable**: ('Unable to complete the operation against any hosts', {<Host: 10.117.19.5:9042 datacenter2>: ConnectionException('Host has been marked down or removed')})
   - **Info**: Issue with cluster consistency


 - **NoHostAvailable**: ('Unable to connect to any servers', {'10.129.53.159:9042': ConnectionShutdown('CRC mismatch on header 22f840. Received 85\", computed e3d12c.')})
 - **NoHostAvailable**: ('Unable to connect to any servers', {'10.129.53.159:9042': ConnectionShutdown('CRC mismatch on header 718a02. Received 85a8\", computed a7811f.')})
   - **Info**: I got the issue during heavy performance tests. It is issue with CRC validation
     (it has relation to consistency). I got the issue with _ProtocolVersion.V5_ under _Cassandra 5.0.0_
   - **Solution**: Use lower and more stable protocol version e.g. _ProtocolVersion.V4_


 - **InvalidRequest**: Error from server: code=2200 [Invalid query] message=\"unconfigured table t01\"
   - **Info**: It was not possible to build expected table
   - **Solution**: Please, check compaction level, typical issue is that Cassandra support **UnifiedCompactionStrategy** 
     but ScyllaDB not and from these reasons, you have to modify single ENV file 
     with compaction setting


 - **AuthenticationFailed**('Failed to authenticate to 10.117.19.6:9042: Error from server: code=0100 [Bad credentials] message="Unable to perform authentication: Cannot achieve consistency level QUORUM"')
   - **Info**: the connection is using CL QUORUM
   - **Solution**: Use different account than 'cassandra', this account has setting to CL QUORUM.
     see full clarification https://docs.datastax.com/en/archived/datastax_enterprise/4.8/datastax_enterprise/sec/secConfiguringInternalAuthentication.html
     see citation 
     - Logins for the cassandra user are performed with QUORUM consistency. 
     - Do not use the default cassandra user in production, because QUORUM consistency has significant performance degradation for multiple data centers. 
     - Logins for all other users are performed with LOCAL_ONE consistency.


 - **NoHostAvailable**: ('Unable to connect to any servers', {'10.129.53.159:9042': ConnectionRefusedError(10061, "Tried connecting to [('10.129.53.159', 9042)]. Last error: No connection could be made because the target machine actively refused it")})
   - **Info**: The node '10.129.53.159:9042' is not available and you did not define other nodes for connection
   - **Solution**: Add to the connection:
     - more nodes 
     - define retry policy for optimal error handling
