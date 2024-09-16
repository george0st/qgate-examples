# Knowledge base for CQL solutions

## Well known issues

 - **WARNING**: cassandra.connection:An authentication challenge was not sent, this is suspicious because the driver expects authentication (configured authenticator = PlainTextAuthenticator)
   - **Info**: Only info about low security access 
   - **Solution**: It is possible to change setting on Cassandra server side in cassandra.yaml
   

 - **ReadTimeout**: Error from server: code=1200 [Coordinator node timed out waiting for replica nodes' responses]
   - **Info**: Long execution time on server side is needed, typically complex CQL which expected more execution time or network issue between nodes
   - **Solution**: 
     - Change CQL or tune schema (tune where conditions, add indexes, etc.)
     - or focus on network quality


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
   - **Info**: Issue with CRC validation (it has relation to consistency).
     I got the issue with _ProtocolVersion.V5_ under _Cassandra 5.0.0_
   - **Solution**: Use lower and more stable protocol version e.g. _ProtocolVersion.V4_
