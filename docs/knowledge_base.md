# Knowledge base for CQL solutions

## Well known issues

 - **WARNING**: cassandra.connection:An authentication challenge was not sent, this is suspicious because the driver expects authentication (configured authenticator = PlainTextAuthenticator)
   - **Info**: Only info about low security access 
   - **Solution**: It is possible to change setting on Cassandra server side in cassandra.yaml
   

 - **ReadTimeout**: Error from server: code=1200 [Coordinator node timed out waiting for replica nodes' responses]
   - **Info**: Long execution time is needed, typically complex CQL which expected more execution time
   - **Solution**: Change CQL or tune schema (tune where conditions, add indexes, etc.)


 - **OperationTimedOut**: errors={<Host: 10.117.19.5:9042 datacenter2>: ConnectionShutdown('Connection to 10.117.19.5:9042 was closed')}, last_host=10.117.19.6:9042
   - **Info**: Connection issue e.g. with VPN, Wifi, etc.


 - **OperationTimedOut**: errors={'10.129.53.154:9042': 'Client request timeout. See Session.execute[_async](timeout)'}, last_host=10.129.53.154:9042
   - TBD.